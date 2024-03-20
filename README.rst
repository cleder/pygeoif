Introduction
============

.. inclusion-marker-do-not-remove

PyGeoIf provides a `GeoJSON-like protocol <https://gist.github.com/2217756>`_
for geo-spatial (GIS) vector data.

Other Python programs and packages that you may have heard of that
implement this protocol:

* `ArcPy <https://www.esri.com/about/newsroom/arcuser/geojson/>`_
* `descartes <https://docs.descarteslabs.com/>`_
* `PySAL <http://pysal.geodacenter.org/>`_
* `Shapely <https://github.com/Toblerity/Shapely>`_
* `pyshp <https://pypi.python.org/pypi/pyshp>`_
* `GeoPandas <https://geopandas.org/>`_
* `Karta <https://github.com/fortyninemaps/karta>`_
* `mapnik <https://github.com/mapnik/mapnik>`_

When you want to write your own geospatial library with support
for this protocol you may use pygeoif as a starting point and build
your functionality on top of it. It has no requirements outside the
Python standard library and is therefore easy to integrate into your
project. It is tested on `CPython <https://python.org>`_ and
`PyPy <https://www.pypy.org/>`_, but it should work on alternative
Python implementations (that implement the language specification *>=3.8*) as well.

You may think of pygeoif as a 'shapely ultralight' which lets you
construct geometries and perform **very** basic operations like
reading and writing geometries from/to WKT, constructing line strings
out of points, polygons from linear rings, multi polygons from
polygons, etc. It was inspired by shapely and implements the
geometries in a way that when you are familiar with pygeoif,
you will feel right at home with shapely or the other way round.

It was written to provide clean and python only geometries for fastkml_

.. image:: https://github.com/cleder/pygeoif/actions/workflows/run-all-tests.yml/badge.svg?branch=main
    :target: https://github.com/cleder/pygeoif/actions/workflows/run-all-tests.yml
    :alt: GitHub Actions

.. image:: https://readthedocs.org/projects/pygeoif/badge/?version=latest
    :target: https://pygeoif.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status

.. image:: https://codecov.io/gh/cleder/pygeoif/branch/main/graph/badge.svg?token=2EfiwBXs9X
    :target: https://codecov.io/gh/cleder/pygeoif
    :alt: Codecov

.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :target: https://github.com/psf/
    :alt: Black

.. image:: https://img.shields.io/badge/type%20checker-mypy-blue
    :target: http://mypy-lang.org/
    :alt: Mypy

.. image:: https://www.openhub.net/p/pygeoif/widgets/project_thin_badge.gif
    :target: https://www.openhub.net/p/pygeoif/
    :alt: Openhub

.. image:: https://www.codefactor.io/repository/github/cleder/pygeoif/badge/main
   :target: https://www.codefactor.io/repository/github/cleder/pygeoif/overview/main
   :alt: CodeFactor

.. image:: https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit
   :target: https://github.com/pre-commit/pre-commit
   :alt: pre-commit

.. image:: https://img.shields.io/pypi/pyversions/pygeoif.svg
    :target: https://pypi.python.org/pypi/pygeoif/
    :alt: Supported Python versions

.. image:: https://img.shields.io/pypi/implementation/pygeoif.svg
    :target: https://pypi.python.org/pypi/pygeoif/
    :alt: Supported Python implementations

.. image:: https://img.shields.io/pypi/v/pygeoif.svg
    :target: https://pypi.python.org/pypi/pygeoif/
    :alt: Latest Version

.. image:: https://img.shields.io/pypi/l/pygeoif.svg
    :target: https://pypi.python.org/pypi/pygeoif/
    :alt: License

.. image:: https://img.shields.io/pypi/dm/pygeoif.svg
    :target: https://pypi.python.org/pypi/pygeoif/
    :alt: Downloads

Installation
------------

You can install PyGeoIf from pypi using pip::

    pip install pygeoif


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
`tests <https://github.com/cleder/pygeoif/tree/main/tests>`_
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

Return the signed area enclosed by a ring.
A value >= 0 indicates a counter-clockwise oriented ring.


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

Clone this repository, create a virtualenv with Python 3.8 or later with
``python3 -m venv .venv`` and activate it with ``source .venv/bin/activate``.

Then install the requirements with ``pip install -e ".[dev]"``.

pre-commit
----------

Install the ``pre-commit`` hook with::

    pip install pre-commit
    pre-commit install

and check the code with::

    pre-commit run --all-files

Testing
-------

Run the unit and static tests with::

    pytest tests
    pytest --doctest-glob="README.rst"
    black pygeoif
    ruff pygeoif
    flake8 pygeoif
    mypy pygeoif



Acknowledgments
================

The tests were improved with mutmut_ which discovered some nasty edge cases.

.. _mutmut: https://github.com/boxed/mutmut
.. _GeoJSON: https://geojson.org/
.. _fastkml: http://pypi.python.org/pypi/fastkml/
