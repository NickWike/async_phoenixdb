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

from .cursors import Cursor, CursorRef
from .avatica.client import AvaticaClient
from typing import Generic, TypeVar, overload, Dict, Any, List
from aiophoenixdb.typeshed import Props, Self
from .meta import Meta

_C = TypeVar("_C", bound=Cursor)
_C2 = TypeVar("_C2", bound=Cursor)


class Connection(Generic[_C]):

    _client: AvaticaClient
    _closed: bool
    _cursors: List[CursorRef]
    cursor_factory: type[Cursor]
    _phoenix_props: Dict[str, Any]
    avatica_props_init: Dict[str, Any]
    _conn_id: str
    _avatica_props: Dict

    def __init__(self,
                 client: AvaticaClient,
                 cursor_factory: _C,
                 **kwargs
                 ): ...

    async def connect(self): ...
    async def __aenter__(self: Self) -> Self: ...
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None: ...

    @property
    def client(self) -> AvaticaClient: ...
    @property
    def closed(self) -> bool: ...
    @property
    def connect_id(self) -> str: ...
    @property
    def _default_avatica_props(self): ...
    @staticmethod
    def _map_conn_props(conn_props: Props): ...
    @staticmethod
    def _map_legacy_avatica_props(props: Props): ...
    async def open(self) -> None: ...
    async def close(self) -> None: ...
    async def commit(self) -> None: ...
    async def rollback(self) -> None: ...

    def cursor(self) -> _C: ...
    @overload
    def cursor(self, cursor_factory: type[_C2] | None = ...) -> _C2: ...
    async def set_session(self, **props) -> None: ...

    @overload
    def autocommit(self) -> bool: ...
    @overload
    def autocommit(self, value) -> None: ...

    @overload
    def readonly(self) -> bool: ...
    @overload
    def readonly(self, value) -> None: ...

    @overload
    def transactionisolation(self) -> bool: ...
    @overload
    def transactionisolation(self, value) -> None: ...

    def meta(self) -> Meta: ...