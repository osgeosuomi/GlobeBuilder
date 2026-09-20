#  Copyright (C) 2020-2021 GlobeBuilder contributors.
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
from qgis.core import QgsProject

from globe_builder.core.globe import Globe
from globe_builder.definitions.projections import Projections

"""
!!! IMPORTANT !!!
DO NOT import anything that imports qgis.utils.iface
(or some module that imports other module that imports it) in conftest root!
Importing those modules in fixtures is OK.

The same goes with globe_builder.env.py.
"""


@pytest.fixture(autouse=True)
def _set_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Set environment variables for tests."""
    monkeypatch.setenv("IS_DEVELOPMENT_MODE", "yes")


@pytest.fixture(autouse=True)
def _reset_session_state(
    qgis_new_project: None,
) -> None:
    if project_instance := QgsProject.instance():
        project_instance.clear()


@pytest.fixture(scope="function")
def globe(qgis_iface) -> Globe:
    globe = Globe(qgis_iface)
    globe.set_projection(Projections.AZIMUTHAL_ORTHOGRAPHIC)
    return globe
