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

So when you want to write your own geospatilal library with support
for this protocol you may use pygeoif as a starting point and build
your functionality on top of it

You may think of pygeoif as a 'shapely ultralight' which lets you
construct geometries and perform _very_ basic operations like
reading and writing geometries from/to WKT, constructing line strings
out of points, polygons from linear rings, multi polygons from
polygons, etc. It was inspired by shapely and implements the
geometries in a way that when you are familiar with shapely
you feel right at home with pygeoif

It was written to provide clean and python only geometries for fastkml
http://pypi.python.org/pypi/fastkml/

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
    >>> dir (geometry)
    >>> dir(l)
    ['__class__', '__delattr__', '__dict__', '__doc__', '__format__',
    '__geo_interface__', '__getattribute__', '__hash__', '__init__',
    '__module__', '__new__', '__reduce__', '__reduce_ex__', '__repr__',
    '__setattr__', '__sizeof__', '__str__', '__subclasshook__',
    '__weakref__', '_coordinates', '_geoms', '_type', 'bounds', 'coords',
    'geom_type', 'geoms', 'to_wkt']
    >>> print l
    LINESTRING (1.0 1.0, 0.0 0.0)


You find more examples in the tests.py file which cover every aspect of
pygeoif.
https://github.com/cleder/pygeoif/blob/master/pygeoif/tests.py

Classes
========

All classes implement the attributes:

* __geo_interface__: as dicussed above
* geom_type: Returns a string specifying the Geometry Type of the object
* bounds: Returns a (minx, miny, maxx, maxy) tuple (float values) that bounds the object.


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


    >>> p = geometry.from_wkt('POINT (0.0 1.0)')
    >>> print p
    POINT (0.0 1.0)



