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

from qgis.PyQt.QtCore import QCoreApplication, Qt, QTranslator
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction
from qgis_plugin_tools.tools.custom_logging import setup_logger, teardown_logger
from qgis_plugin_tools.tools.i18n import setup_translation, tr
from qgis_plugin_tools.tools.resources import plugin_name, resources_path

import logging
import typing

import qgis_plugin_tools
from qgis.PyQt.QtWidgets import QMessageBox
from qgis.utils import iface as utils_iface
from qgis_plugin_tools.tools import custom_logging
from qgis_plugin_tools.tools.decorations import log_if_fails
from qgis_plugin_tools.tools.i18n import tr

import template_plugin
from template_plugin import env

if typing.TYPE_CHECKING:
    from qgis.gui import QgisInterface




from globe_builder.ui.globe_builder_dockwidget import GlobeBuilderDockWidget

LOGGER = logging.getLogger(__name__)

iface = typing.cast("QgisInterface", utils_iface)

class GlobeBuilder:
    """QGIS Plugin Implementation."""

    def __init__(self):
        self._teardown_loggers = lambda: None


        # Declare instance attributes
        self.actions = []
        self.menu = tr("&Globe Builder")

        # Check if plugin was started the first time in current QGIS session
        # Must be set in initGui() to survive plugin reloads
        self.pluginIsActive = False
        self.dockwidget = None


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None,
    ):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """
        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        # noinspection PyUnresolvedReferences
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            # Adds plugin icon to Plugins toolbar
            iface.addToolBarIcon(action)

        if add_to_menu:
            iface.addPluginToMenu(self.menu, action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""
        global iface  # noqa: PLW0602

        self._teardown_loggers = custom_logging.setup_loggers(
            template_plugin.__name__,
            qgis_plugin_tools.__name__,
            message_log_name=tr("Template Plugin"),
        )

        # noinspection PyTypeChecker
        self.add_action(
            resources_path("icon.png"),
            text=tr("Build Globe view"),
            callback=self.run,
            parent=iface.mainWindow(),
        )

        # will be set False in run()
        self.first_start = True

        if hasattr(iface, "initializationCompleted"):
            iface.initializationCompleted.connect(self.iface_initialization_completed)

        if bool(env.IS_DEVELOPMENT_MODE):
            self.iface_initialization_completed()

        LOGGER.info("Plugin initialized")


    def onClosePlugin(self):
        """Cleanup necessary items here when plugin dockwidget is closed"""
        # disconnects
        self.dockwidget.closingPlugin.disconnect(self.onClosePlugin)

        # remove this statement if dockwidget is to remain
        # for reuse if plugin is reopened
        # Commented next statement since it causes QGIS crashe
        # when closing the docked window:
        # self.dockwidget = None

        self.pluginIsActive = False

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            iface.removePluginMenu(tr("&Globe Builder"), action)
            iface.removeToolBarIcon(action)
        self._teardown_loggers()
        self._teardown_loggers = lambda: None

    @log_if_fails
    def iface_initialization_completed(self) -> None:
        """Run additional setup for the plugin.

        Executed after initializationCompleted signal is emitted.
        """
        LOGGER.debug("iface initialization completed")

    def run(self):
        """Run method that performs all the real work"""
        if not self.pluginIsActive:
            self.pluginIsActive = True

            # dockwidget may not exist if:
            #    first run of plugin
            #    removed on close (see self.onClosePlugin method)
            if self.dockwidget == None:
                # Create the dockwidget (after translation) and keep reference
                self.dockwidget = GlobeBuilderDockWidget(self.iface)

            # connect to provide cleanup on closing of dockwidget
            self.dockwidget.closingPlugin.connect(self.onClosePlugin)

            # show the dockwidget
            iface.addDockWidget(Qt.RightDockWidgetArea, self.dockwidget)
            self.dockwidget.show()
