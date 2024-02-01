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
from _weakref import ReferenceType
from typing import Any, List, Generator, Dict, TypeVar, Callable
from aiophoenixdb.typeshed import Self
from aiophoenixdb.avatica.proto.common_pb import ColumnMetaData, Signature, Frame, Row
from aiophoenixdb.avatica.proto.responses_pb import ResultSetResponse, SyncResultsResponse
from aiophoenixdb.connection import Connection

_C = TypeVar("_C", bound="Cursor")

class CursorRef:

    _ref: ReferenceType

    def __init__(self, o: _C, callback: Callable[[CursorRef], _C] | None = ...): ...

    def __call__(self, *args, **kwargs) -> _C: ...

class Cursor(object):
    _ARRAY_SIZE: int
    _ITER_SIZE: int
    _connection: Connection
    _id: int
    _signature: Any
    _column_data_types: List
    _frame: Frame | None
    _pos: int
    _closed: bool
    _array_size: int
    _iter_size: int
    _update_count: int
    _parameter_data_types: List[Any]



    def __init__(self, connection: Connection, _id: int = None): ...
    async def __aenter__(self: Self) -> Self: ...
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None: ...
    def __iter__(self: Self): Self
    async def __anext__(self) -> Generator[List[List[Any], Any]]: ...

    async def close(self) -> None: ...
    @property
    def closed(self) -> bool: ...

    @property
    def description(self) -> List[Any]: ...

    @staticmethod
    def _get_column_name(column: ColumnMetaData) -> str: ...

    async def _set_id(self, _id) -> None: ...

    def _set_signature(self, signature: Signature) -> None: ...
    def _set_frame(self, frame: Frame | None) -> None: ...

    async def _fetch_next_frame(self) -> None: ...

    async def process_result(self, result: ResultSetResponse) -> None: ...

    async def _process_results(self, results: List[ResultSetResponse]) -> None: ...

    def _transform_parameters(self, parameters) -> List[Any]: ...

    async def execute(self, operation, parameters=None) -> None: ...

    async def executemany(self, operation, seq_of_parameters) -> List[int]: ...

    async def get_sync_results(self, state) -> SyncResultsResponse: ...

    async def fetch(self, signature) -> None: ...

    def transform_row(self, row: Row) -> List[Any]: ...

    async def fetchone(self) -> Any: ...

    async def fetchmany(self, size=None) -> List[Any]: ...

    async def fetchall(self) -> List[Any]: ...

    def setinputsizes(self, sizes) -> None: ...

    def setoutputsize(self, size, column=None) -> None: ...

    @property
    def connection(self) -> Connection: ...

    @property
    def rowcount(self) -> int: ...

    @property
    def rownumber(self) -> int: ...

    def ref(self,  callback: Callable[[CursorRef], Any] | None = ...) -> CursorRef: ...


class DictCursor(Cursor):
    """A cursor which returns results as a dictionary"""

    def _transform_row(self, row) -> Dict[str, Any]: ...