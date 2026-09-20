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


import typing

from qgis.utils import plugins

from globe_builder.utils import i18n_utils

if typing.TYPE_CHECKING:
    from qgis.PyQt import QtCore

    from globe_builder.plugin import Plugin

TRANSLATORS: "list[QtCore.QTranslator]" = []


def classFactory(_) -> "Plugin":  # noqa: ANN001, N802
    """Class factory."""
    TRANSLATORS.extend(i18n_utils.setup_all_translators())

    from globe_builder.plugin import Plugin  # noqa: PLC0415

    return Plugin()


def get_instance() -> "Plugin | None":
    """Get instance."""
    return plugins.get(__name__)
