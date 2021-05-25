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
"""Geometries in pure Python."""
from typing import Generator
from typing import Iterable
from typing import NoReturn
from typing import Optional
from typing import Sequence
from typing import Tuple
from typing import Union
from typing import cast

from .types import Bounds
from .types import GeoCollectionInterface
from .types import GeoInterface
from .types import GeoType
from .types import LineType
from .types import PointType
from .types import PolygonType


class DimensionError(IndexError):
    """Geometries must have 2 or 3 dimensions."""


def signed_area(coords: LineType) -> float:
    """Return the signed area enclosed by a ring.

    Linear time algorithm: http://www.cgafaq.info/wiki/Polygon_Area.
    A value >= 0 indicates a counter-clockwise oriented ring.
    """
    if len(coords[0]) == 2:  # pragma: no mutate
        xs, ys = map(list, zip(*coords))
    elif len(coords[0]) == 3:  # pragma: no mutate
        xs, ys, _s = map(list, zip(*coords))
    xs.append(xs[1])  # pragma: no mutate
    ys.append(ys[1])  # pragma: no mutate
    return (
        sum(
            xs[i] * (ys[i + 1] - ys[i - 1])  # type: ignore
            for i in range(1, len(coords))
        )
        / 2.0
    )


class _Geometry:
    """Base Class for geometry objects."""

    def __str__(self) -> str:
        return self.wkt

    def __eq__(self, other: object) -> bool:
        if not hasattr(other, "__geo_interface__"):
            return False
        return bool(
            self.__geo_interface__["type"]
            == other.__geo_interface__.get("type")  # type: ignore
            and self.__geo_interface__["coordinates"]
            == other.__geo_interface__.get("coordinates"),  # type: ignore
        )

    @property
    def bounds(self) -> Bounds:
        """Return the X-Y bounding box."""
        raise NotImplementedError("Must be implemented by subclass")

    @property
    def geom_type(self) -> str:
        """Return a string specifying the Geometry Type of the object."""
        return self.__class__.__name__

    @property
    def has_z(self) -> bool:
        """Return True if the geometry's coordinate sequence(s) have z values."""
        raise NotImplementedError("Must be implemented by subclass")

    @property
    def wkt(self) -> str:
        """Return the Well Known Text representation of the object."""
        return f"{self._wkt_type}{self._wkt_inset}({self._wkt_coords})"

    @property
    def __geo_interface__(self) -> GeoInterface:
        raise NotImplementedError("Must be implemented by subclass")

    @property
    def _wkt_coords(self) -> str:
        raise NotImplementedError("Must be implemented by subclass")

    @property
    def _wkt_inset(self) -> str:
        """Return Z for 3 dimensinal geometry or an empty string for 2 dimensions."""
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
            return self._coordinates[2]  # type: ignore
        raise DimensionError("This point has no z coordinate")  # pragma: no mutate

    @property
    def coords(self) -> Tuple[PointType]:
        """Return the geometry coordinates."""
        return (self._coordinates,)

    @coords.setter
    def coords(self, coordinates: Tuple[PointType]) -> None:
        """Set the geometry coordinates."""
        self._coordinates = coordinates[0]

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
        """Return Z for 3 dimensinal geometry or an empty string for 2 dimensions."""
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
    def _from_dict(cls, geo_interface: GeoInterface) -> "Point":
        cls._check_dict(geo_interface)
        return cls(*geo_interface["coordinates"])


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
        coordinates = [point.coords[0] for point in self.geoms]
        return tuple(coordinates)

    @coords.setter
    def coords(self, coordinates: LineType) -> None:
        """Set the geometry coordinates."""
        self._geoms = self._set_geoms(coordinates)

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
    def has_z(self) -> bool:
        """Return True if the geometry's coordinate sequence(s) have z values."""
        return self._geoms[0].has_z

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
    def _from_dict(cls, geo_interface: GeoInterface) -> "LineString":
        cls._check_dict(geo_interface)
        return cls(cast(LineType, geo_interface["coordinates"]))

    @staticmethod
    def _set_geoms(coordinates: LineType) -> Tuple[Point, ...]:
        geoms = []
        l0 = len(coordinates[0])  # pragma: no mutate
        for coord in coordinates:
            if len(coord) != l0:
                raise ValueError(
                    "All coordinates must have the same dimension",  # pragma: no mutate
                )
            point = Point(*coord)
            geoms.append(point)
        return tuple(geoms)


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
        if self._geoms[0].coords != self._geoms[-1].coords:
            self._geoms = self._geoms + (self._geoms[0],)

    @property
    def is_ccw(self) -> bool:
        """Return True if the ring is oriented counter clock-wise."""
        return signed_area(self.coords) >= 0

    @property
    def coords(self) -> LineType:
        """Return the geometry coordinates."""
        return super().coords

    @coords.setter
    def coords(self, coordinates: LineType) -> None:
        """Set the geometry coordinates."""
        self._geoms = self._set_geoms(coordinates)
        if self._geoms[0].coords != self._geoms[-1].coords:  # pragma: no mutate
            self._geoms = self._geoms + (self._geoms[0],)

    def _set_orientation(self, clockwise: bool = False) -> None:
        """Set the orientation of the coordinates."""
        area = signed_area(self.coords)
        if area >= 0 and clockwise or area < 0 and not clockwise:  # pragma: no mutate
            self._geoms = self._geoms[::-1]


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
    def interiors(self) -> Generator[LinearRing, None, None]:
        """Interiors (Holes) of the polygon."""
        if self._interiors:
            yield from self._interiors

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
    def has_z(self) -> bool:
        """Return True if the geometry's coordinate sequence(s) have z values."""
        return self._exterior.has_z

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
    def from_bounds(
        cls,
        xmin: float,
        ymin: float,
        xmax: float,
        ymax: float,
    ) -> "Polygon":
        """Construct a `Polygon()` from spatial bounds."""
        return cls([(xmin, ymin), (xmin, ymax), (xmax, ymax), (xmax, ymin)])

    @classmethod
    def _from_dict(cls, geo_interface: GeoInterface) -> "Polygon":
        cls._check_dict(geo_interface)
        return cls(
            cast(LineType, geo_interface["coordinates"][0]),
            cast(Tuple[LineType], geo_interface["coordinates"][1:]),
        )


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
        geom_bounds = list(zip(*(geom.bounds for geom in self.geoms)))  # type: ignore
        return (
            min(geom_bounds[0]),
            min(geom_bounds[1]),
            max(geom_bounds[2]),
            max(geom_bounds[3]),
        )


