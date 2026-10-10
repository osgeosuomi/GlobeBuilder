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

import urllib.request
from typing import TYPE_CHECKING

import pytest
from qgis.core import (
    QgsProject,
    QgsSingleSymbolRenderer,
    QgsVectorLayer,
)
from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtGui import QColor
from qgis_plugin_tools.utils.typing_utils import require, require_type

from GlobeBuilder.core.globe import Globe
from GlobeBuilder.core.halo import Halo
from GlobeBuilder.definitions.projections import Projections
from GlobeBuilder.definitions.settings import DEFAULT_ORIGIN, S2CLOUDLESS_WMTS_URL

if TYPE_CHECKING:
    from pytest_qgis.qgis_interface import QgisInterface
    from qgis.gui import QgsMapCanvas


def _s2cloudless_service_is_reachable() -> bool:
    url = (
        S2CLOUDLESS_WMTS_URL.split("url=", 1)[1]
        .split("&", 1)[0]
        .replace("%3D", "=")
        .replace("%26", "&")
    )
    try:
        with urllib.request.urlopen(url, timeout=10):
            return True
    except OSError:
        return False


requires_s2cloudless = pytest.mark.skipif(
    not _s2cloudless_service_is_reachable(),
    reason="Sentinel-2 cloudless WMTS service is not reachable",
)


def load_data(
    globe: Globe,
    *,
    load_s2: bool = False,
    load_countries: bool = False,
    load_graticules: bool = False,
    intersecting_countries_color: QColor | None = None,
) -> None:
    globe.load_data(
        load_s2=load_s2,
        load_countries=load_countries,
        load_graticules=load_graticules,
        countries_color=QColor(Qt.GlobalColor.blue),
        graticules_color=QColor(Qt.GlobalColor.blue),
        intersecting_countries_color=intersecting_countries_color,
        countries_resolution="50m",
        graticules_resolution=10,
    )


def test_projection_change_with_default_origin(globe: Globe):
    """Test if projection really changes"""
    globe.change_project_projection()
    expected_proj = Projections.AZIMUTHAL_ORTHOGRAPHIC.value.proj_str(DEFAULT_ORIGIN)
    assert require(QgsProject.instance()).crs().toProj() == expected_proj


def test_projection_change_with_custom_origin(globe: Globe):
    """Test if projection really changes"""
    custom_origin = {"lat": 10, "lon": 10}
    globe.set_origin(custom_origin)
    globe.change_project_projection()
    expected_proj = Projections.AZIMUTHAL_ORTHOGRAPHIC.value.proj_str(custom_origin)
    assert require(QgsProject.instance()).crs().toProj() == expected_proj


def test_projection_change_preserves_scale_and_centers_origin(
    globe: Globe, qgis_canvas: "QgsMapCanvas"
):
    qgis_canvas.zoomScale(5_000_000)
    scale = qgis_canvas.scale()
    globe.change_project_projection()
    center = qgis_canvas.center()
    assert qgis_canvas.scale() == pytest.approx(scale)
    assert (round(center.x()), round(center.y())) == (0, 0)


def test_loading_countries(
    globe: Globe, qgis_iface: "QgisInterface", qgis_canvas: "QgsMapCanvas"
):
    """Test loading data"""
    assert len(qgis_iface.getMockLayers()) == 0
    load_data(globe, load_countries=True)
    names = get_existing_layer_names(qgis_iface, qgis_canvas)
    assert "Countries" in names


def test_reloading_countries_after_intersecting_style(globe: Globe):
    load_data(
        globe,
        load_countries=True,
        intersecting_countries_color=QColor(Qt.GlobalColor.red),
    )
    load_data(globe, load_countries=True)
    layer = require_type(
        require(QgsProject.instance()).mapLayersByName("Countries")[0], QgsVectorLayer
    )
    renderer = require_type(layer.renderer(), QgsSingleSymbolRenderer)
    assert require(renderer.symbol()).color() == QColor(Qt.GlobalColor.blue)


@pytest.mark.skip("TODO: figure way to test processing")
def test_loading_graticules(
    globe: Globe, qgis_iface: "QgisInterface", qgis_canvas: "QgsMapCanvas"
):
    """Test loading data"""
    assert len(qgis_iface.getMockLayers()) == 0
    load_data(globe, load_graticules=True)
    names = get_existing_layer_names(qgis_iface, qgis_canvas)
    assert "Graticules" in names


@requires_s2cloudless
def test_loading_s2cloudless(
    globe: Globe, qgis_iface: "QgisInterface", qgis_canvas: "QgsMapCanvas"
):
    """Test loading data"""
    assert len(qgis_iface.getMockLayers()) == 0
    load_data(globe, load_s2=True)
    names = get_existing_layer_names(qgis_iface, qgis_canvas)
    assert "S2 Cloudless 2018" in names


@requires_s2cloudless
def test_loading_s2cloudless_countries_and_graticules(
    globe: Globe,
    qgis_iface: "QgisInterface",
    qgis_canvas: "QgsMapCanvas",
    qgis_processing: None,
):
    """Test loading data"""
    assert len(qgis_iface.getMockLayers()) == 0
    load_data(globe, load_s2=True, load_countries=True, load_graticules=True)
    names = get_existing_layer_names(qgis_iface, qgis_canvas)
    expected_names = {"Graticules", "S2 Cloudless 2018", "Countries"}
    assert names == expected_names


def test_background_color_changing(globe: Globe, qgis_canvas: "QgsMapCanvas"):
    """Test if background color really changes"""
    expected_b_color = QColor(Qt.GlobalColor.blue)
    globe.change_background_color(expected_b_color)
    new_background_color = qgis_canvas.canvasColor()
    assert new_background_color == expected_b_color


def test_adding_halo(
    globe: Globe, qgis_iface: "QgisInterface", qgis_canvas: "QgsMapCanvas"
):
    globe.add_halo(QColor(Qt.GlobalColor.blue), use_effects=True)
    names = get_existing_layer_names(qgis_iface, qgis_canvas)
    assert "Halo" in names


def test_ortho_halo_is_centered(globe: Globe):
    globe.set_origin({"lat": 60, "lon": 25})
    layer, _ = Halo(globe.origin, globe.projection).create_halo_layer(
        QColor(Qt.GlobalColor.blue), use_effects=False
    )
    center = next(layer.getFeatures()).geometry().centroid().asPoint()
    assert (round(center.x()), round(center.y())) == (0, 0)


def test_group(globe: Globe):
    group = globe.group
    children = require(require(QgsProject.instance()).layerTreeRoot()).children()
    assert group in children


def test_group_deletion(globe: Globe):
    group = globe.group
    globe.delete_group()
    children = require(require(QgsProject.instance()).layerTreeRoot()).children()
    assert group not in children


@pytest.mark.skip("TODO: figure way to test processing")
def test_theme_exist_if_items_in_group(globe: Globe):
    load_data(globe, load_graticules=True)
    globe.refresh_theme()
    assert (
        Globe.THEME_NAME
        in require(require(QgsProject.instance()).mapThemeCollection()).mapThemes()
    )


def test_theme_doesnt_exist_group_is_empty(globe: Globe):
    globe.refresh_theme()
    assert (
        Globe.THEME_NAME
        not in require(require(QgsProject.instance()).mapThemeCollection()).mapThemes()
    )


def get_existing_layer_names(
    qgis_iface: "QgisInterface", qgis_canvas: "QgsMapCanvas"
) -> set[str]:
    return {layer.name() for layer in qgis_iface.getMockLayers() + qgis_canvas.layers()}
