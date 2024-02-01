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

import logging
from typing import Any, List

from aiophoenixdb.connection import Connection
from aiophoenixdb.avatica.proto.common_pb import MetaDataOperationArgument, ColumnMetaData

__all__ = ['Meta']

logger: logging.Logger


class Meta(object):
    """Database meta for querying MetaData
    """

    _connection: Connection

    def __init__(self, connection: Connection): ...

    def get_catalogs(self) -> Any: ...

    def get_schemas(self, catalog=None, schema_pattern=None) -> Any: ...

    def get_tables(self, catalog=None, schema_pattern=None, table_name_pattern=None, type_list=None) -> Any: ...

    def get_columns(self, catalog=None, schema_pattern=None, table_name_pattern=None, column_name_pattern=None) -> Any: ...

    def get_table_types(self) -> Any: ...

    def get_type_info(self) -> Any: ...

    async def get_primary_keys(self, catalog=None, schema=None, table=None) -> List[Any]: ...

    async def get_index_info(self, catalog=None, schema=None, table=None, unique=False, approximate=False) -> List[Any]: ...

    @staticmethod
    def _column_meta_data_factory(ordinal: int, column_name: str, jdbc_code: int) -> ColumnMetaData: ...

    @staticmethod
    def _moa_string_arg_factory(arg: str) -> MetaDataOperationArgument: ...

    @staticmethod
    def _moa_bool_arg_factory(arg: bool) -> MetaDataOperationArgument: ...

    @staticmethod
    def _fix_default(rows: List[Any], catalog=None, schema_pattern=None) -> Any: ...
