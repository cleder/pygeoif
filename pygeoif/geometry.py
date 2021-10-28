# -*- coding: utf-8 -*-
#
#   Copyright (C) 2012 -2021  Christian Ledermann
#
#   This library is free software; you can redistribute it and/or
#   modify it under the terms of the GNU Lesser General Public
#   License as published by the Free Software Foundation; either
#   version 2.1 of the License, or (at your option) any later version.

#   This library is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#   Lesser General Public License for more details.

#   You should have received a copy of the GNU Lesser General Public License
#   along with this library; if not, write to the Free Software Foundation,
#   Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA
#
# file deepcode ignore inconsistent~equality: Python 3 only
"""Geometries in pure Python."""
import warnings
from itertools import chain
from typing import Iterable
from typing import Iterator
from typing import NoReturn
from typing import Optional
from typing import Sequence
from typing import Tuple
from typing import Union
from typing import cast

from pygeoif.exceptions import DimensionError
from pygeoif.functions import centroid
from pygeoif.functions import convex_hull
from pygeoif.functions import dedupe
from pygeoif.functions import signed_area
from pygeoif.types import Bounds
from pygeoif.types import GeoCollectionInterface
from pygeoif.types import GeoInterface
from pygeoif.types import GeoType
from pygeoif.types import LineType
from pygeoif.types import Point2D
from pygeoif.types import PointType
from pygeoif.types import PolygonType


class _Geometry:
    """Base Class for geometry objects."""

    def __str__(self) -> str:
        return self.wkt

    def __eq__(self, other: object) -> bool:
        try:
            return bool(
                self.__geo_interface__["type"]
                == other.__geo_interface__.get("type")  # type: ignore [attr-defined]
                and self.__geo_interface__["coordinates"]
                == other.__geo_interface__.get("coordinates"),  # type: ignore
            )
        except AttributeError:
            return False

    def __bool__(self) -> bool:
        return self.is_empty is False

    @property
    def bounds(self) -> Bounds:
        """Return the X-Y bounding box."""
        raise NotImplementedError("Must be implemented by subclass")

    @property
    def convex_hull(self) -> Optional[Union["Point", "LineString", "Polygon"]]:
        """
        Return the Convex Hull.

        Returns a representation of the smallest convex Polygon containing
        all the points in the object unless the number of points in the object
        is less than three.
        For two points, the convex hull collapses to a LineString;
        for 1, to a Point.
        """
        if self.has_z:
            warnings.warn(
                "The convex Hull will only return the projection "
                "to 2 dimensions xy coordinates",
            )
        hull = convex_hull(self._prepare_hull())
        if len(hull) == 0:
            return None
        if len(hull) == 1:
            return Point(*hull[0])
        if len(hull) == 2:
            return LineString(hull)
        return Polygon(hull)

    @property
    def geom_type(self) -> str:
        """Return a string specifying the Geometry Type of the object."""
        return self.__class__.__name__

    @property
    def has_z(self) -> Optional[bool]:
        """
        Return True if the geometry's coordinate sequence(s) have z values.

        Return None if the geometry is empty.
        """
        raise NotImplementedError("Must be implemented by subclass")

    @property
    def is_empty(self) -> bool:
        """Return if this geometry is empty."""
        raise NotImplementedError("Must be implemented by subclass")

    @property
    def wkt(self) -> str:
        """Return the Well Known Text representation of the object."""
        if self.is_empty:
            return f"{self._wkt_type} EMPTY"
        return f"{self._wkt_type}{self._wkt_inset}({self._wkt_coords})"

    @property
    def __geo_interface__(self) -> GeoInterface:
        raise NotImplementedError("Must be implemented by subclass")

    @property
    def _wkt_coords(self) -> str:
        raise NotImplementedError("Must be implemented by subclass")

    @property
    def _wkt_inset(self) -> str:
        """Return Z for 3 dimensional geometry or an empty string for 2 dimensions."""
        return ""

    @property
    def _wkt_type(self) -> str:
        """Return the WKT name of the geometry."""
        return self.__class__.__name__.upper()

    @classmethod
    def _check_dict(cls, geo_interface: GeoInterface) -> None:
        if geo_interface["type"] != cls.__name__:
            raise ValueError(
                f"You cannot assign {geo_interface['type']} to {cls.__name__}",
            )

    @classmethod
    def _from_dict(cls, geo_interface: GeoInterface) -> "_Geometry":
        cls._check_dict(geo_interface)
        raise NotImplementedError("Must be implemented by subclass")

    @classmethod
    def _from_interface(cls, obj: GeoType) -> "_Geometry":
        return cls._from_dict(obj.__geo_interface__)

    def _prepare_hull(self) -> Iterable[Point2D]:
        raise NotImplementedError("Must be implemented by subclass")


