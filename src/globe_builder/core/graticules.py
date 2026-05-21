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

from PyQt5.QtGui import QColor
from qgis.core import (QgsProcessingFeedback, QgsVectorLayer, QgsFillSymbol,
                       QgsSymbolLayer, QgsFeatureRenderer)

from globe_builder.definitions.settings import WGS84
from qgis_plugin_tools.tools.i18n import tr

'''
alg:
create grid!
densify grid!
'''


class Graticules:
    LAYER_NAME = tr('Graticules')

    def __init__(self, spacing=30, num_vertices=100) -> None:
        self.spacing = spacing
        self.num_vertices = num_vertices
        self.feedback = QgsProcessingFeedback()

    def create_graticules(self, stroke_color):
        tmp_grid_layer = self._create_grid_layer()
        layer = self._create_graticule_layer(tmp_grid_layer)
        self._set_styles(layer, stroke_color)
        return layer

    @staticmethod
    def _set_styles(layer, stroke_color):
        # Set transparent fill

        renderer: QgsFeatureRenderer = layer.renderer()
        props = {'color': 'white'}
        # noinspection PyArgumentList
        fill_symbol = QgsFillSymbol.createSimple(props)
        fill_symbol_layer: QgsSymbolLayer = fill_symbol.symbolLayers()[0]
        fill_color: QColor = fill_symbol_layer.fillColor()
        fill_color.setAlpha(0)
        fill_symbol_layer.setFillColor(fill_color)
        fill_symbol_layer.setStrokeColor(stroke_color)
        # noinspection PyUnresolvedReferences
        renderer.setSymbol(fill_symbol)
        layer.triggerRepaint()

    def _create_graticule_layer(self, tmp_grid_layer) -> QgsVectorLayer:
        # noinspection PyUnresolvedReferences
        import processing
        params = {
            'INPUT': tmp_grid_layer,
            'OUTPUT': f'memory:{self.LAYER_NAME}', 'VERTICES': self.num_vertices}
        res = processing.run('native:densifygeometries', params, feedback=self.feedback)
        layer: QgsVectorLayer = res['OUTPUT']

        return layer

    def _create_grid_layer(self) -> QgsVectorLayer:
        # noinspection PyUnresolvedReferences
        import processing
        params = {'CRS': WGS84,
                  'EXTENT': '-180,180,-90,90 [EPSG:4326]', 'HOVERLAY': 0, 'HSPACING': self.spacing,
                  'OUTPUT': 'memory:tmp_grid', 'TYPE': 2, 'VOVERLAY': 0, 'VSPACING': self.spacing}
        res = processing.run('native:creategrid', params, feedback=self.feedback)
        tmp_grid_layer = res['OUTPUT']
        return tmp_grid_layer
