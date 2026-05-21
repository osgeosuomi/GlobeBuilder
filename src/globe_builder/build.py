#!/usr/bin/env python
# -*- coding: utf-8 -*-


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

import glob
from typing import List

from qgis_plugin_tools.infrastructure.plugin_maker import PluginMaker

"""
#################################################
# Edit the following to match the plugin
#################################################
"""

py_files = [
    fil
    for fil in glob.glob("**/*.py", recursive=True)
    if "test/" not in fil and "test\\" not in fil
]
locales = ["fi"]
profile = "dev"
ui_files = list(glob.glob("**/*.ui", recursive=True))
resources = list(glob.glob("**/*.qrc", recursive=True))
extra_dirs = ["resources"]
compiled_resources: List[str] = []

PluginMaker(
    py_files=py_files,
    ui_files=ui_files,
    resources=resources,
    extra_dirs=extra_dirs,
    compiled_resources=compiled_resources,
    locales=locales,
    profile=profile,
)
