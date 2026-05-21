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

from enum import Enum
from typing import Tuple

from qgis_plugin_tools.tools.i18n import tr


class Projection:

    def __init__(self, name: str, proj_str: str, min_proj_version: Tuple[int, int] = (0, 0)):
        self.name = name
        self.proj_str_raw = proj_str
        self.min_proj = min_proj_version

    def proj_str(self, origin: {str: float}) -> str:
        return self.proj_str_raw.format(**origin)


class Projections(Enum):
    AZIMUTHAL_ORTHOGRAPHIC = Projection(tr(u'Azimuthal Orthographic'),
                                        '+proj=ortho +lat_0={lat} +lon_0={lon} +x_0=0 +y_0=0 +a=6370997 +b=6370997 +units=m +no_defs')

    # Unfortunately +lon_0={lon} causes nasty rendering artifacts for all projections below (tested with QGIS 3.14.0 and 3.20.3)

    # https://www.gislounge.com/how-to-use-the-equal-earth-projection-using-qgis-on-the-mac/
    EQUAL_EARTH = Projection(tr(u'Equal Earth'), '+proj=eqearth +datum=WGS84 +units=m +no_defs', (5, 2))

    # 'https://proj.org/operations/projections/hammer.html'
    HAMMER_ECKERT = Projection(tr(u'Hammer & Eckert-Greifendorff'), '+proj=hammer')

    # 'https://proj.org/operations/projections/aitoff.html'
    AITOFF = Projection(tr(u'Aitoff'), '+proj=aitoff')

    # 'https://proj.org/operations/projections/eck1.html'
    ECKERT_I = Projection(tr(u'Eckert I'), '+proj=eck1')

    @staticmethod
    def proj_from_id(tr_name: str):
        for projection in Projections:
            if projection.value.name == tr_name:
                return projection
