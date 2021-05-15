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
from typing import NoReturn
from typing import Optional
from typing import Sequence
from typing import Tuple
from typing import cast

from .types import Bounds
from .types import GeoInterface
from .types import GeoType
from .types import LineType
from .types import PointType


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

    @property
    def geom_type(self) -> str:
        """Return a string specifying the Geometry Type of the object."""
        return self.__class__.__name__

    @property
    def wkt(self) -> str:
        """Return the Well Known Text Representation of the object."""
        raise NotImplementedError

    @property
    def bounds(self) -> Bounds:
        """Return the X-Y bounding box."""
        raise NotImplementedError

    @property
    def __geo_interface__(self) -> GeoInterface:
        raise NotImplementedError

    @property
    def _wkt_type(self) -> str:
        return self.__class__.__name__.upper()

    @classmethod
    def _check_dict(cls, geo_interface: GeoInterface) -> None:
        if geo_interface["type"] != cls.__name__:
            raise ValueError(
                f"You cannot assign {geo_interface['type']} to {cls.__name__}",
            )


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
        return f"{self.geom_type}{tuple(self._coordinates)}"

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
        raise DimensionError("This point has no z coordinate.")  # pragma: no mutate

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
    def wkt(self) -> str:
        """Return the Well Known Text Representation of the object."""
        coords = " ".join(str(coordinate) for coordinate in self._coordinates)
        inset = " "
        if len(self._coordinates) == 3:
            inset = " Z "
        return f"{self._wkt_type}{inset}({coords})"

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

    @classmethod
    def _from_interface(cls, obj: GeoType) -> "Point":
        return cls._from_dict(obj.__geo_interface__)


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

    def __init__(self, coordinates: LineType):
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
        return tuple(self._geoms)

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
    def wkt(self) -> str:
        """Return the well known text representation of the LineSring."""
        inset = " "
        if len(self.coords[0]) == 3:  # pragma: no mutate
            inset = " Z "
        coords = self._wkt_coords
        return f"{self._wkt_type}{inset}{coords}"

    @property
    def bounds(self) -> Bounds:
        """Return the X-Y bounding box."""
        return (
            min(p.x for p in self._geoms),
            min(p.y for p in self._geoms),
            max(p.x for p in self._geoms),
            max(p.y for p in self._geoms),
        )

    @property
    def _wkt_coords(self) -> str:
        return f'({", ".join(" ".join(str(x) for x in c) for c in self.coords)})'

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

    @classmethod
    def _from_interface(cls, obj: GeoType) -> "LineString":
        return cls._from_dict(obj.__geo_interface__)

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
        interiors = tuple(hole.coords for hole in self.interiors)
        return f"{self.geom_type}({self.exterior.coords}, {interiors or ''})"

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
    def coords(self) -> NoReturn:
        """
        Raise a NotImplementedError.

        A polygon does not have  coordinate sequences.
        """
        raise NotImplementedError(
            "Component rings have coordinate sequences, but the polygon does not",
        )

    @property
    def wkt(self) -> str:
        """Return the well known text representation of the Polygon."""
        inset = " "
        if len(self._exterior.coords[0]) == 3:
            inset = " Z "
        coords = self._wkt_coords
        return f"{self._wkt_type}{inset}{coords}"

    @property
    def _wkt_coords(self) -> str:
        ec = self.exterior._wkt_coords
        ic = "".join(f",{interior._wkt_coords}" for interior in self.interiors)
        return f"({ec}{ic})"

    @property
    def __geo_interface__(self) -> GeoInterface:
        """Return the geo interface."""
        if self._interiors:
            coords = [self.exterior.coords]
            coords.extend(hole.coords for hole in self.interiors)
            return {
                "type": self.geom_type,
                "bbox": self.bounds,
                "coordinates": tuple(coords),
            }
        return {
            "type": self.geom_type,
            "bbox": self.bounds,
            "coordinates": (self._exterior.coords,),
        }

    @classmethod
    def _from_dict(cls, geo_interface: GeoInterface) -> "Polygon":
        cls._check_dict(geo_interface)
        return cls(
            cast(LineType, geo_interface["coordinates"][0]),
            cast(Tuple[LineType], geo_interface["coordinates"][1:]),
        )

    @classmethod
    def _from_interface(cls, obj: GeoType) -> "Polygon":
        return cls._from_dict(obj.__geo_interface__)


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
    def bounds(self) -> Bounds:
        """Return the X-Y bounding box."""
        return (
            min(p.x for p in self._geoms),
            min(p.y for p in self._geoms),
            max(p.x for p in self._geoms),
            max(p.y for p in self._geoms),
        )

    @property
    def wkt(self) -> str:
        """Return the well known text representation of the MultiPoint."""
        return f"{self._wkt_type}{self._wkt_coords}"

    @property
    def _wkt_coords(self):
        wc = ", ".join(" ".join(str(x) for x in c.coords[0]) for c in self.geoms)
        return f"({wc})"

    @property
    def __geo_interface__(self) -> GeoInterface:
        """Return the geo interface."""
        return {
            "type": self.geom_type,
            "bbox": self.bounds,
            "coordinates": tuple(g.coords[0] for g in self._geoms),
        }

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

    def __init__(self, lines) -> None:
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
        return tuple(self._geoms)

    @property
    def bounds(self) -> Bounds:
        """Return the X-Y bounding box."""
        return (
            min(geom.bounds[0] for geom in self.geoms),
            min(geom.bounds[1] for geom in self.geoms),
            max(geom.bounds[2] for geom in self.geoms),
            max(geom.bounds[3] for geom in self.geoms),
        )

    @property
    def wkt(self) -> str:
        """Return the well known text representation of the MultiLineString."""
        wc = ",".join(linestring._wkt_coords for linestring in self.geoms)
        return f"{self._wkt_type}({wc})"

    @property
    def __geo_interface__(self) -> GeoInterface:
        """Return the geo interface."""
        return {
            "type": self.geom_type,
            "bbox": self.bounds,
            "coordinates": tuple(tuple(g.coords) for g in self.geoms),
        }
