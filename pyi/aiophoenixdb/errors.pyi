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

__all__: List[str]


class _StandardError(Exception):
    """Base Error"""


class WarningException(_StandardError):
    """Not used by this package, only defined for compatibility
    with DB API 2.0."""


class Error(_StandardError):
    """Exception that is the base class of all other error exceptions.
    You can use this to catch all errors with one single except statement."""

    def __init__(self, message, code=None, sqlstate=None, cause=None): ...
    @property
    def message(self): ...

    @property
    def code(self): ...

    @property
    def sqlstate(self): ...

    @property
    def cause(self): ...


class InterfaceError(Error):
    """Exception raised for errors that are related to the database
    interface rather than the database itself."""


class DatabaseError(Error):
    """Exception raised for errors that are related to the database."""


class DataError(DatabaseError):
    """Exception raised for errors that are due to problems with the
    processed data like division by zero, numeric value out of range,
    etc."""


class OperationalError(DatabaseError):
    """Raised for errors that are related to the database's operation and not
    necessarily under the control of the programmer, e.g. an unexpected
    disconnect occurs, the data source name is not found, a transaction could
    not be processed, a memory allocation error occurred during
    processing, etc."""


class IntegrityError(DatabaseError):
    """Raised when the relational integrity of the database is affected, e.g. a foreign key check fails."""


class InternalError(DatabaseError):
    """Raised when the database encounters an internal problem."""


class ProgrammingError(DatabaseError):
    """Raises for programming errors, e.g. table not found, syntax error, etc."""


class NotSupportedError(DatabaseError):
    """Raised when using an API that is not supported by the database."""

class MasRetriesError(_StandardError):
    """Raised when retry more than the maximum number of attempts."""
