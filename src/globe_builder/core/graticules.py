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

from typing import TYPE_CHECKING

from qgis import processing
from qgis.core import (
    QgsFillSymbol,
    QgsProcessingFeedback,
    QgsVectorLayer,
)
from qgis_plugin_tools.tools.i18n import tr

from globe_builder.definitions.settings import WGS84

if TYPE_CHECKING:
    from qgis.PyQt.QtGui import QColor


class Graticules:
    """Creates a graticule layer with the processing framework.

    Algorithm: create grid, densify grid.
    """

    LAYER_NAME = tr("Graticules")

    def __init__(self, spacing: int = 30, number_of_vertices: int = 100) -> None:
        self.spacing = spacing
        self.number_of_vertices = number_of_vertices
        self.feedback = QgsProcessingFeedback()

    def create_graticules(self, stroke_color: "QColor") -> QgsVectorLayer:
        """Create a styled graticule layer."""
        temp_grid_layer = self._create_grid_layer()
        layer = self._create_graticule_layer(temp_grid_layer)
        self._set_styles(layer, stroke_color)
        return layer

    @staticmethod
    def _set_styles(layer: QgsVectorLayer, stroke_color: "QColor") -> None:
        # Set transparent fill
        renderer = layer.renderer()
        # noinspection PyArgumentList
        fill_symbol = QgsFillSymbol.createSimple({"color": "white"})
        fill_symbol_layer = fill_symbol.symbolLayers()[0]
        fill_color = fill_symbol_layer.fillColor()
        fill_color.setAlpha(0)
        fill_symbol_layer.setFillColor(fill_color)
        fill_symbol_layer.setStrokeColor(stroke_color)
        # noinspection PyUnresolvedReferences
        renderer.setSymbol(fill_symbol)
        layer.triggerRepaint()

    def _create_graticule_layer(
        self, temp_grid_layer: QgsVectorLayer
    ) -> QgsVectorLayer:
        params = {
            "INPUT": temp_grid_layer,
            "OUTPUT": f"memory:{self.LAYER_NAME}",
            "VERTICES": self.number_of_vertices,
        }
        result = processing.run(
            "native:densifygeometries", params, feedback=self.feedback
        )
        return result["OUTPUT"]

    def _create_grid_layer(self) -> QgsVectorLayer:
        params = {
            "CRS": WGS84,
            "EXTENT": "-180,180,-90,90 [EPSG:4326]",
            "HOVERLAY": 0,
            "HSPACING": self.spacing,
            "OUTPUT": "memory:tmp_grid",
            "TYPE": 2,
            "VOVERLAY": 0,
            "VSPACING": self.spacing,
        }
        result = processing.run("native:creategrid", params, feedback=self.feedback)
        return result["OUTPUT"]
