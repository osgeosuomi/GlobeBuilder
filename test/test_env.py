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

import pytest

from globe_builder.env import EnvVariable

MOCK_ENV_VARIABLE = "MOCK_ENV_VAR"


def test_string_env_variable(monkeypatch: "pytest.MonkeyPatch"):
    env_value = "env_value"
    monkeypatch.setenv(MOCK_ENV_VARIABLE, env_value)
    env_variable = EnvVariable(MOCK_ENV_VARIABLE)

    assert env_variable.value == env_value


def test_int_env_variable(monkeypatch: "pytest.MonkeyPatch"):
    env_value = 1
    monkeypatch.setenv(MOCK_ENV_VARIABLE, str(env_value))
    env_variable = EnvVariable(MOCK_ENV_VARIABLE)

    assert int(env_variable) == env_value


@pytest.mark.parametrize(
    ("env_value", "expected_value"),
    [
        ("1", True),
        ("0", False),
        ("True", True),
        ("False", False),
        ("yes", True),
        ("no", False),
    ],
    ids=[
        "integer true",
        "integer false",
        "true",
        "false",
        "yes/no true",
        "yes/no false",
    ],
)
def test_bool_env_variable(
    monkeypatch: "pytest.MonkeyPatch", env_value: str, expected_value: bool
):
    monkeypatch.setenv(MOCK_ENV_VARIABLE, env_value)
    env_variable = EnvVariable(MOCK_ENV_VARIABLE)

    assert bool(env_variable) == expected_value


def test_get_missing_env_variable_with_default():
    default = "some-default"
    env_variable = EnvVariable(MOCK_ENV_VARIABLE, default)

    assert env_variable.value == default
    assert env_variable.get_optional_value() == default


def test_get_missing_env_variable_with_no_default_raises_error():
    env_variable = EnvVariable(MOCK_ENV_VARIABLE)

    with pytest.raises(KeyError, match="Env variable"):
        env_variable.get_optional_value()


def test_get_missing_env_variable_with_no_default_but_not_mandatory_does_not_raise():
    env_variable = EnvVariable(MOCK_ENV_VARIABLE, mandatory=False)

    assert env_variable.value == ""
    assert env_variable.get_optional_value() is None
