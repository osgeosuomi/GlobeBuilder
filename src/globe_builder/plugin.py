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

import logging
import typing

import qgis_plugin_tools
from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction
from qgis.utils import iface as utils_iface
from qgis_plugin_tools.tools import custom_logging
from qgis_plugin_tools.tools.decorations import log_if_fails
from qgis_plugin_tools.tools.i18n import tr
from qgis_plugin_tools.tools.resources import resources_path

import globe_builder
from globe_builder import env
from globe_builder.ui.globe_builder_dockwidget import GlobeBuilderDockWidget

if typing.TYPE_CHECKING:
    from collections.abc import Callable

    from qgis.gui import QgisInterface
    from qgis.PyQt.QtWidgets import QWidget

LOGGER = logging.getLogger(__name__)

iface = typing.cast("QgisInterface", utils_iface)


class Plugin:
    """QGIS Plugin Implementation."""

    def __init__(self) -> None:
        self._teardown_loggers: Callable[[], None] = lambda: None

        # Declare instance attributes
        self.actions: list[QAction] = []
        self.menu = tr("&Globe Builder")

        # Check if plugin was started the first time in current QGIS session
        # Must be set in initGui() to survive plugin reloads
        self.plugin_is_active = False
        self.dockwidget: GlobeBuilderDockWidget | None = None

    def add_action(  # noqa: PLR0913
        self,
        icon_path: str,
        text: str,
        callback: "Callable[..., None]",
        *,
        enabled_flag: bool = True,
        add_to_menu: bool = True,
        add_to_toolbar: bool = True,
        status_tip: str | None = None,
        whats_this: str | None = None,
        parent: "QWidget | None" = None,
    ) -> QAction:
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.

        :param text: Text that should be shown in menu items for this action.

        :param callback: Function to be called when the action is triggered.

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.

        :param parent: Parent widget for the new action. Defaults None.

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
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

    def initGui(self) -> None:  # noqa: N802
        """Create the menu entries and toolbar icons inside the QGIS GUI."""
        self._teardown_loggers = custom_logging.setup_loggers(
            globe_builder.__name__,
            qgis_plugin_tools.__name__,
            message_log_name=tr("Globe Builder"),
        )

        # noinspection PyTypeChecker
        self.add_action(
            resources_path("icon.png"),
            text=tr("Build Globe view"),
            callback=self.run,
            parent=iface.mainWindow(),
        )

        if hasattr(iface, "initializationCompleted"):
            iface.initializationCompleted.connect(self.iface_initialization_completed)

        if bool(env.IS_DEVELOPMENT_MODE):
            self.iface_initialization_completed()

        LOGGER.info("Plugin initialized")

    def on_close_plugin(self) -> None:
        """Cleanup necessary items here when plugin dockwidget is closed."""
        # disconnects
        if self.dockwidget is not None:
            self.dockwidget.closingPlugin.disconnect(self.on_close_plugin)

        # The dockwidget is kept for reuse if plugin is reopened, since
        # setting it to None causes QGIS to crash when closing the docked window

        self.plugin_is_active = False

    def unload(self) -> None:
        """Remove the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            iface.removePluginMenu(self.menu, action)
            iface.removeToolBarIcon(action)
        self._teardown_loggers()
        self._teardown_loggers = lambda: None

    @log_if_fails
    def iface_initialization_completed(self) -> None:
        """Run additional setup for the plugin.

        Executed after initializationCompleted signal is emitted.
        """
        LOGGER.debug("iface initialization completed")

    def run(self) -> None:
        """Show the dock widget."""
        if self.plugin_is_active:
            return
        self.plugin_is_active = True

        # dockwidget may not exist if this is the first run of the plugin
        if self.dockwidget is None:
            # Create the dockwidget (after translation) and keep reference
            self.dockwidget = GlobeBuilderDockWidget()

        # connect to provide cleanup on closing of dockwidget
        self.dockwidget.closingPlugin.connect(self.on_close_plugin)

        # show the dockwidget
        iface.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.dockwidget)
        self.dockwidget.show()
