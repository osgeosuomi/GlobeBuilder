"""
This class contains fixtures and common helper function to keep the test files shorter

pytest-qgis (https://pypi.org/project/pytest-qgis) contains the following helpful fixtures:

* qgis_app initializes and returns fully configured QgsApplication.
  This fixture is called automatically on the start of pytest session.
* qgis_canvas initializes and returns QgsMapCanvas
* qgis_iface returns mocked QgsInterface
* new_project makes sure that all the map layers and configurations are removed.
  This should be used with tests that add stuff to QgsProject.

"""

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

from globe_builder.core.globe import Globe
from globe_builder.definitions.projections import Projections


@pytest.fixture(scope='function')
def globe(qgis_new_project, qgis_iface) -> Globe:
    globe = Globe(qgis_iface)
    globe.set_projection(Projections.AZIMUTHAL_ORTHOGRAPHIC)
    return globe
