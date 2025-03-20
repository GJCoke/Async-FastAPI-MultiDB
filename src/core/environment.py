"""
Environment enum constant.

Defines the possible environments for the application and includes helper properties
to determine the environment's specific characteristics.

Author : Coke
Date   : 2025-03-11
"""

from enum import Enum

DB_NAMING_CONVENTION = {
    "ix": "%(column_0_label)s_idx",
    "uq": "%(table_name)s_%(column_0_name)s_key",
    "ck": "%(table_name)s_%(constraint_name)s_check",
    "fk": "%(table_name)s_%(column_0_name)s_fkey",
    "pk": "%(table_name)s_pkey",
}


class Environment(str, Enum):
    LOCAL = "LOCAL"
    STAGING = "STAGING"
    TESTING = "TESTING"
    PRODUCTION = "PRODUCTION"

    @property
    def is_debug(self) -> bool:
        """Returns True if the environment is LOCAL, STAGING, or TESTING."""
        return self in (self.LOCAL, self.STAGING, self.TESTING)

    @property
    def is_testing(self) -> bool:
        """Returns True if the environment is TESTING."""
        return self == self.TESTING

    @property
    def is_deployed(self) -> bool:
        """Returns True if the environment is STAGING or PRODUCTION."""
        return self in (self.STAGING, self.PRODUCTION)
