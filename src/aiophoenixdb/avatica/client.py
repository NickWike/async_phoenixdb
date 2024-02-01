import re
import asyncio
import aiohttp
import urllib.parse as urlparse
import betterproto
from aiophoenixdb import errors
from aiophoenixdb.avatica.proto import common_pb, requests_pb, responses_pb
from html.parser import HTMLParser
from aiohttp import BasicAuth, ClientError
from typing import Optional, Dict, TypeVar

_RESPONSE_MSG_JAVA_CLS_NAME = "org.apache.calcite.avatica.proto.Responses${cls_name}"
_REQUEST_MSG_JAVA_CLS_NAME = "org.apache.calcite.avatica.proto.Requests${cls_name}"


class JettyErrorPageParser(HTMLParser):

    def __init__(self):
        HTMLParser.__init__(self)
        self.path = []
        self.title = []
        self.message = []

    def handle_starttag(self, tag, attrs):
        self.path.append(tag)

    def handle_endtag(self, tag):
        self.path.pop()

    def handle_data(self, data):
        if len(self.path) > 2 and self.path[0] == 'html' and self.path[1] == 'body':
            if len(self.path) == 3 and self.path[2] == 'h2':
                self.title.append(data.strip())
            elif len(self.path) == 4 and self.path[2] == 'p' and self.path[3] == 'pre':
                self.message.append(data.strip())


def parse_url(url):
    url = urlparse.urlparse(url)
    if not url.scheme and not url.netloc and url.path:
        netloc = url.path
        if ':' not in netloc:
            netloc = '{}:8765'.format(netloc)

        return urlparse.ParseResult('http', netloc, '/', '', '', '')
    return url


# Defined in phoenix-core/src/main/java/org/apache/phoenix/exception/SQLExceptionCode.java
SQLSTATE_ERROR_CLASSES = [
    ('08', errors.OperationalError),  # Connection Exception
    ('22018', errors.IntegrityError),  # Constraint violatioin.
    ('22', errors.DataError),  # Data Exception
    ('23', errors.IntegrityError),  # Constraint Violation
    ('24', errors.InternalError),  # Invalid Cursor State
    ('25', errors.InternalError),  # Invalid Transaction State
    ('42', errors.ProgrammingError),  # Syntax Error or Access Rule Violation
    ('XLC', errors.OperationalError),  # Execution exceptions
    ('INT', errors.InternalError),  # Phoenix internal error
]


def raise_sql_error(code, sqlstate, message):
    for prefix, error_class in SQLSTATE_ERROR_CLASSES:
        if sqlstate.startswith(prefix):
            raise error_class(message, code, sqlstate)
    raise errors.InternalError(message, code, sqlstate)


def parse_and_raise_sql_error(message):
    match = re.findall(r'(?:([^ ]+): )?ERROR (\d+) \(([0-9A-Z]{5})\): (.*?) ->', message)
    if match is not None and len(match):
        exception, code, sqlstate, message = match[0]
        raise_sql_error(int(code), sqlstate, message)


def parse_error_page(html):
    parser = JettyErrorPageParser()
    parser.feed(html)
    if parser.title == ['HTTP ERROR: 500']:
        message = ' '.join(parser.message).strip()
        parse_and_raise_sql_error(message)
        raise errors.InternalError(message)


def parse_error_protobuf(text):
    try:
        message = common_pb.WireMessage()
        message.parse(text)

        err = responses_pb.ErrorResponse()
        if not err.parse(message.wrapped_message):
            raise Exception('No error message found')
    except Exception:
        # Not a protobuf error, fall through
        return

    parse_and_raise_sql_error(err.error_message)
    raise_sql_error(err.error_code, err.sql_state, err.error_message)
    # Not a protobuf error, fall through


_MESSAGE_TYPE = TypeVar("_MESSAGE_TYPE", bound=betterproto.Message)


