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

import betterproto
from typing import List
from .common_pb import Signature
from .common_pb import Frame
from .common_pb import StatementHandle
from .common_pb import Severity
from .common_pb import DatabaseProperty
from .common_pb import TypedValue
from .common_pb import ConnectionProperties


class ResultSetResponse(betterproto.Message):
    """Response that contains a result set."""

    connection_id: str
    statement_id: int
    own_statement: bool
    signature: "Signature"
    first_frame: "Frame"
    update_count: int
    # with no signature nor other data.
    metadata: "RpcMetadata"


class ExecuteResponse(betterproto.Message):
    """Response to PrepareAndExecuteRequest"""

    results: List["ResultSetResponse"]
    missing_statement: bool
    metadata: "RpcMetadata"


class PrepareResponse(betterproto.Message):
    """Response to PrepareRequest"""

    statement: "StatementHandle"
    metadata: "RpcMetadata"


class FetchResponse(betterproto.Message):
    """Response to FetchRequest"""

    frame: "Frame"
    missing_statement: bool
    missing_results: bool
    metadata: "RpcMetadata"


class CreateStatementResponse(betterproto.Message):
    """Response to CreateStatementRequest"""

    connection_id: str
    statement_id: int
    metadata: "RpcMetadata"


class CloseStatementResponse(betterproto.Message):
    """Response to CloseStatementRequest"""

    metadata: "RpcMetadata"


class OpenConnectionResponse(betterproto.Message):
    """Response to OpenConnectionRequest {"""

    metadata: "RpcMetadata"


class CloseConnectionResponse(betterproto.Message):
    """Response to CloseConnectionRequest {"""

    metadata: "RpcMetadata"


class ConnectionSyncResponse(betterproto.Message):
    """Response to ConnectionSyncRequest"""

    conn_props: "ConnectionProperties"
    metadata: "RpcMetadata"


class DatabasePropertyElement(betterproto.Message):
    key: "DatabaseProperty"
    value: "TypedValue"
    metadata: "RpcMetadata"


class DatabasePropertyResponse(betterproto.Message):
    """Response for Meta#getDatabaseProperties()"""

    props: List["DatabasePropertyElement"]
    metadata: "RpcMetadata"


class ErrorResponse(betterproto.Message):
    """
    Send contextual information about some error over the wire from the server.
    """

    exceptions: List[str]
    has_exceptions: bool
    error_message: str
    severity: "Severity"
    error_code: int
    sql_state: str
    metadata: "RpcMetadata"


class SyncResultsResponse(betterproto.Message):
    missing_statement: bool
    more_results: bool
    metadata: "RpcMetadata"


class RpcMetadata(betterproto.Message):
    """Generic metadata for the server to return with each response."""

    server_address: str


class CommitResponse(betterproto.Message):
    """Response to a commit request"""

    pass


class RollbackResponse(betterproto.Message):
    """Response to a rollback request"""
    pass


class ExecuteBatchResponse(betterproto.Message):
    """Response to a batch update request"""

    connection_id: str
    statement_id: int
    update_counts: List[int]
    missing_statement: bool
    metadata: "RpcMetadata"
