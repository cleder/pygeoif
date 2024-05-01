#
#   Copyright (C) 2012 -2024  Christian Ledermann
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
import math
import warnings
from itertools import chain
from typing import Any
from typing import Hashable
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
from pygeoif.functions import compare_coordinates
from pygeoif.functions import compare_geo_interface
from pygeoif.functions import convex_hull
from pygeoif.functions import dedupe
from pygeoif.functions import signed_area
from pygeoif.types import Bounds
from pygeoif.types import GeoCollectionInterface
from pygeoif.types import GeoInterface
from pygeoif.types import GeomType
from pygeoif.types import GeoType
from pygeoif.types import LineType
from pygeoif.types import Point2D
from pygeoif.types import PointType
from pygeoif.types import PolygonType


class _Geometry:
    """Base Class for geometry objects."""

    __slots__ = ("_geoms",)

    _geoms: Hashable

    def __setattr__(self, *args: Any) -> NoReturn:  # noqa: ANN401
        msg = f"Attributes of {self.__class__.__name__} cannot be changed"
        raise AttributeError(
            msg,
        )

    def __delattr__(self, *args: Any) -> NoReturn:  # noqa: ANN401
        msg = f"Attributes of {self.__class__.__name__} cannot be deleted"
        raise AttributeError(
            msg,
        )

    def __str__(self) -> str:
        return self.wkt

    def __eq__(self, other: object) -> bool:
        """
        Check if the geometry objects have the same coordinates and type.

        Empty geometries are always considered as not equal.
        """
        try:
            return all(
                (
                    not self.is_empty,
                    self.__geo_interface__["type"]
                    == other.__geo_interface__.get(  # type: ignore [attr-defined]
                        "type",
                    ),
                    compare_coordinates(
                        coords=self.__geo_interface__["coordinates"],
                        other=other.__geo_interface__.get(  # type: ignore [attr-defined]
                            "coordinates",
                        ),
                    ),
                ),
            )
        except AttributeError:
            return False

    def __bool__(self) -> bool:
        return self.is_empty is False

    @property
    def bounds(self) -> Union[Bounds, Tuple[()]]:
        """
        Return minimum bounding region (min x, min y, max x, max y).

        An empty geometry returns an empty tuple.
        """
        return () if self.is_empty else self._get_bounds()

    @property
    def convex_hull(self) -> Optional[Union["Point", "LineString", "Polygon"]]:
        """
        Return the Convex Hull.

        Returns a representation of the smallest convex Polygon containing
        all the points in the object unless the number of points in the object
        is fewer than three.
        For two points, the convex hull collapses to a LineString;
        for 1, to a Point.
        """
        if self.has_z:
            warnings.warn(
                "The convex Hull will only return the projection to"
                " 2 dimensions xy coordinates",
                stacklevel=2,
            )

        hull = convex_hull(self._prepare_hull())
        if len(hull) == 0:
            return None
        if len(hull) == 1:
            return Point(*hull[0])
        return LineString(hull) if len(hull) == 2 else Polygon(hull)  # noqa: PLR2004

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
        msg = "Must be implemented by subclass"
        raise NotImplementedError(msg)

    @property
    def is_empty(self) -> bool:
        """Return if this geometry is empty."""
        msg = "Must be implemented by subclass"
        raise NotImplementedError(msg)

    @property
    def wkt(self) -> str:
        """Return the Well Known Text representation of the object."""
        if self.is_empty:
            return f"{self._wkt_type} EMPTY"
        return f"{self._wkt_type}{self._wkt_inset}({self._wkt_coords})"

    @property
    def __geo_interface__(self) -> GeoInterface:
        if self.is_empty:
            msg = "Empty Geometry"
            raise AttributeError(msg)
        return {
            "type": cast(GeomType, self.geom_type),
            "bbox": cast(Bounds, self.bounds),
            "coordinates": (),
        }

    @property
    def _wkt_coords(self) -> str:
        msg = "Must be implemented by subclass"
        raise NotImplementedError(msg)

    @property
    def _wkt_inset(self) -> str:
        """Return Z for 3 dimensional geometry or an empty string for 2 dimensions."""
        return " Z " if self.has_z else " "

    @property
    def _wkt_type(self) -> str:
        """Return the WKT name of the geometry."""
        return self.__class__.__name__.upper()

    @classmethod
    def _check_dict(cls, geo_interface: GeoInterface) -> None:
        if geo_interface["type"] != cls.__name__:
            msg = f"You cannot assign {geo_interface['type']} to {cls.__name__}"
            raise ValueError(
                msg,
            )

    @classmethod
    def _from_dict(cls, geo_interface: GeoInterface) -> "_Geometry":
        cls._check_dict(geo_interface)
        msg = "Must be implemented by subclass"
        raise NotImplementedError(msg)

    @classmethod
    def _from_interface(cls, obj: GeoType) -> "_Geometry":
        return cls._from_dict(obj.__geo_interface__)

    def _prepare_hull(self) -> Iterable[Point2D]:
        msg = "Must be implemented by subclass"
        raise NotImplementedError(msg)

    def _get_bounds(self) -> Bounds:
        msg = "Must be implemented by subclass"
        raise NotImplementedError(msg)


