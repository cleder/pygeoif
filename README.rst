Introduction
============

PyGeoIf provides a `GeoJSON-like protocol <https://gist.github.com/2217756>`_ for geo-spatial (GIS) vector data.

Other Python programs and packages that you may have heard of already
implement this protocol:

* `ArcPy <https://www.esri.com/about/newsroom/arcuser/geojson/>`_
* `descartes <https://docs.descarteslabs.com/>`_
* `PySAL <http://pysal.geodacenter.org/>`_
* `Shapely <https://github.com/Toblerity/Shapely>`_
* `pyshp <https://pypi.python.org/pypi/pyshp>`_

So when you want to write your own geospatial library with support
for this protocol you may use pygeoif as a starting point and build
your functionality on top of it

You may think of pygeoif as a 'shapely ultralight' which lets you
construct geometries and perform **very** basic operations like
reading and writing geometries from/to WKT, constructing line strings
out of points, polygons from linear rings, multi polygons from
polygons, etc. It was inspired by shapely and implements the
geometries in a way that when you are familiar with shapely
you feel right at home with pygeoif.

It was written to provide clean and python only geometries for fastkml_

.. image:: https://github.com/cleder/pygeoif/actions/workflows/run-all-tests.yml/badge.svg
    :target: https://github.com/cleder/pygeoif/actions/workflows/run-all-tests.yml

.. image:: https://codecov.io/gh/cleder/pygeoif/branch/main/graph/badge.svg?token=2EfiwBXs9X
    :target: https://codecov.io/gh/cleder/pygeoif

.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :target: https://github.com/psf/black

.. image:: https://img.shields.io/badge/type%20checker-mypy-blue
    :target: http://mypy-lang.org/

.. image:: https://www.openhub.net/p/pygeoif/widgets/project_thin_badge.gif
    :target: https://www.openhub.net/p/pygeoif/

Example
========

    >>> from pygeoif import geometry
    >>> p = geometry.Point(1,1)
    >>> p.__geo_interface__
    {'type': 'Point', 'bbox': (1, 1, 1, 1), 'coordinates': (1, 1)}
    >>> print(p)
    POINT (1 1)
    >>> p
    Point(1, 1)
    >>> l = geometry.LineString([(0.0, 0.0), (1.0, 1.0)])
    >>> l.bounds
    (0.0, 0.0, 1.0, 1.0)
    >>> print(l)
    LINESTRING (0.0 0.0, 1.0 1.0)


You find more examples in the
`tests <https://github.com/cleder/pygeoif/tree/main/pygeoif/tests>`_
directory which cover every aspect of pygeoif or in fastkml_.

Classes
========

All classes implement the attribute:

* ``__geo_interface__``: as discussed above, an interface to GeoJSON_.

All geometry classes implement the attributes:

* ``geom_type``: Returns a string specifying the Geometry Type of the object
* ``bounds``: Returns a (minx, miny, maxx, maxy) tuple that bounds the object.
* ``wkt``: Returns the 'Well Known Text' representation of the object

For two-dimensional geometries the following methods are implemented:

* ``convex_hull``: Returns a representation of the smallest convex Polygon containing
  all the points in the object unless the number of points in the object is less than three.
  For two points, the convex hull collapses to a LineString; for 1, a Point.
  For three dimensional objects only their projection in the xy plane is taken into consideration.
  Empty objects without coordinates return ``None`` for the convex_hull.


Point
-----
A zero dimensional geometry

A point has zero length and zero area. A point cannot be empty.

Attributes
~~~~~~~~~~~
x, y, z : float
    Coordinate values

Example
~~~~~~~~

      >>> from pygeoif import Point
      >>> p = Point(1.0, -1.0)
      >>> print(p)
      POINT (1.0 -1.0)
      >>> p.y
      -1.0
      >>> p.x
      1.0



LineString
-----------

A one-dimensional figure comprising one or more line segments

A LineString has non-zero length and zero area. It may approximate a curve
and need not be straight. Unlike a LinearRing, a LineString is not closed.

Attributes
~~~~~~~~~~~
geoms : sequence
    A sequence of Points

LinearRing
-----------

A closed one-dimensional geometry comprising one or more line segments

A LinearRing that crosses itself or touches itself at a single point is
invalid and operations on it may fail.

A LinearRing is self closing.


Polygon
--------

A two-dimensional figure bounded by a linear ring

A polygon has a non-zero area. It may have one or more negative-space
"holes" which are also bounded by linear rings. If any rings cross each
other, the geometry is invalid and operations on it may fail.

Attributes
~~~~~~~~~~~

exterior : LinearRing
    The ring which bounds the positive space of the polygon.
interiors : sequence
    A sequence of rings which bound all existing holes.
