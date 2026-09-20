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

import typing

from qgis.core import (
    QgsCoordinateTransform,
    QgsCoordinateTransformContext,
    QgsFeatureRequest,
    QgsFillSymbol,
    QgsPrintLayout,
    QgsRuleBasedRenderer,
)
from qgis.utils import iface as utils_iface
from qgis_plugin_tools.tools.i18n import tr

from globe_builder.definitions.settings import WGS84

if typing.TYPE_CHECKING:
    from qgis.core import (
        QgsCoordinateReferenceSystem,
        QgsPointXY,
        QgsProject,
        QgsRectangle,
        QgsVectorLayer,
    )
    from qgis.gui import QgisInterface
    from qgis.PyQt.QtGui import QColor

iface = typing.cast("QgisInterface", utils_iface)


def create_layout(layout_name: str, qgis_instance: "QgsProject") -> QgsPrintLayout:
    """Create a new print layout, replacing any existing layout with the same name."""
    manager = qgis_instance.layoutManager()
    layouts_list = manager.printLayouts()
    # remove any duplicate layouts
    for existing_layout in layouts_list:
        if existing_layout.name() == layout_name:
            manager.removeLayout(existing_layout)
    layout = QgsPrintLayout(qgis_instance)
    layout.initializeDefaults()
    layout.setName(layout_name)
    manager.addLayout(layout)
    return layout


def set_selection_based_style(
    layer: "QgsVectorLayer", s_color: "QColor", else_color: "QColor"
) -> "QgsVectorLayer":
    """Style selected features with one color and the rest with another."""
    # noinspection PyCallByClass,PyArgumentList
    fill_for_selected = QgsFillSymbol.createSimple({"color": "blue"})
    fill_for_selected.setColor(s_color)
    rule_s = QgsRuleBasedRenderer.Rule(
        fill_for_selected, label=tr("Selected"), filterExp="is_selected()"
    )

    fill_for_else = fill_for_selected.clone()
    fill_for_else.setColor(else_color)
    rule_else = QgsRuleBasedRenderer.Rule(
        fill_for_else, label=tr("Not Selected"), elseRule=True
    )

    renderer = QgsRuleBasedRenderer(QgsRuleBasedRenderer.Rule(None))
    root_rule = renderer.rootRule()
    root_rule.appendChild(rule_s)
    root_rule.appendChild(rule_else)

    layer.setRenderer(renderer)
    return layer


def transform_to_wgs84(
    point: "QgsPointXY",
    crs: "QgsCoordinateReferenceSystem",
    qgis_instance: "QgsProject",
) -> "QgsPointXY":
    """Transform a point from the given CRS to WGS84."""
    transformer = QgsCoordinateTransform(crs, WGS84, qgis_instance)
    return transformer.transform(point)


def get_feature_ids_that_intersect_bbox(
    layer: "QgsVectorLayer",
    rectangle: "QgsRectangle",
    crs: "QgsCoordinateReferenceSystem",
) -> list[int]:
    """Get ids of the features intersecting the rectangle given in the CRS."""
    request = (
        QgsFeatureRequest()
        .setFilterRect(rectangle)
        .setDestinationCrs(crs=crs, context=QgsCoordinateTransformContext())
        .setNoAttributes()
        .setFlags(QgsFeatureRequest.Flag.NoGeometry)
    )
    return [f.id() for f in layer.getFeatures(request)]


def get_map_center_coordinates(
    qgis_instance: "QgsProject", number_format: str = "{:.0f}"
) -> dict[str, float]:
    """Get the center of the map canvas in WGS84 coordinates."""
    center_point = iface.mapCanvas().extent().center()
    center_point = transform_to_wgs84(center_point, qgis_instance.crs(), qgis_instance)
    return {
        "lon": float(number_format.format(center_point.x())),
        "lat": float(number_format.format(center_point.y())),
    }