class Point(_Geometry):
    """
    A zero dimensional geometry.

    A point has zero length and zero area.

    Attributes:
    ----------
    x, y, z : float
        Coordinate values

    Example:
    -------
      >>> p = Point(1.0, -1.0)
      >>> print p
      POINT (1.0 -1.0)
      >>> p.y
      -1.0
      >>> p.x
      1.0

    """

    _geoms: PointType

    def __init__(self, x: float, y: float, z: Optional[float] = None) -> None:
        """
        Initialize a Point.

        Parameters
        ----------
        2 or 3 coordinate parameters: x, y, [z] : float
            Easting, northing, and elevation.

        """
        geoms = (x, y, z) if z is not None else (x, y)
        object.__setattr__(
            self,
            "_geoms",
            geoms,
        )

    def __repr__(self) -> str:
        """Return the representation."""
        if self.is_empty:
            return f"{self.geom_type}()"
        return f"{self.geom_type}{self._geoms}"

    @property
    def is_empty(self) -> bool:
        """
        Return if this geometry is empty.

        A Point is considered empty when it has no valid coordinates.
        """
        return any(coord is None or math.isnan(coord) for coord in self._geoms)

    @property
    def x(self) -> float:
        """Return x coordinate."""
        return self._geoms[0]

    @property
    def y(self) -> float:
        """Return y coordinate."""
        return self._geoms[1]

    @property
    def z(self) -> Optional[float]:
        """Return z coordinate."""
        if self.has_z:
            return self._geoms[2]  # type: ignore [misc]
        msg = f"The {self!r} geometry does not have z values"
        raise DimensionError(msg)

    @property
    def coords(self) -> Union[Tuple[PointType], Tuple[()]]:
        """Return the geometry coordinates."""
        return () if self.is_empty else (self._geoms,)

    @property
    def has_z(self) -> bool:
        """Return True if the geometry's coordinate sequence(s) have z values."""
        return len(self._geoms) == 3  # noqa: PLR2004

    @property
    def _wkt_coords(self) -> str:
        return " ".join(str(coordinate) for coordinate in self._geoms)

    @property
    def __geo_interface__(self) -> GeoInterface:
        """Return the geo interface."""
        geo_interface = super().__geo_interface__
        geo_interface["coordinates"] = cast(PointType, tuple(self._geoms))
        return geo_interface

    @classmethod
    def from_coordinates(cls, coordinates: Sequence[PointType]) -> "Point":
        """Construct a point from coordinates."""
        return cls(*coordinates[0])

    @classmethod
    def _from_dict(cls, geo_interface: GeoInterface) -> "Point":
        cls._check_dict(geo_interface)
        return cls(*geo_interface["coordinates"])

    def _get_bounds(self) -> Bounds:
        return self.x, self.y, self.x, self.y

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

    _geoms: Tuple[Point, ...]

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
        object.__setattr__(self, "_geoms", self._set_geoms(coordinates))

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
        return cast(
            LineType,
            tuple(point.coords[0] for point in self.geoms if point.coords),
        )

    @property
    def is_empty(self) -> bool:
        """
        Return if this geometry is empty.

        A Linestring is considered empty when it has no points.
        """
        return len(self._geoms) == 0

    @property
    def has_z(self) -> Optional[bool]:
        """Return True if the geometry's coordinate sequence(s) have z values."""
        return self._geoms[0].has_z if self.geoms else None

    @property
    def _wkt_coords(self) -> str:
        return ", ".join(point._wkt_coords for point in self.geoms)  # noqa: SLF001

    @property
    def __geo_interface__(self) -> GeoInterface:
        """Return the geo interface."""
        geo_interface = super().__geo_interface__
        geo_interface["coordinates"] = self.coords
        return geo_interface

    @classmethod
    def from_coordinates(cls, coordinates: LineType) -> "LineString":
        """Construct a linestring from coordinates."""
        return cls(coordinates)

    @classmethod
    def from_points(cls, *args: Point) -> "LineString":
        """Create a linestring from points."""
        return cls(
            cast(LineType, tuple(point.coords[0] for point in args if point.coords)),
        )

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
                msg = (  # type: ignore [unreachable]
                    "All coordinates must have the same dimension"
                )
                raise DimensionError(
                    msg,
                )
            last_len = len(coord)
            point = Point(*coord)
            if point:
                geoms.append(point)
        return tuple(geoms)

    def _get_bounds(self) -> Bounds:
        """Return the X-Y bounding box."""
        xy = list(zip(*((p.x, p.y) for p in self._geoms)))
        return (
            min(xy[0]),
            min(xy[1]),
            max(xy[0]),
            max(xy[1]),
        )

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
        ----
            coordinates (Sequence):
                A sequence of (x, y [,z]) numeric coordinate pairs or triples

        """
        super().__init__(coordinates)
        if not self.is_empty and self._geoms[0].coords != self._geoms[-1].coords:
            object.__setattr__(self, "_geoms", (*self._geoms, self._geoms[0]))

    @property
    def centroid(self) -> Optional[Point]:
        """Return the centroid of the ring."""
        if self.has_z:
            msg = "Centeroid is only implemented for 2D coordinates"
            raise DimensionError(msg)

        cent, area = centroid(self.coords)
        if any(math.isnan(coord) for coord in cent):
            return None
        return (
            Point(x=cent[0], y=cent[1])
            if math.isclose(a=area, b=signed_area(self.coords))
            else None
        )

    @property
    def is_ccw(self) -> bool:
        """Return True if the ring is oriented counter clock-wise."""
        return signed_area(self.coords) >= 0


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

    _geoms: Tuple[LinearRing, ...]

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
        interiors = tuple(LinearRing(hole) for hole in holes) if holes else ()
        exterior = LinearRing(shell)
        object.__setattr__(self, "_geoms", (exterior, interiors))

    def __repr__(self) -> str:
        """Return the representation."""
        return f"{self.geom_type}{self.coords}"

    @property
    def exterior(self) -> LinearRing:
        """Return the exterior Linear Ring of the polygon."""
        return self._geoms[0]

    @property
    def interiors(self) -> Iterator[LinearRing]:
        """Interiors (Holes) of the polygon."""
        yield from (
            interior
            for interior in self._geoms[1]  # type: ignore [attr-defined]
            if interior
        )

    @property
    def is_empty(self) -> bool:
        """
        Return if this geometry is empty.

        A polygon is empty when it does not have an exterior.
        """
        return self._geoms[0].is_empty

    @property
    def coords(self) -> PolygonType:
        """
        Return Coordinates of the Polygon.

        Note that this is not implemented in Shapely.
        """
        if self._geoms[1]:
            return cast(
                PolygonType,
                (
                    self.exterior.coords,
                    tuple(interior.coords for interior in self.interiors if interior),
                ),
            )
        return cast(PolygonType, (self.exterior.coords,))

    @property
    def has_z(self) -> Optional[bool]:
        """Return True if the geometry's coordinate sequence(s) have z values."""
        return self._geoms[0].has_z

    @property
    def _wkt_coords(self) -> str:
        ec = self.exterior._wkt_coords  # noqa: SLF001
        ic = "".join(
            f",({interior._wkt_coords})" for interior in self.interiors  # noqa: SLF001
        )
        return f"({ec}){ic}"

    @property
    def __geo_interface__(self) -> GeoInterface:
        """Return the geo interface."""
        geo_interface = super().__geo_interface__
        coords = (self.exterior.coords, *tuple(hole.coords for hole in self.interiors))
        geo_interface["coordinates"] = coords
        return geo_interface

    @classmethod
    def from_coordinates(cls, coordinates: PolygonType) -> "Polygon":
        """Construct a linestring from coordinates."""
        return cls(*coordinates)

    @classmethod
    def from_linear_rings(cls, shell: LinearRing, *args: LinearRing) -> "Polygon":
        """Construct a Polygon from linear rings."""
        return cls(
            shell=shell.coords,
            holes=tuple(lr.coords for lr in args),
        )

    @classmethod
    def _from_dict(cls, geo_interface: GeoInterface) -> "Polygon":
        cls._check_dict(geo_interface)
        if not geo_interface["coordinates"]:
            return cls(shell=(), holes=())
        return cls(
            shell=cast(LineType, geo_interface["coordinates"][0]),
            holes=cast(Tuple[LineType], geo_interface["coordinates"][1:]),
        )

    def _get_bounds(self) -> Bounds:
        return self.exterior._get_bounds()  # noqa: SLF001

    def _prepare_hull(self) -> Iterable[Point2D]:
        return self.exterior._prepare_hull()  # noqa: SLF001


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
        msg = "Multi-part geometries do not provide a coordinate sequence"
        raise NotImplementedError(
            msg,
        )

    @property
    def has_z(self) -> Optional[bool]:
        """Return True if any geometry of the collection have z values."""
        return any(geom.has_z for geom in self.geoms) if self._geoms else None

    @property
    def geoms(self) -> Iterator[_Geometry]:
        """Iterate over the geometries."""
        yield from (
            geom
            for geom in self._geoms  # type: ignore [attr-defined]
            if not geom.is_empty
        )

    @property
    def is_empty(self) -> bool:
        """Return if collection is not empty and all its member are not empty."""
        return all(geom.is_empty for geom in self._geoms)  # type: ignore [attr-defined]

    def _get_bounds(self) -> Bounds:
        """Return the X-Y bounding box."""
        geom_bounds = list(
            zip(*(geom.bounds for geom in self.geoms)),
        )
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

    _geoms: Tuple[Point, ...]

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
        object.__setattr__(self, "_geoms", tuple(Point(*point) for point in points))

    def __len__(self) -> int:
        """Return the number of points in this MultiPoint."""
        return len(self._geoms)

    def __repr__(self) -> str:
        """Return the representation."""
        return (
            f"{self.geom_type}"
            f"({tuple(geom.coords[0] for geom in self._geoms if geom.coords)})"
        )

    @property
    def geoms(self) -> Iterator[Point]:
        """Iterate over the points."""
        yield from (cast(Point, p) for p in super().geoms)

    @property
    def _wkt_coords(self) -> str:
        return ", ".join(point._wkt_coords for point in self.geoms)  # noqa: SLF001

    @property
    def __geo_interface__(self) -> GeoInterface:
        """Return the geo interface."""
        geo_interface = super().__geo_interface__
        geo_interface["coordinates"] = tuple(
            geom.coords[0] for geom in self.geoms if geom.coords
        )
        return geo_interface

    @classmethod
    def from_points(cls, *args: Point, unique: bool = False) -> "MultiPoint":
        """Create a MultiPoint from Points."""
        return cls([point.coords[0] for point in args if point.coords], unique=unique)

    @classmethod
    def _from_dict(cls, geo_interface: GeoInterface) -> "MultiPoint":
        cls._check_dict(geo_interface)
        return cls(cast(Sequence[PointType], geo_interface["coordinates"]))

    def _prepare_hull(self) -> Iterable[Point2D]:
        return ((pt.x, pt.y) for pt in self.geoms)


