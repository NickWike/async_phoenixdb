# Copyright 2024 Nick Hao
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import aiohttp
import betterproto
from html.parser import HTMLParser
from typing import TypeVar, Type, List, Dict, Any, Optional
from urllib.parse import ParseResult
from aiohttp import ClientResponse, BasicAuth
from aiophoenixdb import errors
from aiophoenixdb.typeshed import Self
from .proto.common_pb import Frame
from .proto.common_pb import StatementHandle
from .proto.common_pb import ConnectionProperties
from .proto.responses_pb import ResultSetResponse
from .proto.responses_pb import SyncResultsResponse
from .proto.responses_pb import OpenConnectionResponse
from .proto.responses_pb import CloseConnectionResponse
from .proto.responses_pb import CloseStatementResponse
from .proto.responses_pb import CommitResponse
from .proto.responses_pb import RollbackResponse


class JettyErrorPageParser(HTMLParser):
    path: List[Any]
    title: List[Any]
    message: List[Any]

    def handle_starttag(self, tag, attrs) -> None: ...

    def handle_endtag(self, tag) -> None: ...

    def handle_data(self, data) -> None: ...


def parse_url(url) -> ParseResult:...


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

def raise_sql_error(code, sqlstate, message) -> None: ...


def parse_and_raise_sql_error(message: str) -> None: ...


def parse_error_page(html: str) -> None: ...


def parse_error_protobuf(text: bytes) -> None: ...


_MESSAGE_TYPE = TypeVar("_MESSAGE_TYPE", bound=betterproto.Message)


class AvaticaClient(object):
    _url: str
    _headers = {'content-type': 'application/x-google-protobuf'}
    _verify: Any
    _max_retries: int
    _session: aiohttp.ClientSession

    def __init__(self, url: str, max_retries: int, verify, extra_headers: Dict, auth: Optional[BasicAuth]): ...

    async def __post_request(self, body: bytes, retry_delay: int = 1) -> ClientResponse: ...

    async def _request(self, request_data: betterproto.Message,
                       expected_response_cls: Type[_MESSAGE_TYPE] | None = None) -> _MESSAGE_TYPE: ...

    async def get_catalogs(self, connection_id: str) -> ResultSetResponse: ...

    async def get_schemas(self, connection_id: str,
                          catalog: str | None = None,
                          schema_pattern: str | None = None) -> ResultSetResponse: ...

    async def get_tables(self, connection_id, catalog=None,
                         schema_pattern=None,
                         table_name_pattern=None,
                         type_list: List[str] = None) -> ResultSetResponse: ...

    async def get_columns(self, connection_id,
                          catalog=None, schema_pattern=None,
                          table_name_pattern=None,
                          column_name_pattern=None) -> ResultSetResponse: ...

    async def get_table_types(self, connection_id) -> ResultSetResponse: ...

    async def get_type_info(self, connection_id) -> ResultSetResponse: ...

    async def get_sync_results(self, connection_id, statement_id, state) -> SyncResultsResponse: ...

    async def connection_sync_dict(self, connection_id, conn_props: Dict[str, Any] = None) -> Dict[str, Any]: ...

    async def connection_sync(self, connection_id, conn_props: Dict[str, Any] = None) -> ConnectionProperties: ...

    async def open_connection(self, connection_id, info=None) -> OpenConnectionResponse: ...

    async def close_connection(self, connection_id) -> CloseConnectionResponse: ...

    async def create_statement(self, connection_id) -> int: ...

    async def close_statement(self, connection_id, statement_id) -> CloseStatementResponse: ...

    async def prepare_and_execute(self, connection_id, statement_id, sql, max_rows_total=None,
                                  first_frame_max_size=None) -> List[ResultSetResponse]: ...

    async def prepare(self, connection_id, sql, max_rows_total=None) -> StatementHandle: ...

    async def execute(self, connection_id,
                      statement_id,
                      signature,
                      parameter_values=None,
                      first_frame_max_size=None) -> List[ResultSetResponse]: ...

    async def execute_batch(self, connection_id, statement_id, rows) -> List[int]: ...

    async def fetch(self, connection_id, statement_id, offset=0, frame_max_size=None) -> Frame: ...

    async def commit(self, connection_id) -> CommitResponse: ...

    async def rollback(self, connection_id) -> RollbackResponse: ...

    async def close(self) -> None: ...

    async def __aenter__(self: Self) -> Self: ...

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None: ...