maybe_valid: boolean
    When a polygon has obvious problems such as self crossing
    lines or holes that are outside the exterior bounds this will
    return False. Even if this returns True the geometry may still be invalid,
    but if this returns False you do have a problem.

MultiPoint
----------
A collection of one or more points.

Attributes
~~~~~~~~~~~

geoms : sequence
    A sequence of Points.

MultiLineString
----------------
A collection of one or more line strings.

A MultiLineString has non-zero length and zero area.

Attributes
~~~~~~~~~~~

geoms : sequence
    A sequence of LineStrings

MultiPolygon
-------------

A collection of one or more polygons.

Attributes
~~~~~~~~~~~~~
geoms : sequence
    A sequence of `Polygon` instances


GeometryCollection
-------------------
A heterogenous collection of geometries (Points, LineStrings, LinearRings
and Polygons).

Attributes
~~~~~~~~~~~
geoms : sequence
    A sequence of geometry instances

Please note:
``GEOMETRYCOLLECTION`` isn't supported by the Shapefile or GeoJSON_ format.
And this sub-class isn't generally supported by ordinary GIS sw (viewers and so on).
So it's very rarely used in the real GIS professional world.

Example
~~~~~~~~

    >>> from pygeoif import geometry
    >>> p = geometry.Point(1.0, -1.0)
    >>> p2 = geometry.Point(1.0, -1.0)
    >>> geoms = [p, p2]
    >>> c = geometry.GeometryCollection(geoms)
    >>> [geom for geom in geoms]
    [Point(1.0, -1.0), Point(1.0, -1.0)]

Feature
-------
Aggregates a geometry instance with associated user-defined properties.

Attributes
~~~~~~~~~~~
geometry : object
    A geometry instance
properties : dict
    A dictionary linking field keys with values associated with with geometry instance

Example
~~~~~~~~
      >>> from pygeoif import Point, Feature
      >>> p = Point(1.0, -1.0)
      >>> props = {'Name': 'Sample Point', 'Other': 'Other Data'}
      >>> a = Feature(p, props)
      >>> a.properties
      {'Name': 'Sample Point', 'Other': 'Other Data'}
      >>> a.properties['Name']
      'Sample Point'

FeatureCollection
-----------------
A heterogenous collection of Features

Attributes
~~~~~~~~~~~
features: sequence
    A sequence of feature instances

Example
~~~~~~~~

    >>> from pygeoif import Point, Feature, FeatureCollection
    >>> p = Point(1.0, -1.0)
    >>> props = {'Name': 'Sample Point', 'Other': 'Other Data'}
    >>> a = Feature(p, props)
    >>> p2 = Point(1.0, -1.0)
    >>> props2 = {'Name': 'Sample Point2', 'Other': 'Other Data2'}
    >>> b = Feature(p2, props2)
    >>> features = [a, b]
    >>> c = FeatureCollection(features)
    >>> [feature for feature in c]
    [Feature(Point(1.0, -1.0), {'Name': 'Sample Point', 'Other': 'Other Data'},...]

Functions
=========

shape
--------

Create a pygeoif feature from an object that provides the ``__geo_interface__``
or any GeoJSON_ compatible dictionary.

    >>> from shapely.geometry import Point
    >>> from pygeoif import geometry, shape
    >>> shape(Point(0,0))
    Point(0.0, 0.0)


from_wkt
---------

Create a geometry from its WKT representation

    >>> from pygeoif import from_wkt
    >>> p = from_wkt('POINT (0 1)')
    >>> print(p)
    POINT (0.0 1.0)


signed_area
------------

Return the signed area enclosed by a ring using the linear time
algorithm at http://www.cgafaq.info/wiki/Polygon_Area. A value >= 0
indicates a counter-clockwise oriented ring.


orient
-------
Returns a copy of a polygon with exteriors and interiors in the right orientation.

if ccw is True than the exterior will be in counterclockwise orientation
and the interiors will be in clockwise orientation, or
the other way round when ccw is False.


box
---
Return a rectangular polygon with configurable normal vector.


mapping
-------

Return the ``__geo_interface__`` dictionary.


Development
===========

Installation
------------

You can install PyGeoIf from pypi using pip::

    pip install pygeoif

Testing
-------

Install the requirements with ``pip install -r test-requirements.txt``
and run the unit and static tests with::

    pytest pygeoif
    pytest --doctest-glob="README.rst"
    yesqa pygeoif/*.py
    black pygeoif
    flake8 pygeoif
    mypy pygeoif


Acknowledgments
================

The tests were improved with mutmut_ which discovered some nasty edge cases.

.. _mutmut: https://github.com/boxed/mutmut
.. _GeoJSON: https://geojson.org/
.. _fastkml: http://pypi.python.org/pypi/fastkml/