class Point(_Geometry):
    """
    A zero dimensional geometry.

    A point has zero length and zero area.

    Attributes
    ----------
    x, y, z : float
        Coordinate values

    Example
    -------

      >>> p = Point(1.0, -1.0)
      >>> print p
      POINT (1.0 -1.0)
      >>> p.y
      -1.0
      >>> p.x
      1.0
    """

    def __init__(self, x: float, y: float, z: Optional[float] = None) -> None:
        """
        Initialize a Point.

        Parameters
        ----------
        2 or 3 coordinate parameters: x, y, [z] : float
            Easting, northing, and elevation.
        """
        self._coordinates = cast(
            PointType,
            tuple(coordinate for coordinate in [x, y, z] if coordinate is not None),
        )

    def __repr__(self) -> str:
        """Return the representation."""
        return f"{self.geom_type}{self._coordinates}"

    @property
    def is_empty(self) -> bool:
        """
        Return if this geometry is empty.

        A Point is considered empty when it has less than 2 coordinates.
        """
        return len(self._coordinates) < 2

    @property
    def x(self) -> float:
        """Return x coordinate."""
        return self._coordinates[0]

    @property
    def y(self) -> float:
        """Return y coordinate."""
        return self._coordinates[1]

    @property
    def z(self) -> float:
        """Return z coordinate."""
        if len(self._coordinates) == 3:
            return self._coordinates[2]  # type: ignore [misc]
        raise DimensionError("This point has no z coordinate")  # pragma: no mutate

    @property
    def coords(self) -> Tuple[PointType]:
        """Return the geometry coordinates."""
        return (self._coordinates,)

    @property
    def bounds(self) -> Bounds:
        """Return the X-Y bounding box."""
        return self.x, self.y, self.x, self.y

    @property
    def has_z(self) -> bool:
        """Return True if the geometry's coordinate sequence(s) have z values."""
        return len(self._coordinates) == 3

    @property
    def _wkt_coords(self) -> str:
        return " ".join(str(coordinate) for coordinate in self._coordinates)

    @property
    def _wkt_inset(self) -> str:
        """Return Z for 3 dimensional geometry or an empty string for 2 dimensions."""
        if len(self._coordinates) == 3:
            return " Z "
        return " "

    @property
    def __geo_interface__(self) -> GeoInterface:
        """Return the geo interface."""
        return {
            "type": self.geom_type,
            "bbox": self.bounds,
            "coordinates": cast(PointType, tuple(self._coordinates)),
        }

    @classmethod
    def from_coordinates(cls, coordinates: Tuple[PointType]) -> "Point":
        """Construct a point from coordinates."""
        return cls(*coordinates[0])

    @classmethod
    def _from_dict(cls, geo_interface: GeoInterface) -> "Point":
        cls._check_dict(geo_interface)
        return cls(*geo_interface["coordinates"])

    def _prepare_hull(self) -> Iterable[Point2D]:
        return ((self.x, self.y),)


