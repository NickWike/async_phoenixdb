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
from typing import Dict, List
from .common_pb import ConnectionProperties
from .common_pb import StatementHandle
from .common_pb import TypedValue
from .common_pb import QueryState


class CatalogsRequest(betterproto.Message):
    """Request for Meta#getCatalogs()"""

    connection_id: str


class DatabasePropertyRequest(betterproto.Message):
    """Request for Meta#getDatabaseProperties()"""

    connection_id: str


class SchemasRequest(betterproto.Message):
    """
    Request for Meta#getSchemas(String, org.apache.calcite.avatica.Meta.Pat)}
    """

    catalog: str
    schema_pattern: str
    connection_id: str
    has_catalog: bool
    has_schema_pattern: bool


class TablesRequest(betterproto.Message):
    """
    Request for Request for Meta#getTables(String,
    org.apache.calcite.avatica.Meta.Pat,   org.apache.calcite.avatica.Meta.Pat,
    java.util.List)
    """

    catalog: str
    schema_pattern: str
    table_name_pattern: str
    type_list: List[str]
    has_type_list: bool
    connection_id: str
    has_catalog: bool
    has_schema_pattern: bool
    has_table_name_pattern: bool


class TableTypesRequest(betterproto.Message):
    """Request for Meta#getTableTypes()"""

    connection_id: str


class ColumnsRequest(betterproto.Message):
    """
    Request for Meta#getColumns(String, org.apache.calcite.avatica.Meta.Pat,
    org.apache.calcite.avatica.Meta.Pat, org.apache.calcite.avatica.Meta.Pat).
    """

    catalog: str
    schema_pattern: str
    table_name_pattern: str
    column_name_pattern: str
    connection_id: str
    has_catalog: bool
    has_schema_pattern: bool
    has_table_name_pattern: bool
    has_column_name_pattern: bool


class TypeInfoRequest(betterproto.Message):
    """Request for Meta#getTypeInfo()"""

    connection_id: str


class PrepareAndExecuteRequest(betterproto.Message):
    """
    Request for Meta#prepareAndExecute(Meta.StatementHandle, String, long,
    Meta.PrepareCallback)
    """

    connection_id: str
    sql: str
    max_row_count: int
    statement_id: int
    max_rows_total: int
    first_frame_max_size: int


class PrepareRequest(betterproto.Message):
    """Request for Meta.prepare(Meta.ConnectionHandle, String, long)"""

    connection_id: str
    sql: str
    max_row_count: int
    max_rows_total: int


class FetchRequest(betterproto.Message):
    """Request for Meta#fetch(Meta.StatementHandle, List, long, int)"""

    connection_id: str
    statement_id: int
    offset: int
    fetch_max_row_count: int
    frame_max_size: int


class CreateStatementRequest(betterproto.Message):
    """Request for Meta#createStatement(Meta.ConnectionHandle)"""

    connection_id: str


class CloseStatementRequest(betterproto.Message):
    """Request for Meta#closeStatement(Meta.StatementHandle)"""

    connection_id: str
    statement_id: int


class OpenConnectionRequest(betterproto.Message):
    """
    Request for Meta#openConnection(Meta.ConnectionHandle, Map<String, String>)
    """

    connection_id: str
    info: Dict[str, str] = betterproto.map_field(
        2, betterproto.TYPE_STRING, betterproto.TYPE_STRING
    )


class CloseConnectionRequest(betterproto.Message):
    """Request for Meta#closeConnection(Meta.ConnectionHandle)"""

    connection_id: str


class ConnectionSyncRequest(betterproto.Message):
    connection_id: str
    conn_props: "ConnectionProperties"


class ExecuteRequest(betterproto.Message):
    """Request for Meta#execute(Meta.ConnectionHandle, list, long)"""

    statement_handle: "StatementHandle"
    parameter_values: List["TypedValue"]
    deprecated_first_frame_max_size: int
    has_parameter_values: bool
    first_frame_max_size: int


class SyncResultsRequest(betterproto.Message):
    connection_id: str
    statement_id: int
    state: "QueryState"
    offset: int


class CommitRequest(betterproto.Message):
    """Request to invoke a commit on a Connection"""

    connection_id: str


class RollbackRequest(betterproto.Message):
    """Request to invoke rollback on a Connection"""

    connection_id: str


class PrepareAndExecuteBatchRequest(betterproto.Message):
    """Request to prepare and execute a collection of sql statements."""

    connection_id: str
    statement_id: int
    sql_commands: List[str]


class UpdateBatch(betterproto.Message):
    """Each command is a list of TypedValues"""

    parameter_values: List["TypedValue"]


class ExecuteBatchRequest(betterproto.Message):
    connection_id: str
    statement_id: int
    updates: List["UpdateBatch"]
