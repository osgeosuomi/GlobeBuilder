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