class LineString(_Geometry):
    """
    A one-dimensional figure comprising one or more line segments.

    A LineString has non-zero length and zero area. It may approximate a curve
    and need not be straight. Unlike a LinearRing, a LineString is not closed.

    Attributes
    ----------
    geoms : sequence
        A sequence of Points
    """

    def __init__(self, coordinates: LineType) -> None:
        """
        Initialize a Linestring.

        Parameters
        ----------
        coordinates : sequence
            A sequence of (x, y [,z]) numeric coordinate pairs or triples

        Example
        -------
        Create a line with two segments

          >>> a = LineString([(0, 0), (1, 0), (1, 1)])
        """
        self._geoms = self._set_geoms(coordinates)

    def __repr__(self) -> str:
        """Return the representation."""
        return f"{self.geom_type}({self.coords})"

    @property
    def geoms(self) -> Tuple[Point, ...]:
        """Return the underlying geometries."""
        return self._geoms

    @property
    def coords(self) -> LineType:
        """Return the geometry coordinates."""
        return tuple(point.coords[0] for point in self.geoms)

    @property
    def bounds(self) -> Bounds:
        """Return the X-Y bounding box."""
        xy = list(zip(*((p.x, p.y) for p in self._geoms)))
        return (
            min(xy[0]),
            min(xy[1]),
            max(xy[0]),
            max(xy[1]),
        )

    @property
    def is_empty(self) -> bool:
        """
        Return if this geometry is empty.

        A Linestring is considered empty when it has less than 2 points.
        """
        return len(self._geoms) < 2

    @property
    def has_z(self) -> Optional[bool]:
        """Return True if the geometry's coordinate sequence(s) have z values."""
        if not self.geoms:
            return None
        return self._geoms[0].has_z

    @property
    def maybe_valid(self) -> bool:
        """
        Check validity of the coordinates.

        Returns False if the coordinates colapse to a single Point.
        This only highlights obvious problems with this geometry.
        Even if this test passes the geometry may still be invalid.
        """
        return len({p.coords[0] for p in self._geoms}) > 1

    @property
    def _wkt_inset(self) -> str:
        return self.geoms[0]._wkt_inset

    @property
    def _wkt_coords(self) -> str:
        return ", ".join(point._wkt_coords for point in self.geoms)

    @property
    def __geo_interface__(self) -> GeoInterface:
        """Return the geo interface."""
        return {
            "type": self.geom_type,
            "bbox": self.bounds,
            "coordinates": self.coords,
        }

    @classmethod
    def from_coordinates(cls, coordinates: Tuple[PointType]) -> "LineString":
        """Construct a linestring from coordinates."""
        return cls(coordinates)

    @classmethod
    def from_points(cls, *args: Point) -> "LineString":
        """Create a linestring from points."""
        return cls(tuple(point.coords[0] for point in args))

    @classmethod
    def _from_dict(cls, geo_interface: GeoInterface) -> "LineString":
        cls._check_dict(geo_interface)
        return cls(cast(LineType, geo_interface["coordinates"]))

    @staticmethod
    def _set_geoms(coordinates: LineType) -> Tuple[Point, ...]:
        geoms = []
        last_len = None
        for coord in dedupe(coordinates):
            if len(coord) != last_len and last_len is not None:
                raise DimensionError(
                    "All coordinates must have the same dimension",
                )
            last_len = len(coord)
            point = Point(*coord)
            if not point.is_empty:
                geoms.append(point)
        return tuple(geoms)

    def _prepare_hull(self) -> Iterable[Point2D]:
        return ((pt.x, pt.y) for pt in self._geoms)


class LinearRing(LineString):
    """
    A closed one-dimensional geometry comprising one or more line segments.

    A LinearRing that crosses itself or touches itself at a single point is
    invalid and operations on it may fail.

    A Linear Ring is self closing
    """

    def __init__(self, coordinates: LineType) -> None:
        """
        Initialize a LinearRing.

        Args:
            coordinates (Sequence):
                A sequence of (x, y [,z]) numeric coordinate pairs or triples
        """
        super().__init__(coordinates)
        if not self.is_empty and self._geoms[0].coords != self._geoms[-1].coords:
            self._geoms = self._geoms + (self._geoms[0],)

    @property
    def centroid(self) -> Optional[Point]:
        """Return the centroid of the ring."""
        if self.has_z:
            raise DimensionError("Centeroid is only implemented for 2D coordinates")
        try:
            cent, area = centroid(self.coords)
        except ZeroDivisionError:
            return None
        if abs(area - signed_area(self.coords)) > 0.000_001 * abs(area):
            return None
        return Point(cent[0], cent[1])

    @property
    def is_ccw(self) -> bool:
        """Return True if the ring is oriented counter clock-wise."""
        return signed_area(self.coords) >= 0

    @property
    def maybe_valid(self) -> bool:
        """
        Check validity of the coordinates.

        This only highlights obvious problems with this geometry.
        Even if this test passes the geometry may still be invalid.
        """
        if self.has_z:
            raise DimensionError("Validation is only implemented for 2D coordinates")
        bbox = self.bounds
        if bbox[0] == bbox[2] or bbox[1] == bbox[3]:
            return False
        try:
            _, area = centroid(self.coords)
        except ZeroDivisionError:
            return False
        return abs(area - signed_area(self.coords)) <= 0.000_001 * abs(area)


