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

import json
import logging
from typing import TYPE_CHECKING

from qgis.core import Qgis, QgsMessageLog
from qgis.PyQt.QtCore import QSettings, QUrl
from qgis.PyQt.QtNetwork import QNetworkAccessManager, QNetworkReply, QNetworkRequest
from qgis_plugin_tools.tools.resources import plugin_name

from globe_builder.definitions.settings import MAX_NAME_PARTS, NOMINATIM_URL

if TYPE_CHECKING:
    from collections.abc import Callable

LOGGER = logging.getLogger(plugin_name())

type Geolocations = dict[str, tuple[float, float]]
"""Display names mapped to (lon, lat) coordinates."""


class Geocoder:
    """Asynchronous geocoder using the Nominatim API."""

    # noinspection PyUnresolvedReferences
    def __init__(self, callback: "Callable[[Geolocations], None]") -> None:
        self.network_access_manager = QNetworkAccessManager()
        self.network_access_manager.finished.connect(self.on_search_response)
        self.callback = callback

    def geocode(self, query: str, max_results: int) -> None:
        """Send a geocoding request, results are passed to the callback."""
        params = {"query": query, "limit": max_results}
        url = NOMINATIM_URL.format(**params)

        # http://osgeo-org.1560.x6.nabble.com/QGIS-Developer-Do-we-have-a-User-Agent-string-for-QGIS-td5360740.html
        user_agent = QSettings().value("/qgis/networkAndProxy/userAgent", "Mozilla/5.0")
        user_agent += " " if len(user_agent) else ""
        # noinspection PyUnresolvedReferences
        user_agent += f"QGIS/{Qgis.QGIS_VERSION_INT}"
        user_agent += " GlobeBuilder-plugin"

        QgsMessageLog.logMessage(url, "GlobeBuilder", Qgis.MessageLevel.Info)
        geocoding_request = QNetworkRequest(QUrl(url))
        # https://www.riverbankcomputing.com/pipermail/pyqt/2016-May/037514.html
        geocoding_request.setRawHeader(b"User-Agent", bytes(user_agent, "utf-8"))
        self.network_access_manager.get(geocoding_request)

    def on_search_response(self, search_result: QNetworkReply) -> None:
        """Parse the response and pass the results to the callback."""
        error = search_result.error()
        result_dict: Geolocations = {}
        if error == QNetworkReply.NetworkError.NoError:
            bytes_string = search_result.readAll()
            data_string = str(bytes_string, "utf-8")

            result = json.loads(data_string)

            for f in result["features"]:
                name_parts = f["properties"]["display_name"].split(",")
                name = (
                    "{} ({})".format(
                        ",".join(
                            name_parts[0 : min(MAX_NAME_PARTS, len(name_parts) - 1)]
                        ),
                        name_parts[-1].strip(),
                    )
                    if len(name_parts) > 1
                    else name_parts[0]
                )
                coordinates = f["geometry"]["coordinates"]
                result_dict[name] = (coordinates[0], coordinates[1])
        else:
            LOGGER.warning(str(error))
            LOGGER.warning(search_result.errorString())

        self.callback(result_dict)
