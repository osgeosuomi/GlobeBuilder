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

from qgis.core import (QgsFillSymbol, QgsEffectStack, QgsDropShadowEffect, QgsInnerShadowEffect,
                       QgsGeometryGeneratorSymbolLayer, QgsVectorLayer, QgsFeature, QgsGeometry, QgsPointXY,
                       QgsCoordinateTransform, QgsProject)
from qgis.gui import QgisInterface

from globe_builder.definitions.projections import Projections
from globe_builder.definitions.settings import (TRANSPARENT_COLOR, HaloDrawMethod, EARTH_RADIUS, DEFAULT_HALO_DRAW_METHOD,
                                    DEFAULT_NUMBER_OF_SEGMENTS, WGS84)
from qgis_plugin_tools.tools.i18n import tr
from qgis_plugin_tools.tools.settings import get_setting


class Halo:
    LAYER_NAME = tr('Halo')

    def __init__(self, iface: QgisInterface, origin, projection) -> None:
        self.iface = iface
        self.origin = origin
        self.projection = projection

    def create_halo_layer(self, use_effects, stroke_color, fill_color=None):
        # noinspection PyArgumentList
        qgis_instance: QgsProject = QgsProject.instance()

        draw_method = HaloDrawMethod(
            get_setting("haloDrawMethod", DEFAULT_HALO_DRAW_METHOD.value, str))
        proj_string = self.projection.value.proj_str(self.origin)
        # Block signals required to prevent the pop up asking about the crs change
        self.iface.mainWindow().blockSignals(True)
        layer = QgsVectorLayer(draw_method.value, self.LAYER_NAME, "memory")
        crs = layer.crs()
        crs.createFromProj(proj_string)
        layer.setCrs(crs)
        self.iface.mainWindow().blockSignals(False)

        feature = QgsFeature()
        if self.projection == Projections.AZIMUTHAL_ORTHOGRAPHIC:
            # noinspection PyArgumentList
            geom = QgsGeometry.fromPointXY(QgsPointXY(self.origin['lat'], self.origin['lon']))
            if draw_method == HaloDrawMethod.buffered_point:
                geom = geom.buffer(EARTH_RADIUS, DEFAULT_NUMBER_OF_SEGMENTS)
        else:
            geom = self.create_grid_halo(layer.crs())

        feature.setGeometry(geom)
        provider = layer.dataProvider()
        layer.startEditing()
        provider.addFeatures([feature])
        layer.commitChanges()

        # Assign styles and to map (but not toc yet)
        self.set_halo_styles(layer, draw_method, stroke_color, use_effects, fill_color)
        qgis_instance.addMapLayer(layer, False)

        index = 0 if use_effects else -1
        return layer, index

    # noinspection PyCallByClass
    @staticmethod
    def set_halo_styles(layer, draw_method, stroke_color, use_effects, fill_color=None):
        renderer = layer.renderer()
        sym = renderer.symbol()

        props = {'color': 'blue'}
        # noinspection PyArgumentList
        fill_symbol = QgsFillSymbol.createSimple(props)
        fill_symbol_layer = fill_symbol.symbolLayers()[0]
        fill_symbol_layer.setStrokeColor(stroke_color)
        if fill_color is not None:
            fill_symbol_layer.setColor(fill_color)
        elif not use_effects:
            fill_symbol_layer.setColor(TRANSPARENT_COLOR)

        if use_effects:
            # Assign effects
            effect_stack = QgsEffectStack()
            drop_shdw = QgsDropShadowEffect()
            drop_shdw.setColor(stroke_color)
            inner_shdw = QgsInnerShadowEffect()
            inner_shdw.setColor(stroke_color)
            effect_stack.appendEffect(drop_shdw)
            effect_stack.appendEffect(inner_shdw)

            fill_symbol_layer.setPaintEffect(effect_stack)
        # noinspection PyArgumentList
        if draw_method == HaloDrawMethod.buffered_point:
            renderer.setSymbol(fill_symbol)
        else:
            # noinspection PyCallByClass, PyArgumentList
            geom_generator_sl = QgsGeometryGeneratorSymbolLayer.create({
                'SymbolType': 'Fill',
                'geometryModifier': 'buffer($geometry, {:d})'.format(EARTH_RADIUS)
            })
            geom_generator_sl.setSubSymbol(fill_symbol)
            sym.changeSymbolLayer(0, geom_generator_sl)

        layer.triggerRepaint()
        return layer

    @staticmethod
    def create_grid_halo(crs):
        min_x = -180
        min_y = -90
        max_x = 180
        max_y = 90
        step = 2
        coords = []
        for y in range(min_y, max_y + step, step):
            coords.append((min_x, y))
        for x in range(min_x + step, max_x + step, step):
            coords.append((x, max_y))
        for y in reversed(range(min_y, max_y + step, step)):
            coords.append((max_x, y))
        for x in reversed(range(min_x + step, max_x + step, step)):
            coords.append((x, min_y))
        coords.append(coords[0])
        # noinspection PyCallByClass,PyArgumentList
        geom = QgsGeometry.fromPolygonXY([[QgsPointXY(pair[0], pair[1]) for pair in coords]]).asQPolygonF()
        # noinspection PyArgumentList
        transformer = QgsCoordinateTransform(WGS84, crs, QgsProject.instance())
        transformer.transformPolygon(geom)
        # noinspection PyArgumentList
        return QgsGeometry.fromQPolygonF(geom)
