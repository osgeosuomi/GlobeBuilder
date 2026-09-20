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

# ruff: noqa: N815  # widget attribute names come from the .ui file

import logging
import typing

from qgis.core import QgsProject
from qgis.PyQt import QtWidgets
from qgis.PyQt.QtCore import pyqtSignal
from qgis.utils import iface as utils_iface
from qgis_plugin_tools.tools.custom_logging import bar_msg
from qgis_plugin_tools.tools.i18n import tr
from qgis_plugin_tools.tools.resources import load_ui, plugin_name
from qgis_plugin_tools.tools.settings import get_setting, set_setting
from qgis_plugin_tools.tools.version import proj_version

from globe_builder.core.globe import Globe
from globe_builder.core.utils.geocoder import Geocoder
from globe_builder.core.utils.utils import (
    create_layout,
    get_map_center_coordinates,
    transform_to_wgs84,
)
from globe_builder.definitions.projections import Projections
from globe_builder.definitions.settings import (
    DEFAULT_BACKGROUND_COLOR,
    DEFAULT_COUNTRIES_COLOR,
    DEFAULT_GRATICULES_COLOR,
    DEFAULT_HALO_COLOR,
    DEFAULT_HALO_FILL_COLOR,
    DEFAULT_INTERSECTING_COUNTRIES_COLOR,
    DEFAULT_LAYOUT_BACKGROUND_COLOR,
    DEFAULT_MAX_NUMBER_OF_RESULTS,
    DEFAULT_ORIGIN,
    DEFAULT_USE_NE_COUNTRIES,
    DEFAULT_USE_NE_GRATICULES,
    DEFAULT_USE_S2_CLOUDLESS,
)

if typing.TYPE_CHECKING:
    from qgis.gui import (
        QgisInterface,
        QgsCollapsibleGroupBox,
        QgsColorButton,
        QgsMapLayerComboBox,
    )
    from qgis.PyQt.QtGui import QCloseEvent, QColor

    from globe_builder.core.utils.geocoder import Geolocations
    from globe_builder.definitions.settings import Origin

FORM_CLASS: type = load_ui("globe_builder_dockwidget_base.ui")
LOGGER = logging.getLogger(plugin_name())

iface = typing.cast("QgisInterface", utils_iface)