class MultiLineString(_MultiGeometry):
    """
    A collection of one or more line strings.

    A MultiLineString has non-zero length and zero area.

    Attributes
    ----------
    geoms : sequence
        A sequence of LineStrings

    """

    _geoms: Tuple[LineString, ...]

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
        object.__setattr__(self, "_geoms", tuple(LineString(line) for line in lines))

    def __len__(self) -> int:
        """Return the number of lines in the collection."""
        return len(self._geoms)

    def __repr__(self) -> str:
        """Return the representation."""
        return f"{self.geom_type}({tuple(geom.coords for geom in self._geoms)})"

    @property
    def geoms(self) -> Iterator[LineString]:
        """Iterate over the points."""
        yield from (cast(LineString, line) for line in super().geoms)

    @property
    def _wkt_coords(self) -> str:
        return ",".join(
            f"({linestring._wkt_coords})" for linestring in self.geoms  # noqa: SLF001
        )

    @property
    def __geo_interface__(self) -> GeoInterface:
        """Return the geo interface."""
        geo_interface = super().__geo_interface__
        geo_interface["coordinates"] = tuple(geom.coords for geom in self.geoms)
        return geo_interface

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

    _geoms: Tuple[Polygon, ...]

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

        object.__setattr__(
            self,
            "_geoms",
            tuple(
                Polygon(
                    shell=polygon[0],
                    holes=polygon[1] if len(polygon) == 2 else None,  # noqa: PLR2004
                )
                for polygon in polygons
            ),
        )

    def __len__(self) -> int:
        """Return the number of polygons in the collection."""
        return len(self._geoms)

    def __repr__(self) -> str:
        """Return the representation."""
        return f"{self.geom_type}({tuple(geom.coords for geom in self.geoms)})"

    @property
    def geoms(self) -> Iterator[Polygon]:
        """Iterate over the points."""
        yield from (cast(Polygon, p) for p in super().geoms)

    @property
    def _wkt_coords(self) -> str:
        return ",".join(f"({poly._wkt_coords})" for poly in self.geoms)  # noqa: SLF001

    @property
    def __geo_interface__(self) -> GeoInterface:
        """Return the geo interface."""
        geo_interface = super().__geo_interface__
        coords = tuple(
            (geom.exterior.coords, *tuple(hole.coords for hole in geom.interiors))
            for geom in self.geoms
        )
        geo_interface["coordinates"] = coords
        return geo_interface

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

    Attributes:
    ----------
    geoms : sequence
        A sequence of geometry instances

    Please note:
    GEOMETRYCOLLECTION isn't supported by the Shapefile format. And this sub-
    class isn't generally supported by ordinary GIS sw (viewers and so on). So
    it's very rarely used in the real GIS professional world.

    Example:
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

    _geoms: Tuple[Union[Geometry, "GeometryCollection"], ...]

    def __init__(
        self,
        geometries: Iterable[Union[Geometry, "GeometryCollection"]],
    ) -> None:
        """
        Initialize the MultiGeometry with Geometries.

        Args:
        ----
            geometries (Iterable[Geometry]

        """
        object.__setattr__(self, "_geoms", tuple(geom for geom in geometries if geom))

    def __eq__(self, other: object) -> bool:
        """
        Return equality between collections.

        Types and coordinates from all contained geometries must be equal.
        """
        try:
            if self.is_empty:
                return False
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
        return compare_geo_interface(
            first=self.__geo_interface__,
            second=other.__geo_interface__,  # type: ignore [attr-defined]
        )

    def __len__(self) -> int:
        """
        Length of the collection.

        Returns
        -------
            int: Number of geometries in the collection.

        """
        return len(self._geoms)

    def __repr__(self) -> str:
        """Return the representation."""
        return f"{self.geom_type}({tuple(self.geoms)})"

    @property
    def _wkt_coords(self) -> str:
        return ", ".join(geom.wkt for geom in self.geoms)

    @property
    def __geo_interface__(self) -> GeoCollectionInterface:  # type: ignore [override]
        """Return the geo interface of the collection."""
        return {
            "type": "GeometryCollection",
            "geometries": tuple(geom.__geo_interface__ for geom in self.geoms),
        }

    def _prepare_hull(self) -> Iterable[Point2D]:
        return chain.from_iterable(
            geom._prepare_hull() for geom in self.geoms  # noqa: SLF001
        )


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
