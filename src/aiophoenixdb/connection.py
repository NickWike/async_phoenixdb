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
import uuid
from aiophoenixdb import errors
from aiophoenixdb.errors import ProgrammingError
from aiophoenixdb.meta import Meta


__all__ = ['Connection']

logger = logging.getLogger(__name__)

AVATICA_PROPERTIES = ('autoCommit', 'autocommit', 'readOnly', 'readonly', 'transactionIsolation',
                      'catalog', 'schema')


class Connection(object):
    """Database connection.

    You should not construct this object manually, use :func:`~aiophoenixdb.connect` instead.
    """

    """
    The default cursor factory used by :meth:`cursor` if the parameter is not specified.
    """

    def __init__(self, client, cursor_factory=None, **kwargs):
        self._client = client
        self._closed = False
        if cursor_factory is not None:
            self.cursor_factory = cursor_factory
        else:
            from aiophoenixdb.cursors import Cursor
            self.cursor_factory = Cursor
        self._cursors = []
        self._phoenix_props, self.avatica_props_init = Connection._map_conn_props(kwargs)
        self._conn_id = str(uuid.uuid4())
        self._avatica_props = dict()

    async def connect(self):
        await self.open()
        await self.set_session(**self.avatica_props_init)

    # def __del__(self):
    #     asyncio.get_running_loop().run_until_complete(self.close())
    #     print("connect del del del del ", self._closed)

    def __enter__(self):
        raise TypeError("Use async with instead")

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if not self._closed:
            await self.close()

    @property
    def client(self):
        return self._client

    @property
    def closed(self):
        return self._closed

    @property
    def connect_id(self):
        return self._conn_id

    @property
    def _default_avatica_props(self):
        return {'autoCommit': False,
                'readOnly': False,
                'transactionIsolation': 0,
                'catalog': '',
                'schema': ''}

    @staticmethod
    def _map_conn_props(conn_props):
        """Sorts and prepocesses args that should be passed to Phoenix and Avatica"""

        avatica_props = dict([(k, conn_props[k]) for k in conn_props.keys() if k in AVATICA_PROPERTIES])
        phoenix_props = dict([(k, conn_props[k]) for k in conn_props.keys() if k not in AVATICA_PROPERTIES])
        avatica_props = Connection._map_legacy_avatica_props(avatica_props)

        return phoenix_props, avatica_props

    @staticmethod
    def _map_legacy_avatica_props(props):
        if 'autocommit' in props:
            props['autoCommit'] = bool(props.pop('autocommit'))
        if 'readonly' in props:
            props['readOnly'] = bool(props.pop('readonly'))
        return props

    async def open(self):
        """Opens the connection."""
        await self._client.open_connection(self._conn_id, info=self._phoenix_props)

    async def close(self):
        """Closes the connection.
        No further operations are allowed, either on the connection or any
        of its cursors, once the connection is closed.

        If the connection is used in a ``with`` statement, this method will
        be automatically called at the end of the ``with`` block.
        """
        if self._closed:
            raise ProgrammingError('The connection is already closed.')
        for cursor_ref in self._cursors:
            cursor = cursor_ref()
            if cursor is not None and not cursor.closed:
                await cursor.close()
        await self._client.close_connection(self._conn_id)
        await self._client.close()
        self._closed = True

    async def commit(self):
        if self._closed:
            raise ProgrammingError('The connection is already closed.')
        await self._client.commit(self._conn_id)

    async def rollback(self):
        if self._closed:
            raise ProgrammingError('The connection is already closed.')
        await self._client.rollback(self._conn_id)

    def cursor(self, cursor_factory=None):
        """Creates a new cursor.

        :param cursor_factory:
            This argument can be used to create non-standard cursors.
            The class returned must be a subclass of
            :class:`~aiophoenixdb.cursor.Cursor` (for example :class:`~aiophoenixdb.cursor.DictCursor`).
            A default factory for the connection can also be specified using the
            :attr:`cursor_factory` attribute.

        :returns:
            A :class:`~aiophoenixdb.cursor.Cursor` object.
        """
        if self._closed:
            raise ProgrammingError('The connection is already closed.')
        cursor = (cursor_factory or self.cursor_factory)(self)
        self._cursors.append(cursor.ref(self._cursors.remove))
        return cursor

    async def set_session(self, **props):
        """Sets one or more parameters in the current connection.

        :param autocommit:
            Switch the connection to autocommit mode.

        :param readonly:
            Switch the connection to read-only mode.
        """
        props = Connection._map_legacy_avatica_props(props)
        self._avatica_props = await self._client.connection_sync_dict(self._conn_id, props)

    @property
    def autocommit(self):
        """Read/write attribute for switching the connection's autocommit mode."""
        return self._avatica_props['autoCommit']

    async def set_autocommit(self, value):
        if self._closed:
            raise ProgrammingError('The connection is already closed.')
        self._avatica_props = await self._client.connection_sync_dict(self._conn_id, {'autoCommit': bool(value)})

    @property
    def readonly(self):
        """Read/write attribute for switching the connection's readonly mode."""
        return self._avatica_props['readOnly']

    async def set_readonly(self, value):
        if self._closed:
            raise ProgrammingError('The connection is already closed.')
        self._avatica_props = await self._client.connection_sync_dict(self._conn_id, {'readOnly': bool(value)})

    @property
    def transactionisolation(self):
        return self._avatica_props['_transactionIsolation']

    async def set_transactionisolation(self, value):
        if self._closed:
            raise ProgrammingError('The connection is already closed.')
        self._avatica_props = await self._client.connection_sync_dict(
            self._conn_id, {'transactionIsolation': bool(value)})

    def meta(self):
        """Creates a new meta.

        :returns:
            A :class:`~aiophoenixdb.meta` object.
        """
        if self._closed:
            raise ProgrammingError('The connection is already closed.')
        meta = Meta(self)
        return meta


for name in errors.__all__:
    setattr(Connection, name, getattr(errors, name))
