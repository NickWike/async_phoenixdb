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

import datetime
import sys
from typing import Dict, Any, List, Tuple, Set

from aiophoenixdb.avatica.proto import common_pb

__all__: List[str]

def to_date(year: int, month: int, day: int) -> datetime.date: ...


def to_time(hour: int, minute: int, second: int) -> datetime.time: ...


def to_timestamp(year: int, month: int, day: int, hour: int, minute: int, second: int) -> datetime.datetime: ...


def to_date_from_ticks(ticks) -> datetime.date: ...


def to_time_from_ticks(ticks) -> datetime.time: ...


def to_timestamp_from_ticks(ticks) -> datetime.datetime: ...


def to_binary(value) -> bytes: ...


def time_from_java_sql_time(n) -> datetime.time: ...


def time_to_java_sql_time(t) -> int: ...


def date_from_java_sql_date(n) -> datetime.date: ...


def date_to_java_sql_date(d) -> int: ...


def datetime_from_java_sql_timestamp(n) -> datetime: ...


def datetime_to_java_sql_timestamp(d) -> int: ...


# FIXME This doesn't seem to be used anywhere in the code
class ColumnType(object):

    eq_types: Tuple[str]
    eq_types_set: Set[str]

    def __init__(self, eq_types: List[str]): ...

    def __eq__(self, other) -> bool: ...

    def __cmp__(self, other) -> int: ...


STRING: ColumnType

BINARY: ColumnType

NUMBER: ColumnType

DATETIME: ColumnType

ROWID: ColumnType

BOOLEAN : ColumnType

if sys.version_info[0] < 3:
    _long = long  # noqa: F821
else:
    _long = int

FIELD_MAP: Dict[str, Any]

REP_MAP: Dict[common_pb.Rep, Any]

JDBC_TO_REP: Dict[int, common_pb.Rep]

JDBC_MAP: Dict[int, Any]


class TypeHelper(object):

    @staticmethod
    def from_param(param) -> Any: ...

    @staticmethod
    def from_column(column) -> Any: ...

    @staticmethod
    def _from_jdbc(jdbc_code) -> Any: ...