class MultiPoint(_MultiGeometry):
    """
    A collection of one or more points.

    Attributes
    ----------
    geoms : sequence
        A sequence of Points
    """

    def __init__(self, points: Sequence[PointType]) -> None:
        """
        Create a collection of one or more points.

        Parameters
        ----------
        points : sequence
            A sequence of (x, y [,z]) numeric coordinate pairs or triples.

        Example
        -------
        Construct a 2 point collection

          >>> ob = MultiPoint([[0.0, 0.0], [1.0, 2.0]])
          >>> len(ob.geoms)
          2
          >>> type(ob.geoms[0]) == Point
          True
        """
        self._geoms = tuple(Point(*point) for point in points)

    def __len__(self) -> int:
        """Return the number of points in this MultiPoint."""
        return len(self._geoms)

    def __repr__(self) -> str:
        """Return the representation."""
        return f"{self.geom_type}({tuple(geom.coords[0] for geom in self._geoms)})"

    @property
    def geoms(self) -> Generator[Point, None, None]:
        """Return a sequece of Points."""
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
    def _from_dict(cls, geo_interface: GeoInterface) -> "MultiPoint":
        cls._check_dict(geo_interface)
        return cls(cast(Sequence[PointType], geo_interface["coordinates"]))

    def unique(self) -> None:
        """Make Points unique, delete duplicates."""
        coords = [geom.coords for geom in self.geoms]
        self._geoms = tuple(Point(*coord[0]) for coord in set(coords))


class MultiLineString(_MultiGeometry):
    """
    A collection of one or more line strings.

    A MultiLineString has non-zero length and zero area.

    Attributes
    ----------
    geoms : sequence
        A sequence of LineStrings
    """

    def __init__(self, lines: Sequence[LineType]) -> None:
        """
        Ititialize the MultiLineString.

        Parameters
        ----------
        lines : sequence
            A sequence of line-like coordinate sequences.

        Example
        -------
        Construct a collection containing one line string.

          >>> lines = MultiLineString( [[[0.0, 0.0], [1.0, 2.0]]] )
        """
        self._geoms = tuple(LineString(line) for line in lines)

    def __len__(self) -> int:
        """Return the number of lines in the collection."""
        return len(self._geoms)

    def __repr__(self) -> str:
        """Return the representation."""
        return f"{self.geom_type}({tuple(geom.coords for geom in self._geoms)})"

    @property
    def geoms(self) -> Generator[LineString, None, None]:
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
    def _from_dict(cls, geo_interface: GeoInterface) -> "MultiLineString":
        cls._check_dict(geo_interface)
        return cls(cast(Sequence[LineType], geo_interface["coordinates"]))


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

    def __init__(self, polygons: Sequence[PolygonType]) -> None:
        """
        Initialize a Multipolygon.

        Parameters
        ----------
        polygons : sequence
            A sequence of (shell, holes) tuples where shell is the sequence
            representation of a linear ring (see linearring.py) and holes is
            a sequence of such linear rings

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
        self._geoms = tuple(
            Polygon(
                polygon[0],
                polygon[1] if len(polygon) == 2 else None,  # type: ignore # noqa: IF100
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
    def geoms(self) -> Generator[Polygon, None, None]:
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
    def _from_dict(cls, geo_interface: GeoInterface) -> "MultiPolygon":
        cls._check_dict(geo_interface)
        coords = tuple(
            (poly[0], poly[1:]) for poly in geo_interface["coordinates"]  # type: ignore
        )
        return cls(cast(Sequence[PolygonType], coords))


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
        self._geoms = tuple(geometries)

    def __eq__(self, other: object) -> bool:
        """
        Return equality between collections.

        Types and coordinates from all contained geometries must be equal.
        """
        if not hasattr(other, "__geo_interface__"):
            return False
        if other.__geo_interface__.get("type") != self.geom_type:  # type: ignore
            return False
        if len(other.__geo_interface__.get("geometries", [])) != len(  # type: ignore
            self,
        ):
            return False
        return all(
            s["type"] == o.get("type") and s["coordinates"] == o.get("coordinates")
            for s, o in zip(
                (geom.__geo_interface__ for geom in self._geoms),
                other.__geo_interface__.get("geometries", []),  # type:  ignore
            )
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
        return f"{self.geom_type}({tuple(geom for geom in self._geoms)})"

    @property
    def geoms(self) -> Generator[Geometry, None, None]:
        """Iterate over the geometries."""
        yield from self._geoms

    @property
    def _wkt_coords(self) -> str:
        return ", ".join(geom.wkt for geom in self.geoms)

    @property
    def __geo_interface__(self) -> GeoCollectionInterface:  # type: ignore
        """Return the geo interface of the collection."""
        return {
            "type": self.geom_type,
            "geometries": tuple(geom.__geo_interface__ for geom in self._geoms),
        }
