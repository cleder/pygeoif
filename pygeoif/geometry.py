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
from typing import List
from typing import Optional
from typing import Tuple
from typing import cast

from .types import Bounds
from .types import GeoInterface
from .types import GeoType
from .types import LineType
from .types import Point2D
from .types import Point3D
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
    else:
        raise ValueError  # pragma: no mutate
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
        self._coordinates = self._set_geoms(x, y, z)

    def __repr__(self) -> str:
        """Return the representation."""
        return f"{self.geom_type}{tuple(self._coordinates)}"

    @property
    def x(self) -> float:
        """Return x coordinate."""
        return self._coordinates.x

    @property
    def y(self) -> float:
        """Return y coordinate."""
        return self._coordinates.y

    @property
    def z(self) -> float:
        """Return z coordinate."""
        if len(self._coordinates) == 3:
            return self._coordinates.z  # type: ignore
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
        return f"{self.geom_type.upper()}{inset}({coords})"

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

    @staticmethod
    def _set_geoms(x: float, y: float, z: Optional[float] = None) -> PointType:
        """Set coordinates."""
        args = [coordinate for coordinate in [x, y, z] if coordinate is not None]
        if len(args) == 3:
            return Point3D(*args)
        return Point2D(*args)


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
        coords = tuple(tuple(coord) for coord in self.coords)
        return f"{self.geom_type}({coords})"

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
        coords = ", ".join(" ".join(str(x) for x in c) for c in self.coords)
        return f"{self.geom_type.upper()}{inset}({coords})"

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
    def _set_geoms(coordinates: LineType) -> List[Point]:
        geoms = []
        l0 = len(coordinates[0])  # pragma: no mutate
        for coord in coordinates:
            if len(coord) != l0:
                raise ValueError(
                    "All coordinates must have the same dimension",  # pragma: no mutate
                )
            point = Point(*coord)
            geoms.append(point)
        return geoms


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
            self._geoms.append(self._geoms[0])

    @property
    def coords(self) -> LineType:
        """Return the geometry coordinates."""
        return super().coords

    @coords.setter
    def coords(self, coordinates: LineType) -> None:
        """Set the geometry coordinates."""
        self._geoms = self._set_geoms(coordinates)
        if self._geoms[0].coords != self._geoms[-1].coords:  # pragma: no mutate
            self._geoms.append(self._geoms[0])

    def _set_orientation(self, clockwise: bool = False) -> None:
        """Set the orientation of the coordinates."""
        area = signed_area(self.coords)
        if area >= 0 and clockwise or area < 0 and not clockwise:  # pragma: no mutate
            self._geoms = self._geoms[::-1]