class GlobeBuilderDockWidget(QtWidgets.QDockWidget, FORM_CLASS):  # type: ignore[misc, valid-type]
    """Dock widget for configuring and building the globe."""

    closingPlugin = pyqtSignal()

    # Widgets defined in the .ui file
    centeringGroupBox: "QgsCollapsibleGroupBox"
    checkBoxCountries: QtWidgets.QCheckBox
    checkBoxGraticules: QtWidgets.QCheckBox
    checkBoxIntCountries: QtWidgets.QCheckBox
    checkBoxS2cloudless: QtWidgets.QCheckBox
    comboBoxCountries: QtWidgets.QComboBox
    comboBoxGraticules: QtWidgets.QComboBox
    comboBoxLayouts: QtWidgets.QComboBox
    comboBoxProjections: QtWidgets.QComboBox
    lineEditGeocoding: QtWidgets.QLineEdit
    lineEditLonLat: QtWidgets.QLineEdit
    listWidgetGeocodingResults: QtWidgets.QListWidget
    mColorButtonBackground: "QgsColorButton"
    mColorButtonCountries: "QgsColorButton"
    mColorButtonGraticules: "QgsColorButton"
    mColorButtonHalo: "QgsColorButton"
    mColorButtonHFill: "QgsColorButton"
    mColorButtonIntCountries: "QgsColorButton"
    mColorButtonLayoutBackground: "QgsColorButton"
    mMapLayerComboBox: "QgsMapLayerComboBox"
    pushButtonAddToLayout: QtWidgets.QPushButton
    pushButtonApplyVisualizations: QtWidgets.QPushButton
    pushButtonRun: QtWidgets.QPushButton
    pushButtonSearch: QtWidgets.QPushButton
    radioButtonCenter: QtWidgets.QRadioButton
    radioButtonCoordinates: QtWidgets.QRadioButton
    radioButtonGeocoding: QtWidgets.QRadioButton
    radioButtonHFill: QtWidgets.QRadioButton
    radioButtonHFillWithHalo: QtWidgets.QRadioButton
    radioButtonHHalo: QtWidgets.QRadioButton
    radioButtonHOutline: QtWidgets.QRadioButton
    radioButtonLayer: QtWidgets.QRadioButton
    spinBoxGlobeSize: QtWidgets.QSpinBox
    spinBoxMaxResults: QtWidgets.QSpinBox

    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)

        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>
        self.setupUi(self)

        # noinspection PyArgumentList
        self.qgis_instance = QgsProject.instance()
        self.layout_manager = self.qgis_instance.layoutManager()
        self.globe = Globe()
        self.geocoder = Geocoder(self._on_geocoding_finished)

        # Set default values
        self.spinBoxMaxResults.setValue(
            get_setting("maxNumberOfResults", DEFAULT_MAX_NUMBER_OF_RESULTS, int)
        )
        self.checkBoxCountries.setChecked(
            get_setting("useNE-countries", DEFAULT_USE_NE_COUNTRIES, bool)
        )
        self.checkBoxGraticules.setChecked(
            get_setting("useNE-graticules", DEFAULT_USE_NE_GRATICULES, bool)
        )
        self.checkBoxS2cloudless.setChecked(
            get_setting("useS2cloudless", DEFAULT_USE_S2_CLOUDLESS, bool)
        )

        self.lineEditLonLat.setText("{lon}, {lat}".format(**DEFAULT_ORIGIN))
        self._on_coordinates_toggled(self.radioButtonCoordinates.isChecked())
        self._on_layer_toggled(self.radioButtonLayer.isChecked())
        self._on_geocoding_toggled(self.radioButtonGeocoding.isChecked())
        self._on_halo_fill_toggled()
        self._on_intersecting_countries_changed()

        self._populate_layouts()
        self._populate_projections()

        self.mColorButtonBackground.setColor(DEFAULT_BACKGROUND_COLOR)
        self.mColorButtonHalo.setColor(DEFAULT_HALO_COLOR)
        self.mColorButtonHFill.setColor(DEFAULT_HALO_FILL_COLOR)
        self.mColorButtonLayoutBackground.setColor(DEFAULT_LAYOUT_BACKGROUND_COLOR)
        self.mColorButtonCountries.setColor(DEFAULT_COUNTRIES_COLOR)
        self.mColorButtonGraticules.setColor(DEFAULT_GRATICULES_COLOR)
        self.mColorButtonIntCountries.setColor(DEFAULT_INTERSECTING_COUNTRIES_COLOR)

        self.geolocations: Geolocations = {}
        self.old_coordinates: Origin | None = DEFAULT_ORIGIN
        self.old_projection = Projections.proj_from_id(
            self.comboBoxProjections.currentText()
        )

        # connections
        self.radioButtonCoordinates.toggled.connect(self._on_coordinates_toggled)
        self.radioButtonLayer.toggled.connect(self._on_layer_toggled)
        self.radioButtonGeocoding.toggled.connect(self._on_geocoding_toggled)
        self.radioButtonHFill.toggled.connect(self._on_halo_fill_toggled)
        self.radioButtonHFillWithHalo.toggled.connect(self._on_halo_fill_toggled)
        self.spinBoxMaxResults.valueChanged.connect(self._on_max_results_changed)
        self.checkBoxCountries.stateChanged.connect(self._on_countries_changed)
        self.checkBoxGraticules.stateChanged.connect(self._on_graticules_changed)
        self.checkBoxS2cloudless.stateChanged.connect(self._on_s2cloudless_changed)
        self.checkBoxIntCountries.stateChanged.connect(
            self._on_intersecting_countries_changed
        )
        self.pushButtonSearch.clicked.connect(self._on_search_clicked)
        self.pushButtonApplyVisualizations.clicked.connect(
            self._on_apply_visualizations_clicked
        )
        self.pushButtonRun.clicked.connect(self._on_run_clicked)
        self.pushButtonAddToLayout.clicked.connect(self._on_add_to_layout_clicked)
        self.layout_manager.layoutAdded.connect(self._populate_layouts)
        self.layout_manager.layoutRemoved.connect(self._populate_layouts)
        self.layout_manager.layoutRenamed.connect(self._populate_layouts)
        self.comboBoxProjections.currentTextChanged.connect(self._projection_changed)

    def closeEvent(self, event: "QCloseEvent") -> None:  # noqa: N802
        """Emit closingPlugin signal when the widget is closed."""
        # noinspection PyUnresolvedReferences
        self.closingPlugin.emit()
        event.accept()

    def _on_coordinates_toggled(self, is_checked: bool) -> None:  # noqa: FBT001
        self.lineEditLonLat.setEnabled(is_checked)

    def _on_layer_toggled(self, is_checked: bool) -> None:  # noqa: FBT001
        self.mMapLayerComboBox.setEnabled(is_checked)

    def _on_geocoding_toggled(self, is_checked: bool) -> None:  # noqa: FBT001
        self.lineEditGeocoding.setEnabled(is_checked)
        self.pushButtonSearch.setEnabled(is_checked)
        self.listWidgetGeocodingResults.setEnabled(is_checked)
        self.spinBoxMaxResults.setEnabled(is_checked)

    def _on_halo_fill_toggled(self) -> None:
        self.mColorButtonHFill.setEnabled(
            self.radioButtonHFill.isChecked()
            or self.radioButtonHFillWithHalo.isChecked()
        )

    def _on_max_results_changed(self, value: int) -> None:
        set_setting("maxNumberOfResults", value)

    def _on_countries_changed(self) -> None:
        set_setting("useNE-countries", self.checkBoxCountries.isChecked())

    def _on_graticules_changed(self) -> None:
        set_setting("useNE-graticules", self.checkBoxGraticules.isChecked())

    def _on_s2cloudless_changed(self) -> None:
        set_setting("useS2cloudless", self.checkBoxS2cloudless.isChecked())

    def _on_intersecting_countries_changed(self) -> None:
        set_setting("intCountries", self.checkBoxIntCountries.isChecked())
        self.mColorButtonIntCountries.setEnabled(self.checkBoxIntCountries.isChecked())

    def _on_search_clicked(self) -> None:
        text = self.lineEditGeocoding.text()
        if text.strip():
            self.listWidgetGeocodingResults.clear()
            self.geolocations.clear()
            self.geocoder.geocode(text, self.spinBoxMaxResults.value())

    def _on_apply_visualizations_clicked(self) -> None:
        coordinates = self._calculate_origin_coordinates()
        if coordinates != self.old_coordinates:
            self.old_coordinates = coordinates
            self.globe.set_origin(coordinates)
        projection = Projections.proj_from_id(self.comboBoxProjections.currentText())
        if projection is not None and projection != self.old_projection:
            self.old_projection = projection
            self.globe.set_projection(projection)
            self.globe.change_project_projection()
        self._load_data_to_globe()
        self.globe.change_background_color(self.mColorButtonBackground.color())
        self.mColorButtonBackground.setColor(iface.mapCanvas().canvasColor())
        self.globe.set_group_visibility(is_visible=True)
        self._add_halo_to_globe()

    def _on_run_clicked(self) -> None:
        self._load_data_to_globe(possibly_use_intersecting_colors=False)
        self.old_coordinates = self._calculate_origin_coordinates()
        self.globe.set_origin(self.old_coordinates)
        self.old_projection = Projections.proj_from_id(
            self.comboBoxProjections.currentText()
        )
        if self.old_projection is not None:
            self.globe.set_projection(self.old_projection)
        self.globe.change_background_color(self.mColorButtonBackground.color())
        self.mColorButtonBackground.setColor(iface.mapCanvas().canvasColor())
        self.globe.change_project_projection()
        self.globe.set_group_visibility(is_visible=True)
        self._add_halo_to_globe()

    def _on_add_to_layout_clicked(self) -> None:
        selected_layouts = [
            layout
            for layout in self.layout_manager.printLayouts()
            if layout.name() == self.comboBoxLayouts.currentText()
        ]
        layout = (
            selected_layouts[0]
            if len(selected_layouts) == 1
            else create_layout("LayoutGlobe", self.qgis_instance)
        )
        crs = self.qgis_instance.crs()

        # For some reason layout mode can't handle azimuthal orthographic projection
        # with any decimals and the projection needs to be set to project level
        # before attempting to use it in a layout
        coordinates = self._calculate_origin_coordinates()
        if coordinates is not None:
            self.globe.set_origin(
                {key: float(f"{val:.0f}") for key, val in coordinates.items()}
            )
        projection = Projections.proj_from_id(self.comboBoxProjections.currentText())
        if projection is not None:
            self.globe.set_projection(projection)
        self.globe.change_temporarily_to_globe_projection()
        self.globe.delete_group()
        self._load_data_to_globe()

        self._add_halo_to_globe()
        self.globe.set_group_visibility(is_visible=False)
        self.globe.refresh_theme()
        self.globe.add_to_layout(
            layout,
            background_color=self.mColorButtonLayoutBackground.color(),
            size=self.spinBoxGlobeSize.value(),
        )

        self.qgis_instance.setCrs(crs)

    def _populate_layouts(self) -> None:
        self.comboBoxLayouts.clear()
        self.comboBoxLayouts.addItem(tr("Create new layout (LayoutGlobe)"))
        for layout in self.layout_manager.layouts():
            self.comboBoxLayouts.addItem(layout.name())

    def _populate_projections(self) -> None:
        try:
            proj_v = proj_version()
        except AttributeError:
            proj_v = (0, 0)
        self.comboBoxProjections.clear()
        for projection in Projections:
            if proj_v >= projection.value.min_proj:
                self.comboBoxProjections.addItem(projection.value.name)

    def _add_halo_to_globe(self) -> None:
        self.globe.add_halo(
            self.mColorButtonHalo.color(),
            self._get_halo_fill_color(),
            use_effects=self.radioButtonHHalo.isChecked(),
            halo_with_fill=self.radioButtonHFillWithHalo.isChecked(),
        )
        self.globe.refresh_theme()

    def _get_halo_fill_color(self) -> "QColor | None":
        return (
            self.mColorButtonHFill.color()
            if (
                self.radioButtonHFill.isChecked()
                or self.radioButtonHFillWithHalo.isChecked()
            )
            else None
        )

    def _get_intersecting_countries_color(self) -> "QColor | None":
        return (
            self.mColorButtonIntCountries.color()
            if self.checkBoxIntCountries.isChecked()
            else None
        )

    def _on_geocoding_finished(self, geolocations: "Geolocations") -> None:
        self.geolocations = geolocations.copy()
        for name in self.geolocations:
            self.listWidgetGeocodingResults.addItem(name)

    def _load_data_to_globe(
        self, *, possibly_use_intersecting_colors: bool = True
    ) -> None:
        self.globe.load_data(
            load_s2=self.checkBoxS2cloudless.isChecked(),
            load_countries=self.checkBoxCountries.isChecked(),
            load_graticules=self.checkBoxGraticules.isChecked(),
            countries_color=self.mColorButtonCountries.color(),
            graticules_color=self.mColorButtonGraticules.color(),
            intersecting_countries_color=self._get_intersecting_countries_color()
            if possibly_use_intersecting_colors
            else None,
            countries_resolution=self.comboBoxCountries.currentText().split(" ")[-1],
            graticules_resolution=int(
                self.comboBoxGraticules.currentText().split(" ")[-1]
            ),
        )

    def _get_geocoded_coordinates(self) -> "Origin | None":
        current_item = self.listWidgetGeocodingResults.currentItem()
        if not self.geolocations or current_item is None:
            return None
        coordinates = self.geolocations.get(current_item.text())
        if coordinates is None:
            return None
        return {"lon": coordinates[0], "lat": coordinates[1]}

    def _calculate_origin_coordinates(self) -> "Origin | None":
        coordinates: Origin | None = None
        try:
            if self.radioButtonCoordinates.isChecked():
                lon, lat = (
                    float(c.strip()) for c in self.lineEditLonLat.text().split(",")
                )
                coordinates = {"lon": lon, "lat": lat}

            elif self.radioButtonGeocoding.isChecked():
                coordinates = self._get_geocoded_coordinates()
                if not coordinates:
                    raise ValueError(  # noqa: TRY301
                        tr("Make sure to select an item from the Geolocation list")
                    )

            elif self.radioButtonLayer.isChecked():
                layer = self.mMapLayerComboBox.currentLayer()
                if layer is None:
                    raise ValueError(  # noqa: TRY301
                        tr("Make sure to have at least one layer in the project")
                    )
                center_point = layer.extent().center()

                center_point = transform_to_wgs84(
                    center_point, layer.crs(), self.qgis_instance
                )
                coordinates = {"lon": center_point.x(), "lat": center_point.y()}

            elif self.radioButtonCenter.isChecked():
                coordinates = get_map_center_coordinates(self.qgis_instance)

        except ValueError as e:
            LOGGER.warning(
                tr("Error occurred while parsing center of the globe"),
                extra=bar_msg(f"{tr('Traceback')}: {e}", duration=6),
            )
        return coordinates

    def _projection_changed(self, projection_id: str) -> None:
        projection = Projections.proj_from_id(projection_id)
        # Centering is disabled due to rendering artifacts
        self.centeringGroupBox.setEnabled(
            projection == Projections.AZIMUTHAL_ORTHOGRAPHIC
        )
