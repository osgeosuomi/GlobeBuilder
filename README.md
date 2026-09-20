# Globe Builder

![Tests](https://github.com/osgeosuomi/GlobeBuilder/workflows/Tests/badge.svg)
[![codecov.io](https://codecov.io/github/osgeosuomi/GlobeBuilder/coverage.svg?branch=master)](https://codecov.io/github/osgeosuomi/GlobeBuilder?branch=master)
![Release](https://github.com/osgeosuomi/GlobeBuilder/workflows/Release/badge.svg)
[![GPLv2 license](https://img.shields.io/badge/License-GPLv2-blue.svg)](https://www.gnu.org/licenses/old-licenses/gpl-2.0.en.html)

QGIS plugin that is meant for adding globe visualization to the current map using.

![Plugin in action](/images/screenshots/geocoding1.gif?raw=true "Plugin in action")

Inspired by these blog posts by

* [statsmapsnpix](http://www.statsmapsnpix.com/2019/09/globe-projections-and-insets-in-qgis.html)
* [Gispo](https://www.gispo.fi/en/blog/the-power-of-community-30daymapchallenge/)
* [gislounge](https://www.gislounge.com/how-to-use-the-equal-earth-projection-using-qgis-on-the-mac/)

The plugin is still in beta-development. Please report issues preferably to Issues.

Created by [Gispo Ltd.](https://www.gispo.fi/en/home/), maintained by [OSGeo Suomi](https://www.osgeo.fi/).

## Installation instructions

### QGIS Plugin

The plugin can be installed trough QGIS Plugins Repository. It can also be installed
by downloading a release from this repository:

1. Download the latest release zip from GitHub releases (above).

2. Launch QGIS and the plugins menu by selecting Plugins - Manage and Install Plugins
   from the top menu.

3. Select the Install from ZIP tab, browse to the zip file you just downloaded, and
   click Install Plugin!

## Usage

The Globe could be added either to the current map or to a layout.

![Plugin in layout mode](/images/screenshots/layout1.gif?raw=true "Plugin in layout mode")

## Gist

There is also a Github
[Gist](https://gist.github.com/Joonalai/7b8693ef904df75cb15cb9af0e82c032) that
provides the core functionality of the plugin. The usage can be seen in the
following gif.

![Gist in action](/images/screenshots/globe_view_gist.gif?raw=true "Gist in action")

## Development

Refer to [development instructions](DEVELOPMENT.md).

## Licence

This plugin is licenced with
[GNU General Public License, version 2](https://www.gnu.org/licenses/old-licenses/gpl-2.0.en.html).
This plugin uses
[OpenStreetMap Nominatim](https://wiki.openstreetmap.org/wiki/Nominatim) geocoding API.
The OpenStreetMap data is licensed under
[ODbL license](https://opendatacommons.org/licenses/odbl/).
This plugin lists Sentinel-2 cloudless as an optional data source. Sentinel-2
cloudless data by EOX IT Services GmbH (Contains modified Copernicus Sentinel data
2017 & 2018) released under
[Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License](https://creativecommons.org/licenses/by-nc-sa/4.0/).
For commercial usage of Sentinel-2 cloudless please see <https://cloudless.eox.at>.
