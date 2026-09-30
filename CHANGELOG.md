# CHANGELOG

## Unreleased

### New features
* Add usability improvements

### Fixes
* Use correct nominatim url
* Always set project crs on apply and centre ortho halo
* Reset countries renderer when not using intersecting colors
* Preserve canvas scale and center on projection change

### Maintenance
* Improve tests
* Add QGS 4 support
* Drop Python 3.9 and QGIS < 3.40 support
* Adopt qgis-plugin-copier-template

## 0.6.0 - 2020-09-23

* More projections (might work depending on PROJ version)
* Fixed bug with changing origin of the globe
* Fixed rendering artefacts caused by graticules by generating those via processing algorithms
* Various bug fixes
* Use pytest and CI tests
* Automatic release process with [qgis-plugin-ci](https://github.com/opengisch/qgis-plugin-ci)

## 0.5.0 - 2020-02-11

* Possibility to add Globe to any layout
* More accurate countries and graticules
* Improved UI and customization
* Simple tests

## 0.4.0 - 2020-01-24

* Dockable window
* Visualization customization
* Option to center based on a layer
* Bug fixes

## 0.3.0 - 2020-01-17

* Rounder halo with default of 64 segments.
* New data sources: Sentinel-2 cloudless and Natural Earth 30 degree graticules

## 0.2.3 - 2020-01-15

* Initial release