class Polygon(_Geometry):
    """
    A two-dimensional figure bounded by a linear ring.

    A polygon has a non-zero area. It may have one or more negative-space
    "holes" which are also bounded by linear rings. If any rings cross each
    other, the geometry is invalid and operations on it may fail.

    Attributes
    ----------
    exterior : LinearRing
        The ring which bounds the positive space of the polygon.
    interiors : sequence
        A sequence of rings which bound all existing holes.
    """

    def __init__(
        self,
        shell: LineType,
        holes: Optional[Sequence[LineType]] = None,
    ) -> None:
        """
        Initialize the polygon.

        Parameters
        ----------
        shell : sequence
            A sequence of (x, y [,z]) numeric coordinate pairs or triples
        holes : sequence
            A sequence of objects which satisfy the same requirements as the
            shell parameters above

        Example
        -------
        Create a square polygon with no holes

          >>> coords = ((0., 0.), (0., 1.), (1., 1.), (1., 0.), (0., 0.))
          >>> polygon = Polygon(coords)
        """
        self._interiors: Tuple[LinearRing, ...] = ()
        if holes:
            self._interiors = tuple(LinearRing(hole) for hole in holes)
        self._exterior = LinearRing(shell)

    def __repr__(self) -> str:
        """Return the representation."""
        return f"{self.geom_type}{self.coords}"

    @property
    def exterior(self) -> LinearRing:
        """Return the exterior Linear Ring of the polygon."""
        return self._exterior

    @property
    def interiors(self) -> Iterator[LinearRing]:
        """Interiors (Holes) of the polygon."""
        if self._interiors:
            yield from self._interiors

    @property
    def is_empty(self) -> bool:
        """
        Return if this geometry is empty.

        A polygon is empty when it does not have an exterior.
        """
        return self._exterior.is_empty

    @property
    def bounds(self) -> Bounds:
        """Return the X-Y bounding box."""
        return self.exterior.bounds

    @property
    def coords(self) -> PolygonType:
        """
        Return Coordinates of the Polygon.

        Note that this is not implemented in Shaply.
        """
        if self._interiors:
            return self.exterior.coords, tuple(i.coords for i in self.interiors)
        return (self.exterior.coords,)

    @property
    def has_z(self) -> Optional[bool]:
        """Return True if the geometry's coordinate sequence(s) have z values."""
        return self._exterior.has_z

    @property
    def maybe_valid(self) -> bool:
        """
        Check validity of the coordinates.

        This only highlights obvious problems with this geometry.
        Even if this test passes the geometry may still be invalid.
        """
        if not self._check_interior_bounds():
            return False
        if not self._exterior.maybe_valid:
            return False
        return all(interior.maybe_valid for interior in self.interiors)

    @property
    def _wkt_coords(self) -> str:
        ec = self.exterior._wkt_coords
        ic = "".join(f",({interior._wkt_coords})" for interior in self.interiors)
        return f"({ec}){ic}"

    @property
    def _wkt_inset(self) -> str:
        return self.exterior._wkt_inset

    @property
    def __geo_interface__(self) -> GeoInterface:
        """Return the geo interface."""
        coords = (self.exterior.coords,) + tuple(hole.coords for hole in self.interiors)
        return {
            "type": self.geom_type,
            "bbox": self.bounds,
            "coordinates": coords,
        }

    @classmethod
    def from_coordinates(cls, coordinates: PolygonType) -> "Polygon":
        """Construct a linestring from coordinates."""
        return cls(*coordinates)

    @classmethod
    def from_linear_rings(cls, shell: LinearRing, *args: LinearRing) -> "Polygon":
        """Construct a Polygon from linear rings."""
        return cls(shell.coords, tuple(lr.coords for lr in args))

    @classmethod
    def _from_dict(cls, geo_interface: GeoInterface) -> "Polygon":
        cls._check_dict(geo_interface)
        return cls(
            cast(LineType, geo_interface["coordinates"][0]),
            cast(Tuple[LineType], geo_interface["coordinates"][1:]),
        )

    def _check_interior_bounds(self) -> bool:
        """Check that the bounding boxes of holes are inside the bounds of the shell."""
        bounds = self.bounds
        for interior in self.interiors:
            i_box = interior.bounds
            if bounds[0] > i_box[0] or bounds[1] > i_box[1]:
                return False
            if bounds[2] < i_box[2] or bounds[3] < i_box[3]:
                return False
        return True

    def _prepare_hull(self) -> Iterable[Point2D]:
        return self.exterior._prepare_hull()


