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

from typing import List
import betterproto


class StatementType(betterproto.Enum):
    """Has to be consistent with Meta.StatementType"""

    SELECT: int
    INSERT: int
    UPDATE: int
    DELETE: int
    UPSERT: int
    MERGE: int
    OTHER_DML: int
    CREATE: int
    DROP: int
    ALTER: int
    OTHER_DDL: int
    CALL: int


class Rep(betterproto.Enum):
    PRIMITIVE_BOOLEAN: int
    PRIMITIVE_BYTE: int
    PRIMITIVE_CHAR: int
    PRIMITIVE_SHORT: int
    PRIMITIVE_INT: int
    PRIMITIVE_LONG: int
    PRIMITIVE_FLOAT: int
    PRIMITIVE_DOUBLE: int
    BOOLEAN: int
    BYTE: int
    CHARACTER: int
    SHORT: int
    INTEGER: int
    LONG: int
    FLOAT: int
    DOUBLE: int
    BIG_INTEGER: int
    BIG_DECIMAL: int
    JAVA_SQL_TIME: int
    JAVA_SQL_TIMESTAMP: int
    JAVA_SQL_DATE: int
    JAVA_UTIL_DATE: int
    BYTE_STRING: int
    STRING: int
    NUMBER: int
    OBJECT: int
    NULL: int
    ARRAY: int
    STRUCT: int
    MULTISET: int


class Severity(betterproto.Enum):
    """
    The severity of some unexpected outcome to an operation. Protobuf enum
    values must be unique across all other enums
    """

    UNKNOWN_SEVERITY: int
    FATAL_SEVERITY: int
    ERROR_SEVERITY: int
    WARNING_SEVERITY: int


class MetaDataOperation(betterproto.Enum):
    """Enumeration corresponding to DatabaseMetaData operations"""

    GET_ATTRIBUTES: int
    GET_BEST_ROW_IDENTIFIER: int
    GET_CATALOGS: int
    GET_CLIENT_INFO_PROPERTIES: int
    GET_COLUMN_PRIVILEGES: int
    GET_COLUMNS: int
    GET_CROSS_REFERENCE: int
    GET_EXPORTED_KEYS: int
    GET_FUNCTION_COLUMNS: int
    GET_FUNCTIONS: int
    GET_IMPORTED_KEYS: int
    GET_INDEX_INFO: int
    GET_PRIMARY_KEYS: int
    GET_PROCEDURE_COLUMNS: int
    GET_PROCEDURES: int
    GET_PSEUDO_COLUMNS: int
    GET_SCHEMAS: int
    GET_SCHEMAS_WITH_ARGS: int
    GET_SUPER_TABLES: int
    GET_SUPER_TYPES: int
    GET_TABLE_PRIVILEGES: int
    GET_TABLES: int
    GET_TABLE_TYPES: int
    GET_TYPE_INFO: int
    GET_UDTS: int
    GET_VERSION_COLUMNS: int


class StateType(betterproto.Enum):
    SQL: int
    METADATA: int


class CursorFactoryStyle(betterproto.Enum):
    OBJECT: int
    RECORD: int
    RECORD_PROJECTION: int
    ARRAY: int
    LIST: int
    MAP: int


class MetaDataOperationArgumentArgumentType(betterproto.Enum):
    STRING: int
    BOOL: int
    INT: int
    REPEATED_STRING: int
    REPEATED_INT: int
    NULL: int


class ConnectionProperties(betterproto.Message):
    """Details about a connection"""

    is_dirty: bool
    auto_commit: bool
    has_auto_commit: bool
    read_only: bool
    has_read_only: bool
    transaction_isolation: int
    catalog: str
    schema: str


class StatementHandle(betterproto.Message):
    """Statement handle"""

    connection_id: str
    id: int
    signature: "Signature"


class Signature(betterproto.Message):
    """Results of preparing a statement"""

    columns: List["ColumnMetaData"]
    sql: str
    parameters: List["AvaticaParameter"]
    cursor_factory: "CursorFactory"
    statement_type: "StatementType"


class ColumnMetaData(betterproto.Message):
    ordinal: int
    auto_increment: bool
    case_sensitive: bool
    searchable: bool
    currency: bool
    nullable: int
    signed: bool
    display_size: int
    label: str
    column_name: str
    schema_name: str
    precision: int
    scale: int
    table_name: str
    catalog_name: str
    read_only: bool
    writable: bool
    definitely_writable: bool
    column_class_name: str
    type: "AvaticaType"


class AvaticaType(betterproto.Message):
    """Base class for a column type"""

    id: int
    name: str
    rep: "Rep"
    columns: List["ColumnMetaData"]
    component: "AvaticaType"


class AvaticaParameter(betterproto.Message):
    """Metadata for a parameter"""

    signed: bool
    precision: int
    scale: int
    parameter_type: int
    type_name: str
    class_name: str
    name: str


class CursorFactory(betterproto.Message):
    """Information necessary to convert an Iterable into a Calcite Cursor"""

    style: "CursorFactoryStyle"
    class_name: str
    field_names: List[str]


class Frame(betterproto.Message):
    """A collection of rows"""

    offset: int
    done: bool
    rows: List["Row"]


class Row(betterproto.Message):
    """A row is a collection of values"""

    value: List["ColumnValue"]


class DatabaseProperty(betterproto.Message):
    """
    Database property, list of functions the database provides for a certain
    operation
    """

    name: str
    functions: List[str]


class WireMessage(betterproto.Message):
    """
    Message which encapsulates another message to support a single RPC endpoint
    """

    name: str
    wrapped_message: bytes


class ColumnValue(betterproto.Message):
    """A value might be a TypedValue or an Array of TypedValue's"""

    value: List["TypedValue"]
    array_value: List["TypedValue"]
    has_array_value: bool
    scalar_value: "TypedValue"


class TypedValue(betterproto.Message):
    """
    Generic wrapper to support any SQL type. Struct-like to work around no
    polymorphism construct.
    """

    type: "Rep"
    bool_value: bool
    string_value: str
    number_value: int
    # includes numeric types and date/time types.
    bytes_value: bytes
    double_value: float
    null: bool
    array_value: List["TypedValue"]
    component_type: "Rep"
    implicitly_null: bool


class MetaDataOperationArgument(betterproto.Message):
    """Represents the breadth of arguments to DatabaseMetaData functions"""

    string_value: str
    bool_value: bool
    int_value: int
    string_array_values: List[str]
    int_array_values: List[int]
    type: "MetaDataOperationArgumentArgumentType"


class QueryState(betterproto.Message):
    type: "StateType"
    sql: str
    op: "MetaDataOperation"
    args: List["MetaDataOperationArgument"]
    has_args: bool
    has_sql: bool
    has_op: bool
