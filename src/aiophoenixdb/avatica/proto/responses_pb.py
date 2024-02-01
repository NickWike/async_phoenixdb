# Generated by the protocol buffer compiler.  DO NOT EDIT!
# sources: responses.proto
# plugin: python-betterproto
from .common_pb import *
from typing import List
import betterproto


@dataclass
class ResultSetResponse(betterproto.Message):
    """Response that contains a result set."""

    connection_id: str = betterproto.string_field(1)
    statement_id: int = betterproto.uint32_field(2)
    own_statement: bool = betterproto.bool_field(3)
    signature: "Signature" = betterproto.message_field(4)
    first_frame: "Frame" = betterproto.message_field(5)
    update_count: int = betterproto.uint64_field(6)
    # with no signature nor other data.
    metadata: "RpcMetadata" = betterproto.message_field(7)


@dataclass
class ExecuteResponse(betterproto.Message):
    """Response to PrepareAndExecuteRequest"""

    results: List["ResultSetResponse"] = betterproto.message_field(1)
    missing_statement: bool = betterproto.bool_field(2)
    metadata: "RpcMetadata" = betterproto.message_field(3)


@dataclass
class PrepareResponse(betterproto.Message):
    """Response to PrepareRequest"""

    statement: "StatementHandle" = betterproto.message_field(1)
    metadata: "RpcMetadata" = betterproto.message_field(2)


@dataclass
class FetchResponse(betterproto.Message):
    """Response to FetchRequest"""

    frame: "Frame" = betterproto.message_field(1)
    missing_statement: bool = betterproto.bool_field(2)
    missing_results: bool = betterproto.bool_field(3)
    metadata: "RpcMetadata" = betterproto.message_field(4)


@dataclass
class CreateStatementResponse(betterproto.Message):
    """Response to CreateStatementRequest"""

    connection_id: str = betterproto.string_field(1)
    statement_id: int = betterproto.uint32_field(2)
    metadata: "RpcMetadata" = betterproto.message_field(3)


@dataclass
class CloseStatementResponse(betterproto.Message):
    """Response to CloseStatementRequest"""

    metadata: "RpcMetadata" = betterproto.message_field(1)


@dataclass
class OpenConnectionResponse(betterproto.Message):
    """Response to OpenConnectionRequest {"""

    metadata: "RpcMetadata" = betterproto.message_field(1)


@dataclass
class CloseConnectionResponse(betterproto.Message):
    """Response to CloseConnectionRequest {"""

    metadata: "RpcMetadata" = betterproto.message_field(1)


@dataclass
class ConnectionSyncResponse(betterproto.Message):
    """Response to ConnectionSyncRequest"""

    conn_props: "ConnectionProperties" = betterproto.message_field(1)
    metadata: "RpcMetadata" = betterproto.message_field(2)


@dataclass
class DatabasePropertyElement(betterproto.Message):
    key: "DatabaseProperty" = betterproto.message_field(1)
    value: "TypedValue" = betterproto.message_field(2)
    metadata: "RpcMetadata" = betterproto.message_field(3)


@dataclass
class DatabasePropertyResponse(betterproto.Message):
    """Response for Meta#getDatabaseProperties()"""

    props: List["DatabasePropertyElement"] = betterproto.message_field(1)
    metadata: "RpcMetadata" = betterproto.message_field(2)


@dataclass
class ErrorResponse(betterproto.Message):
    """
    Send contextual information about some error over the wire from the server.
    """

    exceptions: List[str] = betterproto.string_field(1)
    has_exceptions: bool = betterproto.bool_field(7)
    error_message: str = betterproto.string_field(2)
    severity: "Severity" = betterproto.enum_field(3)
    error_code: int = betterproto.uint32_field(4)
    sql_state: str = betterproto.string_field(5)
    metadata: "RpcMetadata" = betterproto.message_field(6)


@dataclass
class SyncResultsResponse(betterproto.Message):
    missing_statement: bool = betterproto.bool_field(1)
    more_results: bool = betterproto.bool_field(2)
    metadata: "RpcMetadata" = betterproto.message_field(3)


@dataclass
class RpcMetadata(betterproto.Message):
    """Generic metadata for the server to return with each response."""

    server_address: str = betterproto.string_field(1)


@dataclass
class CommitResponse(betterproto.Message):
    """Response to a commit request"""

    pass


@dataclass
class RollbackResponse(betterproto.Message):
    """Response to a rollback request"""

    pass


@dataclass
class ExecuteBatchResponse(betterproto.Message):
    """Response to a batch update request"""

    connection_id: str = betterproto.string_field(1)
    statement_id: int = betterproto.uint32_field(2)
    update_counts: List[int] = betterproto.uint64_field(3)
    missing_statement: bool = betterproto.bool_field(4)
    metadata: "RpcMetadata" = betterproto.message_field(5)
