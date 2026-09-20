from typing import TYPE_CHECKING

import pytest
from qgis.PyQt.QtWidgets import QMessageBox

from globe_builder import classFactory

if TYPE_CHECKING:
    from collections.abc import Iterator
    from unittest.mock import MagicMock

    from pytest_mock import MockerFixture
    from pytest_qgis import QgisInterface

    from globe_builder.plugin import Plugin


@pytest.fixture(autouse=True)
def mock_message_box_ok(mocker: "MockerFixture") -> "MagicMock":
    return mocker.patch.object(
        QMessageBox, "information", return_value=QMessageBox.StandardButton.Ok
    )


@pytest.fixture
def plugin_loaded(qgis_iface: "QgisInterface") -> "Iterator[Plugin]":
    plugin = classFactory(qgis_iface)
    plugin.initGui()

    yield plugin

    plugin.unload()


def test_plugin_loads_without_errors(
    mock_message_box_ok: "MagicMock", plugin_loaded: "Plugin"
) -> None:
    mock_message_box_ok.assert_called_once()

    # TODO: assert components initialized etc.
    # assert plugin_loaded.toolbar is not None
