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

from qgis.PyQt import QtCore
from qgis_plugin_tools.tools import i18n


def setup_all_translators() -> list[QtCore.QTranslator]:
    """Initialize translators."""
    translators = []
    _, main_file_path = i18n.setup_translation()
    if main_file_path:
        main_translator = QtCore.QTranslator()
        main_translator.load(main_file_path)
        # noinspection PyCallByClass
        QtCore.QCoreApplication.installTranslator(main_translator)
        translators.append(main_translator)

    return translators