class _MultiGeometry(_Geometry):
    """
    Heterogeneous collections of geometric objects.

    The collection may be homogeneous (MultiPoint etc.) or heterogeneous.
    """

    @property
    def coords(self) -> NoReturn:
        """
        Raise a NotImplementedError.

        Multi-part geometries do not provide a coordinate sequence.
        """
        raise NotImplementedError(
            "Multi-part geometries do not provide a coordinate sequence",
        )

    @property
    def bounds(self) -> Bounds:
        """Return the X-Y bounding box."""
        geom_bounds = list(
            zip(*(geom.bounds for geom in self.geoms)),  # type: ignore [attr-defined]
        )
        return (
            min(geom_bounds[0]),
            min(geom_bounds[1]),
            max(geom_bounds[2]),
            max(geom_bounds[3]),
        )

    @property
    def has_z(self) -> Optional[bool]:
        """Return True if any geometry of the collection have z values."""
        if not self._geoms:  # type: ignore [attr-defined]
            return None
        return any(geom.has_z for geom in self.geoms)  # type: ignore [attr-defined]

    @property
    def is_empty(self) -> bool:
        """Return if collection is not empty and all its member are not empty."""
        return all(geom.is_empty for geom in self._geoms)  # type: ignore [attr-defined]


class MultiPoint(_MultiGeometry):
    """
    A collection of one or more points.

    Attributes
    ----------
    geoms : sequence
        A sequence of Points
    """

    def __init__(self, points: Sequence[PointType], unique: bool = False) -> None:
        """
        Create a collection of one or more points.

        Parameters
        ----------
        points : sequence
            A sequence of (x, y [,z]) numeric coordinate pairs or triples.
        unique: boolean,
            when unique is true duplicates will be removed,
            the ordering will not be preserved.

        Example
        -------
        Construct a 2 point collection

          >>> ob = MultiPoint([[0.0, 0.0], [1.0, 2.0]])
          >>> len(ob.geoms)
          2
          >>> type(ob.geoms[0]) == Point
          True
        """
        if unique:
            points = set(points)  # type: ignore [assignment]
        self._geoms = tuple(Point(*point) for point in points)

    def __len__(self) -> int:
        """Return the number of points in this MultiPoint."""
        return len(self._geoms)

    def __repr__(self) -> str:
        """Return the representation."""
        return f"{self.geom_type}({tuple(geom.coords[0] for geom in self._geoms)})"

    @property
    def geoms(self) -> Iterator[Point]:
        """Return a sequence of Points."""
        yield from self._geoms

    @property
    def _wkt_coords(self) -> str:
        return ", ".join(point._wkt_coords for point in self.geoms)

    @property
    def __geo_interface__(self) -> GeoInterface:
        """Return the geo interface."""
        return {
            "type": self.geom_type,
            "bbox": self.bounds,
            "coordinates": tuple(g.coords[0] for g in self._geoms),
        }

    @classmethod
    def from_points(cls, *args: Point, unique: bool = False) -> "MultiPoint":
        """Create a MultiPoint from Points."""
        return cls([point.coords[0] for point in args], unique=unique)

    @classmethod
    def _from_dict(cls, geo_interface: GeoInterface) -> "MultiPoint":
        cls._check_dict(geo_interface)
        return cls(cast(Sequence[PointType], geo_interface["coordinates"]))

    def _prepare_hull(self) -> Iterable[Point2D]:
        return ((pt.x, pt.y) for pt in self._geoms)