class AvaticaClient(object):

    def __init__(self, url: str, max_retries: int, verify, extra_headers: Dict, auth: Optional[BasicAuth]):
        self._url = url
        self._headers = {'content-type': 'application/x-google-protobuf'}
        self._verify = verify
        self._max_retries = max_retries or 3
        if extra_headers:
            self._headers.update(extra_headers)

        self._session = aiohttp.ClientSession(
            headers=self._headers,
            auth=auth
        )

    async def __post_request(self, body, retry_delay=1):
        for _ in range(self._max_retries):
            request_args = {'data': body}
            if self._verify is not None:
                request_args.update(verify=self._verify)
            try:
                response = await self._session.post(self._url, **request_args)
            except ClientError:
                await asyncio.sleep(retry_delay)
            else:
                if response.status != 503:
                    return response
                else:
                    await asyncio.sleep(retry_delay)
        else:
            raise errors.MasRetriesError("Request retry more than the maximum number of attempts")

    async def _request(self, request_data,
                       expected_response_cls=None):
        request_name = request_data.__class__.__name__
        message = common_pb.WireMessage()
        message.name = _REQUEST_MSG_JAVA_CLS_NAME.format(cls_name=request_name)
        message.wrapped_message = request_data.SerializeToString()
        request_body = message.SerializeToString()

        response = await self.__post_request(request_body)
        response_body = await response.read()

        if response.status != 200:
            # logger.debug("Received response\n%s", response_body)
            if b'<html>' in response_body:
                parse_error_page(response_body.decode(response.get_encoding()))
            else:
                # assume the response is in protobuf format
                parse_error_protobuf(response_body)
            raise errors.InterfaceError('RPC request returned invalid status code', response.status)

        message = common_pb.WireMessage()
        message.parse(response_body)

        # logger.debug("Received response\n%s", message)

        if expected_response_cls is None:
            expected_response_type = request_name.replace('Request', 'Response')
        else:
            expected_response_type = expected_response_cls.__name__

        expected_response_type = _RESPONSE_MSG_JAVA_CLS_NAME.format(cls_name=expected_response_type)
        if message.name != expected_response_type:
            raise errors.InterfaceError(
                'unexpected response type "{}" expected "{}"'.format(message.name, expected_response_type))
        res: _MESSAGE_TYPE = expected_response_cls()
        res.parse(message.wrapped_message)
        return res

    async def get_catalogs(self, connection_id):
        request = requests_pb.CatalogsRequest()
        request.connection_id = connection_id
        response = await self._request(request, responses_pb.ResultSetResponse)
        return response

    async def get_schemas(self, connection_id,
                          catalog=None,
                          schema_pattern=None):
        request = requests_pb.SchemasRequest()
        request.connection_id = connection_id
        if catalog is not None:
            request.catalog = catalog
        if schema_pattern is not None:
            request.schema_pattern = schema_pattern
        response = await self._request(request, responses_pb.ResultSetResponse)
        return response

    async def get_tables(self, connection_id, catalog=None,
                         schema_pattern=None,
                         table_name_pattern=None,
                         type_list=None):
        request = requests_pb.TablesRequest()
        request.connection_id = connection_id
        if catalog is not None:
            request.catalog = catalog
        if schema_pattern is not None:
            request.schema_pattern = schema_pattern
        if table_name_pattern is not None:
            request.table_name_pattern = table_name_pattern
        if type_list is not None:
            request.type_list.extend(type_list)
        request.has_type_list = type_list is not None
        response = await self._request(request, responses_pb.ResultSetResponse)
        return response

    async def get_columns(self, connection_id,
                          catalog=None, schema_pattern=None,
                          table_name_pattern=None,
                          column_name_pattern=None):
        request = requests_pb.ColumnsRequest()
        request.connection_id = connection_id
        if catalog is not None:
            request.catalog = catalog
        if schema_pattern is not None:
            request.schema_pattern = schema_pattern
        if table_name_pattern is not None:
            request.table_name_pattern = table_name_pattern
        if column_name_pattern is not None:
            request.column_name_pattern = column_name_pattern
        response = await self._request(request, responses_pb.ResultSetResponse)
        return response

    async def get_table_types(self, connection_id):
        request = requests_pb.TableTypesRequest()
        request.connection_id = connection_id
        response = await self._request(request, responses_pb.ResultSetResponse)
        return response

    async def get_type_info(self, connection_id):
        request = requests_pb.TypeInfoRequest()
        request.connection_id = connection_id
        response = await self._request(request, responses_pb.ResultSetResponse)
        return response

    async def get_sync_results(self, connection_id, statement_id, state):
        request = requests_pb.SyncResultsRequest()
        request.connection_id = connection_id
        request.statement_id = statement_id
        # todo copyFrom
        request.state.parse(state)
        response = await self._request(request, responses_pb.SyncResultsResponse)
        return response

    async def connection_sync_dict(self, connection_id, conn_props=None):
        conn_props = await self.connection_sync(connection_id, conn_props)
        return {
            'autoCommit': conn_props.auto_commit,
            'readOnly': conn_props.read_only,
            'transactionIsolation': conn_props.transaction_isolation,
            'catalog': conn_props.catalog,
            'schema': conn_props.schema}

    async def connection_sync(self, connection_id, conn_props=None):
        """Synchronizes connection properties with the server.

        :param connection_id:
            ID of the current connection.

        :param conn_props:
            Dictionary with the properties that should be changed.

        :returns:
            A ``common_pb2.ConnectionProperties`` object.
        """
        if conn_props:
            props = conn_props.copy()
        else:
            props = {}

        request = requests_pb.ConnectionSyncRequest()
        request.connection_id = connection_id
        request.conn_props.has_auto_commit = True
        request.conn_props.has_read_only = True
        if 'autoCommit' in props:
            request.conn_props.auto_commit = props.pop('autoCommit')
        if 'readOnly' in props:
            request.conn_props.read_only = props.pop('readOnly')
        if 'transactionIsolation' in props:
            request.conn_props.transaction_isolation = props.pop('transactionIsolation', None)
        if 'catalog' in props:
            request.conn_props.catalog = props.pop('catalog', None)
        if 'schema' in props:
            request.conn_props.schema = props.pop('schema', None)

        # if props:
        #     logger.warning("Unhandled connection property:" + props)

        # response_data = await self._apply(request)
        # response = ConnectionSyncResponse()
        # response.parse(response_data)

        response = await self._request(request, responses_pb.ConnectionSyncResponse)
        return response.conn_props

    async def open_connection(self, connection_id, info=None):
        """Opens a new connection.

        :param info:
        :param connection_id:
            ID of the connection to open.
        """
        request = requests_pb.OpenConnectionRequest()
        request.connection_id = connection_id
        if info is not None:
            # Info is a list of repeated pairs, setting a dict directly fails
            for k, v in info.items():
                request.info[k] = v

        # response_data = await self._apply(request)
        # response = responses_pb.OpenConnectionResponse()
        # response.parse(response_data)
        return await self._request(request, responses_pb.OpenConnectionResponse)

    async def close_connection(self, connection_id):
        """Closes a connection.

        :param connection_id:
            ID of the connection to close.
        """
        request = requests_pb.CloseConnectionRequest()
        request.connection_id = connection_id
        return await self._request(request, responses_pb.CloseConnectionResponse)

    async def create_statement(self, connection_id):
        """Creates a new statement.

        :param connection_id:
            ID of the current connection.

        :returns:
            New statement ID.
        """
        request = requests_pb.CreateStatementRequest()
        request.connection_id = connection_id

        response = await self._request(request, responses_pb.CreateStatementResponse)
        return response.statement_id

    async def close_statement(self, connection_id, statement_id):
        """Closes a statement.

        :param connection_id:
            ID of the current connection.

        :param statement_id:
            ID of the statement to close.
        """
        request = requests_pb.CloseStatementRequest()
        request.connection_id = connection_id
        request.statement_id = statement_id

        return await self._request(request, responses_pb.CloseStatementResponse)

    async def prepare_and_execute(self, connection_id, statement_id, sql, max_rows_total=None,
                                  first_frame_max_size=None):
        """Prepares and immediately executes a statement.

        :param connection_id:
            ID of the current connection.

        :param statement_id:
            ID of the statement to prepare.

        :param sql:
            SQL query.

        :param max_rows_total:
            The maximum number of rows that will be allowed for this query.

        :param first_frame_max_size:
            The maximum number of rows that will be returned in the first Frame returned for this query.

        :returns:
            Result set with the signature of the prepared statement and the first frame data.
        """
        request = requests_pb.PrepareAndExecuteRequest()
        request.connection_id = connection_id
        request.statement_id = statement_id
        request.sql = sql
        if max_rows_total is not None:
            request.max_rows_total = max_rows_total
        if first_frame_max_size is not None:
            request.first_frame_max_size = first_frame_max_size
        # 提交request, 发起请求
        response = await self._request(request, responses_pb.ExecuteResponse)
        return response.results

    async def prepare(self, connection_id, sql, max_rows_total=None):
        """Prepares a statement.

        :param connection_id:
            ID of the current connection.

        :param sql:
            SQL query.

        :param max_rows_total:
            The maximum number of rows that will be allowed for this query.

        :returns:
            Signature of the prepared statement.
        """
        request = requests_pb.PrepareRequest()
        request.connection_id = connection_id
        request.sql = sql
        if max_rows_total is not None:
            request.max_rows_total = max_rows_total

        response = await self._request(request, responses_pb.PrepareResponse)
        return response.statement

    async def execute(self, connection_id,
                      statement_id,
                      signature,
                      parameter_values=None,
                      first_frame_max_size=None):
        """Returns a frame of rows.

        The frame describes whether there may be another frame. If there is not
        another frame, the current iteration is done when we have finished the
        rows in this frame.

        :param connection_id:
            ID of the current connection.

        :param statement_id:
            ID of the statement to fetch rows from.

        :param signature:
            common_pb2.Signature object

        :param parameter_values:
            A list of parameter values, if statement is to be executed; otherwise ``None``.

        :param first_frame_max_size:
            The maximum number of rows that will be returned in the first Frame returned for this query.

        :returns:
            Frame data, or ``None`` if there are no more.
        """
        request = requests_pb.ExecuteRequest()
        request.statement_handle.id = statement_id
        request.statement_handle.connection_id = connection_id
        # todo copy from
        request.statement_handle.signature = signature
        if parameter_values is not None:
            request.parameter_values.extend(parameter_values)
            request.has_parameter_values = True
        if first_frame_max_size is not None:
            request.deprecated_first_frame_max_size = first_frame_max_size
            request.first_frame_max_size = first_frame_max_size

        response = await self._request(request, responses_pb.ExecuteResponse)
        return response.results

    async def execute_batch(self, connection_id, statement_id, rows):
        """Returns an array of update counts corresponding to each row written.

        :param connection_id:
            ID of the current connection.

        :param statement_id:
            ID of the statement to fetch rows from.

        :param rows:
            A list of lists corresponding to the columns to bind to the statement
            for many rows.

        :returns:
            Update counts for the writes.
        """
        request = requests_pb.ExecuteBatchRequest()
        request.statement_id = statement_id
        request.connection_id = connection_id
        if rows is not None:
            for row in rows:
                batch = requests_pb.UpdateBatch()
                for col in row:
                    batch.parameter_values.append(col)
                request.updates.append(batch)

        response = await self._request(request, responses_pb.ExecuteBatchResponse)
        if response.missing_statement:
            raise errors.DatabaseError('ExecuteBatch reported missing statement', -1)
        return response.update_counts

    async def fetch(self, connection_id, statement_id, offset=0, frame_max_size=None):
        """Returns a frame of rows.

        The frame describes whether there may be another frame. If there is not
        another frame, the current iteration is done when we have finished the
        rows in this frame.

        :param connection_id:
            ID of the current connection.

        :param statement_id:
            ID of the statement to fetch rows from.

        :param offset:
            Zero-based offset of first row in the requested frame.

        :param frame_max_size:
            Maximum number of rows to return; negative means no limit.

        :returns:
            Frame data, or ``None`` if there are no more.
        """
        request = requests_pb.FetchRequest()
        request.connection_id = connection_id
        request.statement_id = statement_id
        request.offset = offset
        if frame_max_size is not None:
            request.frame_max_size = frame_max_size

        response = await self._request(request, responses_pb.FetchResponse)
        return response.frame

    async def commit(self, connection_id):
        """TODO Commits the transaction

        :param connection_id:
            ID of the current connection.
        """
        request = requests_pb.CommitRequest()
        request.connection_id = connection_id
        return await self._request(request)

    async def rollback(self, connection_id):
        """TODO Rolls back the transaction

        :param connection_id:
            ID of the current connection.
        """
        request = requests_pb.RollbackRequest()
        request.connection_id = connection_id
        return await self._request(request)

    async def close(self):
        await self._session.close()

    def __enter__(self):
        raise TypeError("Use async with instead")

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass


if __name__ == '__main__':
    pass
