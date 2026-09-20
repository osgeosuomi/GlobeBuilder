#  Copyright (C) 2020-2026 GlobeBuilder contributors.
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

import configparser
from pathlib import Path

import globe_builder
from globe_builder.core.globe import LOGGER


def test_metadata():
    metadata = configparser.ConfigParser()
    metadata.read(Path(globe_builder.__file__).parent / "metadata.txt")
    assert metadata["general"]["name"] == "Globe Builder"
    assert metadata["general"]["repository"].endswith("/GlobeBuilder")


def test_plugin_name_is_resolved_from_metadata():
    assert LOGGER.name == "GlobeBuilder"
