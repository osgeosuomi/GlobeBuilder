# coding=utf-8


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
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from qgis.core import QgsProject, QgsProcessingException, Qgis

from globe_builder.core.globe import Globe
from globe_builder.definitions.projections import Projections
from globe_builder.definitions.settings import (DEFAULT_ORIGIN)


def test_projection_change_with_default_origin(globe):
    """Test if projection really changes"""
    globe.set_projection(Projections.AZIMUTHAL_ORTHOGRAPHIC)
    globe.change_project_projection()
    expeted_proj = Projections.AZIMUTHAL_ORTHOGRAPHIC.value.proj_str(DEFAULT_ORIGIN)
    assert QgsProject.instance().crs().toProj() == expeted_proj


def test_projection_change_with_custom_origin(globe):
    """Test if projection really changes"""
    custom_origin = {'lat': 10, 'lon': 10}
    globe.set_origin(custom_origin)
    globe.change_project_projection()
    expeted_proj = Projections.AZIMUTHAL_ORTHOGRAPHIC.value.proj_str(custom_origin)
    assert QgsProject.instance().crs().toProj() == expeted_proj


def test_loading_countries(globe, qgis_iface, qgis_canvas):
    """Test loading data"""
    assert len(qgis_iface.getMockLayers()) == 0
    globe.load_data(False, True, False, QColor(Qt.blue), QColor(Qt.blue), None, '50m', 10)
    names = get_existing_layer_names(qgis_iface, qgis_canvas)
    assert "Countries" in names


@pytest.mark.skip('TODO: figure way to test processing')
def test_loading_graticules(globe, qgis_iface, qgis_canvas):
    """Test loading data"""
    assert len(qgis_iface.getMockLayers()) == 0
    globe.load_data(False, False, True, QColor(Qt.blue), QColor(Qt.blue), None, '50m', 10)
    names = get_existing_layer_names(qgis_iface, qgis_canvas)
    assert "Graticules" in names


def test_loading_s2cloudless(globe, qgis_iface, qgis_canvas):
    """Test loading data"""
    assert len(qgis_iface.getMockLayers()) == 0
    globe.load_data(True, False, False, QColor(Qt.blue), QColor(Qt.blue), None, '50m', 10)
    names = get_existing_layer_names(qgis_iface, qgis_canvas)
    assert "S2 Cloudless 2018" in names


def test_loading_s2cloudless_countries_and_graticules(globe, qgis_iface, qgis_canvas, qgis_processing):
    """Test loading data"""
    assert len(qgis_iface.getMockLayers()) == 0
    try:
        globe.load_data(True, True, True, QColor(Qt.blue), QColor(Qt.blue), None, '50m', 10)
        names = get_existing_layer_names(qgis_iface, qgis_canvas)
        expected_names = {"Graticules", "S2 Cloudless 2018", "Countries"}
        assert names == expected_names
    except QgsProcessingException:
        # In QGIS 3.10 docker image, the algorithm native:creategrid seems to be missing...
        if not Qgis.QGIS_VERSION.startswith("3.10"):
            raise


def test_background_color_changing(globe, qgis_canvas):
    """Test if background color really changes"""
    expected_b_color = QColor(Qt.blue)
    globe.change_background_color(expected_b_color)
    new_background_color = qgis_canvas.canvasColor()
    assert new_background_color == expected_b_color


def test_adding_halo(globe, qgis_iface, qgis_canvas):
    globe.add_halo(True, QColor(Qt.blue))
    names = get_existing_layer_names(qgis_iface, qgis_canvas)
    assert "Halo" in names


def test_group(globe):
    group = globe.group
    children = QgsProject.instance().layerTreeRoot().children()
    assert group in children


def test_group_deletion(globe):
    group = globe.group
    globe.delete_group()
    children = QgsProject.instance().layerTreeRoot().children()
    assert group not in children


@pytest.mark.skip('TODO: figure way to test processing')
def test_theme_exist_if_items_in_group(globe):
    globe.load_data(False, False, True, QColor(Qt.blue), QColor(Qt.blue), None, '50m', 10)
    globe.refresh_theme()
    assert Globe.THEME_NAME in QgsProject.instance().mapThemeCollection().mapThemes()


def test_theme_doesnt_exist_group_is_empty(globe):
    globe.refresh_theme()
    assert Globe.THEME_NAME not in QgsProject.instance().mapThemeCollection().mapThemes()


def get_existing_layer_names(qgis_iface, qgis_canvas):
    return {layer.name() for layer in qgis_iface.getMockLayers() + qgis_canvas.layers()}
