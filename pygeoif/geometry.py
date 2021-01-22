# -*- coding: utf-8 -*-
#
#   Copyright (C) 2012  Christian Ledermann
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

from typing import Tuple, Optional, Union

Point2D = Tuple[float, float]
Point3D = Tuple[float, float, float]
TPoint = Union[Point2D, Point3D]

Bounds = Tuple[float, float, float, float]


class _Geometry:
    """Base Class for geometry objects."""

    _coordinates = ()

    @property
    def __geo_interface__(self):
        return {"type": self.geom_type, "coordinates": tuple(self._coordinates)}

    def __str__(self) -> str:
        return self.wkt

    @property
    def geom_type(self) -> str:
        return self.__class__.__name__

    @property
    def wkt(self) -> str:
        raise NotImplementedError

    @property
    def bounds(self) -> Bounds:
        raise NotImplementedError


class Point(_Geometry):
    """
    A zero dimensional geometry

    A point has zero length and zero area.

    Attributes
    ----------
    x, y, z : float
        Coordinate values

    Example
    -------

      >>> p = Point(1.0, -1.0)
      >>> print p
      POINT (1.0000000000000000 -1.0000000000000000)
      >>> p.y
      -1.0
      >>> p.x
      1.0
    """

    def __init__(self, x: float, y: float, z: Optional[float] = None) -> None:
        """
        Parameters
        ----------
        2 or 3 coordinate parameters: x, y, [z] : float
            Easting, northing, and elevation.
        """
        self._coordinates = tuple(
            coordinate for coordinate in [x, y, z] if coordinate is not None
        )

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
        return self._coordinates[2]

    @property
    def coords(self) -> Tuple[TPoint]:
        return (tuple(self._coordinates),)

    @coords.setter
    def coords(self, coordinates: Tuple[TPoint]) -> None:
        self._coordinates = tuple(coordinates)

    @property
    def bounds(self) -> Bounds:
        return self._coordinates + self._coordinates

    @property
    def wkt(self) -> str:
        coords = " ".join(str(coordinate) for coordinate in self._coordinates)
        return f"{self.geom_type.upper()} ({coords})"

    def __repr__(self) -> str:
        return f"{self.geom_type}{self._coordinates}"
