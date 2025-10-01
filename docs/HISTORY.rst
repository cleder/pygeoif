Changelog
=========

1.7.0 (unreleased)
--------------------



1.6.0 (2025/10/01)
------------------

- drop Python 3.8 support
- add GraalPy to test matrix

1.5.1 (2024/12/05)
------------------

- expose ``force_2d`` and ``force_3d`` factories in the top-level module.
- fix WKT parsing for nested GeometryCollections.
- fix WKT output for MultiPoints.
- make hypothesis strategy for GeometryCollections recursive, so that it can generate
  nested collections.
- add Python 3.14 to test matrix.


1.5.0 (2024/05/11)
------------------

- fix handling of empty geometries.
- more hypothesis tests

1.4.0 (2024/03/25)
------------------

- add Hypothesis tests [Ben Shaver, Christian Ledermann]
- fix ``convex_hull`` edge-cases discovered by Hypothesis tests
- fix ``from_wkt`` to include multi geometries in GeometryCollections
- drop Python 3.7 support

1.3.0 (2024/02/05)
------------------

- add Python 3.13 to supported versions
- remove ``maybe_valid`` methods
- GeoType and GeoCollectionType protocols to use a property instead of an attribute

1.2.0 (2023/11/27)
------------------

- Geometries are now immutable (but not hashable)
- add ``force_2d`` and ``force_3d`` factories [Alex Svetkin]

1.1.1 (2023/10/27)
------------------

- Use ``pyproject.toml``, remove ``setup.py`` and ``MANIFEST.in``

1.1 (2023/10/13)
-----------------

- Fix nested MultiGeometries
- Improve type annotations
- Add Python 3.12 to supported versions
- Last version to support Python 3.7

1.0 (2022/09/29)
------------------------

- Add type annotations
- refactor
- changes to keep functionality and interface close to ``shapely``
- remove support for python 2
- minimum python version is 3.7
- rename ``as_shape`` to ``shape``
- add ``box`` factory
- format with black
- reconstruct objects from their representation
- Parse WKT that is not in upper case.
- Centroid for LinearRings
- Convex Hull
- implement equality ``__eq__`` operator (``==``)
- ``is_empty`` and ``bool``
- drop duplicate points when creating LineStrings

0.7 (2017/05/04)
-----------------

- fix broken multipolygon [mindflayer]
- add "bbox" to ``__geo_interface__`` output [jzmiller1]

0.6 (2015/08/04)
-----------------

- Add id to feature [jzmiller1]

0.5 (2015/07/13)
-----------------

- Add ``__iter__`` method to FeatureCollection and GeometryCollection [jzmiller1].
- add pypy and pypy3 and python 3.4 to travis.
- Add tox configuration for performing local testing [Ian Lee].
- Add Travis continuous deployment.

0.4 (2013/10/25)
-----------------

- after a year in production promote it to ``Development Status :: 5 - Production/Stable``
- MultiPolygons return tuples as the ``__geo_interface__``

0.3.1 (2012/11/15)
------------------

- specify minor python versions tested with Travis CI
- fix for signed area


0.3 (2012/11/14)
-------------------

- add GeometryCollection
- len(Multi*) and len(GeometryCollection) returns the number of contained Geometries
- add ``orient`` function to get clockwise or counterclockwise oriented polygons
- add ``signed_area`` function
- add ``_set_orientation`` method to lineStrings, Polygons and MultiPolygons


0.2.1 (2012/08/02)
-------------------

- ``as_shape`` also accepts an object that is neither a dictionary nor has a ``__geo_interface__``
  but can be converted into a ``__geo_interface__`` compliant dictionary


0.2 (2012/08/01)
-----------------

- change license to LGPL
- add wkt as a property
- ``as_shape`` also accepts a ``__geo_interface__`` compliant dictionary
- test with python3


0.1 (2012/07/27)
-----------------

- initial release
