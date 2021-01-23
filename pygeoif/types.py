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
"""Types for geometries."""
from typing import Sequence
from typing import Tuple
from typing import Union

from typing_extensions import Protocol
from typing_extensions import TypedDict

Point2D = Tuple[float, float]  # pragma: no mutate
Point3D = Tuple[float, float, float]  # pragma: no mutate
PointType = Union[Point2D, Point3D]  # pragma: no mutate
LineType = Sequence[PointType]  # pragma: no mutate

Bounds = Tuple[float, float, float, float]  # pragma: no mutate

CoordinatesType = Union[PointType, LineType]  # pragma: no mutate

GeoInterface = TypedDict(
    "GeoInterface",  # pragma: no mutate
    {"type": str, "coordinates": CoordinatesType, "bbox": Bounds},  # pragma: no mutate
)  # pragma: no mutate


class GeoType(Protocol):
    """Any compatible type that implements the __geo_interface__."""

    __geo_interface__: GeoInterface
