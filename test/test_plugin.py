#  Copyright (C) 2026 GlobeBuilder contributors.
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

import pytest

from globe_builder import classFactory
from globe_builder.ui.globe_builder_dockwidget import GlobeBuilderDockWidget

if TYPE_CHECKING:
    from collections.abc import Iterator

    from pytest_qgis import QgisInterface

    from globe_builder.plugin import Plugin


@pytest.fixture
def plugin_loaded(qgis_iface: "QgisInterface") -> "Iterator[Plugin]":
    plugin = classFactory(qgis_iface)
    plugin.initGui()

    yield plugin

    plugin.unload()


def test_plugin_loads_without_errors(plugin_loaded: "Plugin") -> None:
    assert len(plugin_loaded.actions) == 1
    assert plugin_loaded.dockwidget is None


def test_plugin_run_shows_dockwidget(plugin_loaded: "Plugin") -> None:
    plugin_loaded.run()

    assert isinstance(plugin_loaded.dockwidget, GlobeBuilderDockWidget)
    assert plugin_loaded.plugin_is_active

    plugin_loaded.dockwidget.close()

    assert not plugin_loaded.plugin_is_active
