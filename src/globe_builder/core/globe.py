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

import logging
import typing
from pathlib import Path

from qgis.core import (
    Qgis,
    QgsCoordinateReferenceSystem,
    QgsLayoutItemMap,
    QgsLayoutPoint,
    QgsLayoutSize,
    QgsMapSettings,
    QgsMapThemeCollection,
    QgsProject,
    QgsRasterLayer,
    QgsRectangle,
    QgsVectorLayer,
)
from qgis.PyQt.QtGui import QColor
from qgis.utils import iface as utils_iface
from qgis_plugin_tools.tools.custom_logging import bar_msg
from qgis_plugin_tools.tools.i18n import tr
from qgis_plugin_tools.tools.resources import plugin_name
from qgis_plugin_tools.tools.settings import get_setting

from globe_builder.core.graticules import Graticules
from globe_builder.core.halo import Halo
from globe_builder.core.utils.utils import (
    get_feature_ids_that_intersect_bbox,
    set_selection_based_style,
)
from globe_builder.definitions.projections import Projections
from globe_builder.definitions.settings import (
    DEFAULT_LAYER_CONNECTION_TYPE,
    DEFAULT_ORIGIN,
    LOCAL_DATA_DIR,
    NATURAL_EARTH_BASE_URL,
    S2CLOUDLESS_WMTS_URL,
    WGS84,
    LayerConnectionType,
)

if typing.TYPE_CHECKING:
    from collections.abc import Callable

    from qgis.core import QgsLayerTreeGroup, QgsMapLayer, QgsPrintLayout
    from qgis.gui import QgisInterface

    from globe_builder.definitions.settings import Origin

LOGGER = logging.getLogger(plugin_name())

iface = typing.cast("QgisInterface", utils_iface)

type LayerStyleMethod = Callable[[QgsVectorLayer], None]


