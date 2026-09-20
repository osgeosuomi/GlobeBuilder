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
