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
from .types import PointType


class DimensionError(IndexError):
    """Geometries must have 2 or 3 dimensions."""


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
    def __geo_interface__(self):
        return {"type": self.geom_type, "coordinates": ()}

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
        raise DimensionError("This point has no z coordinate.")  # pragma: no mutate

    @property
    def coords(self) -> Tuple[PointType]:
        """Return the geometry coordinates."""
        return (cast(PointType, (self._coordinates)),)

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
            "coordinates": cast(LineType, self.coords),
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