class MultiLineString(_MultiGeometry):
    """
    A collection of one or more line strings.

    A MultiLineString has non-zero length and zero area.

    Attributes
    ----------
    geoms : sequence
        A sequence of LineStrings
    """

    def __init__(self, lines: Sequence[LineType], unique: bool = False) -> None:
        """
        Initialize the MultiLineString.

        Parameters
        ----------
        lines : sequence
            A sequence of line-like coordinate sequences.
        unique: boolean,
            when unique is true duplicates will be removed,
            the ordering will not be preserved.

        Example
        -------
        Construct a collection containing one line string.

          >>> lines = MultiLineString( [[[0.0, 0.0], [1.0, 2.0]]] )
        """
        if unique:
            lines = {tuple(line) for line in lines}  # type: ignore [assignment]
        self._geoms = tuple(LineString(line) for line in lines)

    def __len__(self) -> int:
        """Return the number of lines in the collection."""
        return len(self._geoms)

    def __repr__(self) -> str:
        """Return the representation."""
        return f"{self.geom_type}({tuple(geom.coords for geom in self._geoms)})"

    @property
    def geoms(self) -> Iterator[LineString]:
        """Return the LineStrings in the collection."""
        yield from self._geoms

    @property
    def _wkt_coords(self) -> str:
        return ",".join(f"({linestring._wkt_coords})" for linestring in self.geoms)

    @property
    def __geo_interface__(self) -> GeoInterface:
        """Return the geo interface."""
        return {
            "type": self.geom_type,
            "bbox": self.bounds,
            "coordinates": tuple(tuple(g.coords) for g in self.geoms),
        }

    @classmethod
    def from_linestrings(
        cls,
        *args: LineString,
        unique: bool = False,
    ) -> "MultiLineString":
        """Create a MultiLineString from LineStrings."""
        return cls([line.coords for line in args], unique=unique)

    @classmethod
    def _from_dict(cls, geo_interface: GeoInterface) -> "MultiLineString":
        cls._check_dict(geo_interface)
        return cls(cast(Sequence[LineType], geo_interface["coordinates"]))

    def _prepare_hull(self) -> Iterable[Point2D]:
        return (
            (pt.x, pt.y)
            for pt in chain.from_iterable(line.geoms for line in self.geoms)
        )


class MultiPolygon(_MultiGeometry):
    """
    A collection of one or more polygons.

    If component polygons overlap the collection is `invalid` and some
    operations on it may fail.

    Attributes
    ----------
    geoms : sequence
        A sequence of `Polygon` instances
    """

    def __init__(self, polygons: Sequence[PolygonType], unique: bool = False) -> None:
        """
        Initialize a Multipolygon.

        Parameters
        ----------
        polygons : sequence
            A sequence of (shell, holes) tuples where shell is the sequence
            representation of a linear ring and holes is
            a sequence of such linear rings
        unique: boolean,
            when unique is true duplicates will be removed,
            the ordering will not be preserved.


        Example
        -------
        Construct a collection from a sequence of coordinate tuples

          >>> ob = MultiPolygon([
          ...     (
          ...     ((0.0, 0.0), (0.0, 1.0), (1.0, 1.0), (1.0, 0.0)),
          ...     [((0.1, 0.1), (0.1, 0.2), (0.2, 0.2), (0.2, 0.1))]
          ...)
          ...])
          >>> len(ob.geoms)
          1
          >>> type(ob.geoms[0]) == Polygon
          True
        """
        if unique:
            polygons = set(polygons)  # type: ignore [assignment]

        self._geoms = tuple(
            Polygon(
                polygon[0],
                polygon[1]  # type: ignore [misc] # noqa: IF100
                if len(polygon) == 2
                else None,
            )
            for polygon in polygons
        )

    def __len__(self) -> int:
        """Return the number of polygons in the collection."""
        return len(self._geoms)

    def __repr__(self) -> str:
        """Return the representation."""
        return f"{self.geom_type}({tuple(geom.coords for geom in self._geoms)})"

    @property
    def geoms(self) -> Iterator[Polygon]:
        """Return the Polygons in the collection."""
        yield from self._geoms

    @property
    def _wkt_coords(self) -> str:
        return ",".join(f"({poly._wkt_coords})" for poly in self.geoms)

    @property
    def __geo_interface__(self) -> GeoInterface:
        """Return the geo interface."""
        coords = tuple(
            (geom.exterior.coords,) + tuple(hole.coords for hole in geom.interiors)
            for geom in self.geoms
        )
        return {
            "type": self.geom_type,
            "bbox": self.bounds,
            "coordinates": coords,
        }

    @classmethod
    def from_polygons(cls, *args: Polygon, unique: bool = False) -> "MultiPolygon":
        """Create a MultiPolygon from Polygons."""
        return cls([poly.coords for poly in args], unique=unique)

    @classmethod
    def _from_dict(cls, geo_interface: GeoInterface) -> "MultiPolygon":
        cls._check_dict(geo_interface)
        coords = tuple(
            (poly[0], poly[1:])  # type: ignore [index]
            for poly in geo_interface["coordinates"]
        )
        return cls(cast(Sequence[PolygonType], coords))

    def _prepare_hull(self) -> Iterable[Point2D]:
        return (
            (pt.x, pt.y)
            for pt in chain.from_iterable(poly.exterior.geoms for poly in self.geoms)
        )


