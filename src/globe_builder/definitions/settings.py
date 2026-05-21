# -*- coding: utf-8 -*-


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

import enum

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from qgis.core import QgsCoordinateReferenceSystem

from qgis_plugin_tools.tools.resources import resources_path


class LayerConnectionType(enum.Enum):
    local = 1
    url = 2


class HaloDrawMethod(enum.Enum):
    geometry_generator = "Point"
    buffered_point = "Polygon"


NATURAL_EARTH_BASE_URL = "https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson"
S2CLOUDLESS_WMTS_URL = "url=https://tiles.maps.eox.at/wmts?SERVICE%3DWMTS%26REQUEST%3DGetCapabilities&contextualWMSLegend=0&crs=EPSG:4326&dpiMode=7&featureCount=10&format=image/jpeg&layers=s2cloudless-2018&styles=default&tileMatrixSet=WGS84"
LOCAL_DATA_DIR = resources_path("data")
DEFAULT_ORIGIN = {'lat': 42.5, 'lon': 0.5}

EARTH_RADIUS = 6370997
DEFAULT_NUMBER_OF_SEGMENTS = 64
DEFAULT_LAYER_CONNECTION_TYPE = LayerConnectionType.local
DEFAULT_HALO_DRAW_METHOD = HaloDrawMethod.buffered_point

_crs = QgsCoordinateReferenceSystem()
_crs.createFromId(4326)
WGS84 = _crs

# Colors
DEFAULT_BACKGROUND_COLOR = QColor(Qt.black)
DEFAULT_LAYOUT_BACKGROUND_COLOR = QColor(Qt.white)
DEFAULT_COUNTRIES_COLOR = QColor(Qt.darkGreen)
DEFAULT_GRATICULES_COLOR = QColor(Qt.gray)
DEFAULT_HALO_COLOR = QColor(Qt.lightGray)
DEFAULT_HALO_LAYOUT_COLOR = QColor(Qt.black)
DEFAULT_HALO_FILL_COLOR = QColor(Qt.blue)
DEFAULT_INTERSECTING_COUNTRIES_COLOR = QColor(Qt.red)
_transparent = QColor(Qt.black)
_transparent.setAlpha(0)
TRANSPARENT_COLOR = _transparent

# UI
NOMINATIM_URL = "https://nominatim.openstreetmap.org/search/{query}?limit={limit}&format=geojson"
DEFAULT_MAX_NUMBER_OF_RESULTS = 5
MAX_NAME_PARTS = 3
DEFAULT_USE_NE_COUNTRIES = True
DEFAULT_USE_NE_GRATICULES = False
DEFAULT_USE_S2_CLOUDLESS = False