class Globe:
    """Builds and manages the globe layers, projection and layout item."""

    THEME_NAME = tr("Globe")
    GROUP_NAME = tr("Globe")

    def __init__(
        self,
        origin: "Origin" = DEFAULT_ORIGIN,
        projection: Projections = Projections.AZIMUTHAL_ORTHOGRAPHIC,
    ) -> None:
        self.origin = origin
        self.projection = projection
        # noinspection PyArgumentList
        self.qgis_instance = QgsProject.instance()

    @property
    def group(self) -> "QgsLayerTreeGroup":
        """Layer tree group of the globe, created if it does not exist."""
        root = self.qgis_instance.layerTreeRoot()
        groups = [
            child
            for child in root.children()
            if root.isGroup(child) and child.name() == Globe.GROUP_NAME
        ]
        if len(groups) == 1:
            return groups[0]
        return root.addGroup(Globe.GROUP_NAME)

    def delete_group(self) -> None:
        """Remove the globe group and its layers from the project."""
        group = self.group
        root = self.qgis_instance.layerTreeRoot()
        for layer in group.findLayers():
            self.qgis_instance.removeMapLayer(layer.layerId())
        root.removeChildNode(group)

    def set_origin(self, coordinates: "Origin | None") -> None:
        """Set the origin of the globe, None is ignored."""
        if coordinates is not None:
            self.origin = coordinates

    def set_projection(self, projection: Projections) -> None:
        """Set the projection of the globe."""
        self.projection = projection

    def set_group_visibility(self, *, is_visible: bool) -> None:
        """Set the visibility of the globe group and its layers."""
        self.group.setItemVisibilityCheckedRecursive(is_visible)

    def load_data(  # noqa: PLR0913
        self,
        *,
        load_s2: bool,
        load_countries: bool,
        load_graticules: bool,
        countries_color: QColor,
        graticules_color: QColor,
        intersecting_countries_color: QColor | None,
        countries_resolution: str,
        graticules_resolution: int,
    ) -> None:
        """Load the selected data layers to the globe group."""
        existing_layer_names = self.get_existing_layer_names()
        s2_cloudless_layer_name = tr("S2 Cloudless 2018")
        if load_s2 and s2_cloudless_layer_name not in existing_layer_names:
            s2_layer = QgsRasterLayer(
                S2CLOUDLESS_WMTS_URL, s2_cloudless_layer_name, "wms"
            )
            if s2_layer.isValid():
                self.insert_layer_to_group(s2_layer)
            else:
                LOGGER.warning(
                    tr("Could not add Sentinel 2 Cloudless layer"), extra=bar_msg()
                )

        ne_data: dict[str, tuple[str, LayerStyleMethod | None]] = {}
        if load_countries:

            def style_countries(layer: QgsVectorLayer) -> None:
                if intersecting_countries_color is None:
                    layer.renderer().symbol().setColor(countries_color)
                else:
                    set_selection_based_style(
                        layer, intersecting_countries_color, countries_color
                    )
                    ids = get_feature_ids_that_intersect_bbox(
                        layer, iface.mapCanvas().extent(), self.qgis_instance.crs()
                    )
                    layer.select(ids)

            ne_data[tr("Countries")] = (
                f"ne_{countries_resolution}_admin_0_countries.geojson",
                style_countries,
            )

        if ne_data:
            self.load_natural_earth_data(ne_data)

        graticules = Graticules(graticules_resolution)
        if load_graticules and graticules.LAYER_NAME not in existing_layer_names:
            graticule_layer = graticules.create_graticules(graticules_color)
            if graticule_layer.isValid():
                self.insert_layer_to_group(graticule_layer)
            else:
                LOGGER.warning(tr("Could not add graticules"), extra=bar_msg())

        iface.mapCanvas().refresh()

    def load_natural_earth_data(
        self, ne_data: "dict[str, tuple[str, LayerStyleMethod | None]]"
    ) -> None:
        """Load Natural Earth layers, either from local files or from the web.

        The data is a mapping from a layer name to a tuple of the source file
        name and an optional styling callback.
        """
        existing_layer_names = self.get_existing_layer_names()

        connection_type = LayerConnectionType(
            get_setting("layerConnectionType", DEFAULT_LAYER_CONNECTION_TYPE.value, int)
        )

        for name, (source, styling_method) in ne_data.items():
            layer: QgsVectorLayer | None
            if name not in existing_layer_names:
                layer = self._load_natural_earth_layer(name, source, connection_type)
            else:
                layer = self.qgis_instance.mapLayersByName(name)[0]

            if styling_method is not None and layer is not None:
                styling_method(layer)
                layer.triggerRepaint()

    def _load_natural_earth_layer(
        self, name: str, source: str, connection_type: LayerConnectionType
    ) -> QgsVectorLayer | None:
        local_path = str(Path(LOCAL_DATA_DIR) / source)
        if connection_type == LayerConnectionType.local:
            layer = QgsVectorLayer(local_path, name, "ogr")
        else:
            layer = QgsVectorLayer(f"{NATURAL_EARTH_BASE_URL}/{source}", name, "ogr")
            if not layer.isValid():
                layer = QgsVectorLayer(local_path, name, "ogr")
        if not layer.isValid():
            iface.messageBar().pushMessage(
                tr("Could not load Natural Earth layer '{}'", name),
                level=Qgis.MessageLevel.Warning,
                duration=3,
            )
            return None
        self.insert_layer_to_group(layer)
        return layer

    def insert_layer_to_group(self, layer: "QgsMapLayer", index: int = 0) -> None:
        """Add the layer to the project and insert it to the globe group."""
        if self.qgis_instance.addMapLayer(layer, False) is None:  # noqa: FBT003
            msg = tr("Could not add layer '{}' to the project", layer.name())
            raise ValueError(msg)
        self.group.insertLayer(index, layer)

    def change_project_projection(self) -> None:
        """Set the project CRS to the globe projection."""
        # Change to wgs84 to activate the changes in origin
        self.qgis_instance.setCrs(WGS84)
        proj_string = self.projection.value.proj_str(self.origin)
        crs = QgsCoordinateReferenceSystem()
        if not crs.createFromProj(proj_string):
            msg = tr("Invalid projection string: {}", proj_string)
            raise ValueError(msg)
        self.qgis_instance.setCrs(crs)

    def change_temporarily_to_globe_projection(self) -> None:
        """Set the project CRS to the globe projection and restore the old one."""
        crs = self.qgis_instance.crs()
        self.change_project_projection()
        self.qgis_instance.setCrs(crs)

    def change_background_color(self, new_background_color: QColor) -> None:
        """Change the map canvas background color."""
        # Write it to the project (will still need to be saved!)
        self.qgis_instance.writeEntry(
            "Gui", "/CanvasColorRedPart", new_background_color.red()
        )
        self.qgis_instance.writeEntry(
            "Gui", "/CanvasColorGreenPart", new_background_color.green()
        )
        self.qgis_instance.writeEntry(
            "Gui", "/CanvasColorBluePart", new_background_color.blue()
        )

        # And apply for the current session
        iface.mapCanvas().setCanvasColor(new_background_color)
        iface.mapCanvas().refresh()

    # noinspection PyArgumentList
    @staticmethod
    def get_existing_layer_names() -> list[str]:
        """Get the names of all the layers in the project."""
        return [layer.name() for layer in QgsProject.instance().mapLayers().values()]

    # noinspection PyArgumentList
    def add_halo(
        self,
        stroke_color: QColor,
        fill_color: QColor | None = None,
        *,
        use_effects: bool,
        halo_with_fill: bool = False,
    ) -> None:
        """Add a halo layer to the globe group, replacing any existing halo."""
        halo = Halo(self.origin, self.projection)

        if halo_with_fill:
            self.add_halo(stroke_color, use_effects=True)
        else:
            for layer in self.qgis_instance.mapLayersByName(halo.LAYER_NAME):
                self.qgis_instance.removeMapLayer(layer.id())

        layer, index = halo.create_halo_layer(
            stroke_color, fill_color, use_effects=use_effects
        )
        self.insert_layer_to_group(layer, index)

    def refresh_theme(self) -> None:
        """Recreate the globe map theme from the layers in the globe group."""
        theme_collection = self.qgis_instance.mapThemeCollection()
        layers = [layer.layer() for layer in self.group.findLayers()]
        if Globe.THEME_NAME in theme_collection.mapThemes():
            theme_collection.removeMapTheme(Globe.THEME_NAME)
        if layers:
            map_theme_record = QgsMapThemeCollection.MapThemeRecord()
            map_theme_record.setLayerRecords(
                [QgsMapThemeCollection.MapThemeLayerRecord(layer) for layer in layers]
            )
            theme_collection.insert(Globe.THEME_NAME, map_theme_record)

    def add_to_layout(
        self,
        layout: "QgsPrintLayout",
        background_color: QColor | None = None,
        size: int = 80,
    ) -> None:
        """Add a map item showing the globe to the layout.

        Inspired by
        https://opensourceoptions.com/blog/pyqgis-create-and-print-a-map-layout-with-python/
        """
        if background_color is None:
            background_color = QColor(255, 255, 255, 0)
        layers = [layer.layer() for layer in self.group.findLayers()]
        # create map item in the layout
        map_item = QgsLayoutItemMap(layout)
        map_item.setRect(20, 20, 20, 20)
        # set the map extent
        map_settings = QgsMapSettings()
        map_settings.setLayers(layers)  # set layers to be mapped
        crs = QgsCoordinateReferenceSystem()
        if not crs.createFromProj(self.projection.value.proj_str(self.origin)):
            msg = tr("Invalid projection string: {}", self.projection.value.name)
            raise ValueError(msg)
        map_item.setCrs(crs)
        map_item.setFollowVisibilityPreset(True)
        map_item.setFollowVisibilityPresetName(Globe.THEME_NAME)
        rectangle = QgsRectangle(map_settings.fullExtent())

        map_settings.setExtent(rectangle)
        map_item.setExtent(rectangle)
        map_item.setBackgroundColor(background_color)
        layout.addLayoutItem(map_item)
        map_item.attemptMove(QgsLayoutPoint(5, 20, Qgis.LayoutUnit.Millimeters))
        map_item.attemptResize(QgsLayoutSize(size, size, Qgis.LayoutUnit.Millimeters))