Geometry = Union[
    Point,
    LineString,
    LinearRing,
    Polygon,
    MultiPoint,
    MultiLineString,
    MultiPolygon,
]


class GeometryCollection(_MultiGeometry):
    """
    A heterogenous collection of geometries.

    Attributes
    ----------
    geoms : sequence
        A sequence of geometry instances

    Please note:
    GEOMETRYCOLLECTION isn't supported by the Shapefile format. And this sub-
    class isn't generally supported by ordinary GIS sw (viewers and so on). So
    it's very rarely used in the real GIS professional world.

    Example
    -------

    Initialize Geometries and construct a GeometryCollection

    >>> from pygeoif import geometry
    >>> p = geometry.Point(1.0, -1.0)
    >>> p2 = geometry.Point(1.0, -1.0)
    >>> geoms = [p, p2]
    >>> c = geometry.GeometryCollection(geoms)
    >>> c.__geo_interface__
    {'type': 'GeometryCollection',
    'geometries': [{'type': 'Point', 'coordinates': (1.0, -1.0)},
    {'type': 'Point', 'coordinates': (1.0, -1.0)}]}
    """

    def __init__(self, geometries: Iterable[Geometry]) -> None:
        """
        Initialize the MultiGeometry with Geometries.

        Args:
            geometries (Iterable[Geometry]
        """
        self._geoms = tuple(geom for geom in geometries if not geom.is_empty)

    def __eq__(self, other: object) -> bool:
        """
        Return equality between collections.

        Types and coordinates from all contained geometries must be equal.
        """
        try:
            if (
                other.__geo_interface__.get("type")  # type: ignore [attr-defined]
                != self.geom_type
            ):
                return False
            if len(
                other.__geo_interface__.get(  # type: ignore [attr-defined]
                    "geometries",
                    [],
                ),
            ) != len(
                self,
            ):
                return False
        except AttributeError:
            return False
        return all(
            (
                s["type"] == o.get("type") and s["coordinates"] == o.get("coordinates")
                for s, o in zip(
                    (geom.__geo_interface__ for geom in self._geoms),
                    other.__geo_interface__.get(  # type:  ignore [attr-defined]
                        "geometries",
                        [],
                    ),
                )
            ),
        )

    def __len__(self) -> int:
        """
        Length of the collection.

        Returns:
            int: Number of geometries in the collection.
        """
        return len(self._geoms)

    def __iter__(self) -> Iterable[Geometry]:
        """
        Iterate over the geometries of the collection.

        Returns:
            Iterable[Geometry]
        """
        return iter(self._geoms)

    def __repr__(self) -> str:
        """Return the representation."""
        return f"{self.geom_type}({tuple(self._geoms)})"

    @property
    def geoms(self) -> Iterator[Geometry]:
        """Iterate over the geometries."""
        yield from self._geoms

    @property
    def _wkt_coords(self) -> str:
        return ", ".join(geom.wkt for geom in self.geoms)

    @property
    def __geo_interface__(self) -> GeoCollectionInterface:  # type: ignore [override]
        """Return the geo interface of the collection."""
        return {
            "type": self.geom_type,
            "geometries": tuple(geom.__geo_interface__ for geom in self._geoms),
        }

    def _prepare_hull(self) -> Iterable[Point2D]:
        return chain.from_iterable(geom._prepare_hull() for geom in self.geoms)


__all__ = [
    "Geometry",
    "GeometryCollection",
    "LineString",
    "LinearRing",
    "MultiLineString",
    "MultiPoint",
    "MultiPolygon",
    "Point",
    "Polygon",
]
