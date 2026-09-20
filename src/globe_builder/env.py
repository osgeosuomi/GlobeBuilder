#  Copyright (C) 2026 GlobeBuilder contributors.
#
#
#  This file is part of GlobeBuilder.
#
#  GlobeBuilder is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 2 of the License, or
#  (at your option) any later version.
#
#  GlobeBuilder is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with GlobeBuilder.  If not, see <https://www.gnu.org/licenses/>.

import os
from dataclasses import dataclass

_TRUTHY_STRINGS = (
    "1",
    "true",
    "yes",
    "t",
)


@dataclass
class EnvVariable:
    """Represents a configurable environment variable."""

    key: str
    default: str = ""
    mandatory: bool = True

    @property
    def value(self) -> str:
        """Environment variable value or the configured default value.

        Raises:
            KeyError: If a mandatory variable is not defined in the environment.

        """
        value_from_env = os.environ.get(self.key, self.default)

        if self.mandatory and value_from_env == "":
            msg = f"Env variable not configured: {self.key}"
            raise KeyError(msg)

        return value_from_env

    def get_optional_value(self) -> str | None:
        """Return the environment variable value, or None if it is empty."""
        return self.value or None

    def __bool__(self) -> bool:
        return self.value.lower() in _TRUTHY_STRINGS

    def __int__(self) -> int:
        return int(self.value)


IS_DEVELOPMENT_MODE = EnvVariable("IS_DEVELOPMENT_MODE", default="no", mandatory=False)
