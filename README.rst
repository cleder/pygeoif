Introduction
============

PyGeoIf provides a GeoJSON-like protocol for geo-spatial (GIS) vector data.

see https://gist.github.com/2217756

Other Python programs and packages that you may have heard of already
implement this protocol:

* ArcPy http://help.arcgis.com/en/arcgisdesktop/
* descartes https://bitbucket.org/sgillies/descartes/
* geojson http://pypi.python.org/pypi/geojson/
* PySAL http://pysal.geodacenter.org/
* Shapely https://github.com/Toblerity/Shapely
* pyshp https://pypi.python.org/pypi/pyshp

So when you want to write your own geospatilal library with support
for this protocol you may use pygeoif as a starting point and build
your functionality on top of it

You may think of pygeoif as a 'shapely ultralight' which lets you
construct geometries and perform **very** basic operations like
reading and writing geometries from/to WKT, constructing line strings
out of points, polygons from linear rings, multi polygons from
polygons, etc. It was inspired by shapely and implements the
geometries in a way that when you are familiar with shapely
you feel right at home with pygeoif

It was written to provide clean and python only geometries for
fastkml_

.. _fastkml: http://pypi.python.org/pypi/fastkml/

PyGeoIf is continually tested with *Travis CI*

.. image:: https://api.travis-ci.org/cleder/pygeoif.png
    :target: https://travis-ci.org/cleder/pygeoif

.. image:: https://coveralls.io/repos/cleder/pygeoif/badge.png?branch=master
    :target: https://coveralls.io/r/cleder/pygeoif?branch=master




Example
========


    >>> from pygeoif import geometry
    >>> p = geometry.Point(1,1)
    >>> p.__geo_interface__
    {'type': 'Point', 'coordinates': (1.0, 1.0)}
    >>> print p
    POINT (1.0 1.0)
    >>> p1 = geometry.Point(0,0)
    >>> l = geometry.LineString([p,p1])
    >>> l.bounds
    (0.0, 0.0, 1.0, 1.0)
    >>> dir(l)
    ['__class__', '__delattr__', '__dict__', '__doc__', '__format__',
    '__geo_interface__', '__getattribute__', '__hash__', '__init__',
    '__module__', '__new__', '__reduce__', '__reduce_ex__', '__repr__',
    '__setattr__', '__sizeof__', '__str__', '__subclasshook__',
    '__weakref__', '_coordinates', '_geoms', '_type', 'bounds', 'coords',
    'geom_type', 'geoms', 'to_wkt']
    >>> print l
    LINESTRING (1.0 1.0, 0.0 0.0)


You find more examples in the
`test_main.py <https://github.com/cleder/pygeoif/blob/master/pygeoif/test_main.py>`_
file which cover every aspect of pygeoif or in fastkml_.

Classes
========

All classes implement the attributes:

* __geo_interface__: as dicussed above
* geom_type: Returns a string specifying the Geometry Type of the object
* bounds: Returns a (minx, miny, maxx, maxy) tuple (float values) that bounds the object.
* wkt: Returns the 'Well Known Text' representation of the object


and the method:

* to_wkt which also prints the object


Point
-----
A zero dimensional feature

Attributes
~~~~~~~~~~~
x, y, z : float
    Coordinate values

Example
~~~~~~~~

      >>> p = Point(1.0, -1.0)
      >>> print p
      POINT (1.0000000000000000 -1.0000000000000000)
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

A closed one-dimensional feature comprising one or more line segments

A LinearRing that crosses itself or touches itself at a single point is
invalid and operations on it may fail.

A Linear Ring is self closing



Polygon
--------

A two-dimensional figure bounded by a linear ring

A polygon has a non-zero area. It may have one or more negative-space
"holes" which are also bounded by linear rings. If any rings cross each
other, the feature is invalid and operations on it may fail.

Attributes
~~~~~~~~~~~

exterior : LinearRing
    The ring which bounds the positive space of the polygon.
interiors : sequence
    A sequence of rings which bound all existing holes.


MultiPoint
----------
A collection of one or more points

Attributes
~~~~~~~~~~~

geoms : sequence
    A sequence of Points

MultiLineString
----------------
A collection of one or more line strings

A MultiLineString has non-zero length and zero area.

Attributes
~~~~~~~~~~~

geoms : sequence
    A sequence of LineStrings

MultiPolygon
-------------

A collection of one or more polygons

Attributes
~~~~~~~~~~~~~
geoms : sequence
    A sequence of `Polygon` instances


GeometryCollection
-------------------
A heterogenous collection of geometries (Points, LineStrings, LinearRings
and Polygons)

Attributes
~~~~~~~~~~~
geoms : sequence
    A sequence of geometry instances

Please note:
GEOMETRYCOLLECTION isn't supported by the Shapefile format.
And this sub-class isn't generally supported by ordinary GIS sw (viewers and so on).
So it's very rarely used in the real GIS professional world.

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

      >>> p = Point(1.0, -1.0)
      >>> props = {'Name': 'Sample Point', 'Other': 'Other Data'}
      >>> a = Feature(p, props)
      >>> a.properties
      {'Name': 'Sample Point', 'Other': 'Other Data'}
      >>> a.properties['Name']
      'Sample Point'

Functions
=========

as_shape
--------

Create a pygeoif feature from an object that provides the __geo_interface__


    >>> from shapely.geometry import Point
    >>> from pygeoif import geometry
    >>> geometry.as_shape(Point(0,0))
    <pygeoif.geometry.Point object at 0x...>


from_wkt
---------

Create a geometry from its WKT representation


    >>> p = geometry.from_wkt('POINT (0 1)')
    >>> print p
    POINT (0.0 1.0)


signed_area
------------

Return the signed area enclosed by a ring using the linear time
algorithm at http://www.cgafaq.info/wiki/Polygon_Area. A value >= 0
indicates a counter-clockwise oriented ring.

orient
-------

Returns a copy of the polygon with exterior in counter-clockwise and
interiors in clockwise orientation for sign=1.0 and the other way round
for sign=-1.0


mapping
-------

Returns the __geo_interface__ dictionary


Development
===========

Installation
------------

You can install PyGeoIf from pypi using pip::

    pip install pygeoif

Testing
-------

In order to provide a Travis-CI like testing of the PyGeoIf package during
development, you can use tox (``pip install tox``) to evaluate the tests on
all supported Python interpreters which you have installed on your system.

You can run the tests with ``tox --skip-missin-interpreters`` and are looking
for output similar to the following::

    ______________________________________________________ summary ______________________________________________________
    SKIPPED:  py26: InterpreterNotFound: python2.6
      py27: commands succeeded
    SKIPPED:  py32: InterpreterNotFound: python3.2
    SKIPPED:  py33: InterpreterNotFound: python3.3
      py34: commands succeeded
    SKIPPED:  pypy: InterpreterNotFound: pypy
    SKIPPED:  pypy3: InterpreterNotFound: pypy3
      congratulations :)

You are primarily looking for the ``congratulations :)`` line at the bottom,
signifying that the code is working as expected on all configurations
available.
