#
#   Copyright (C) 2012 -2022  Christian Ledermann
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
from typing import Any
from typing import Dict
from typing import Optional
from typing import Sequence
from typing import Tuple
from typing import Union

from typing_extensions import Literal
from typing_extensions import NotRequired
from typing_extensions import Protocol
from typing_extensions import TypedDict  # for Python <3.11 with (Not)Required

Point2D = Tuple[float, float]
Point3D = Tuple[float, float, float]
PointType = Union[Point2D, Point3D]
LineType = Sequence[PointType]
PolygonType = Union[
    Tuple[LineType, Sequence[LineType]],
    Tuple[LineType],
]

Exteriors = Optional[Sequence[LineType]]

MultiGeometryType = Sequence[Union[PointType, LineType, PolygonType]]
Bounds = Tuple[float, float, float, float]

CoordinatesType = Union[
    PointType,
    LineType,
    Sequence[LineType],
]
MultiCoordinatesType = Sequence[CoordinatesType]


class GeoInterface(TypedDict):
    """Required keys for the GeoInterface."""

    type: str
    coordinates: Union[CoordinatesType, MultiCoordinatesType]
    bbox: NotRequired[Bounds]


class GeoCollectionInterface(TypedDict):
    """Geometry Collection Interface."""

    type: Literal["GeometryCollection"]
    geometries: Sequence[Union[GeoInterface, "GeoCollectionInterface"]]
    bbox: NotRequired[Bounds]


class GeoFeatureInterface(TypedDict):
    """The GeoFeatureInterface has optional keys."""

    type: Literal["Feature"]
    bbox: NotRequired[Bounds]
    properties: NotRequired[Dict[str, Any]]
    id: NotRequired[Union[str, int]]
    geometry: GeoInterface


class GeoFeatureCollectionInterface(TypedDict):
    """Bbox and id are optional keys for the GeoFeatureCollectionInterface."""

    type: Literal["FeatureCollection"]
    features: Sequence[GeoFeatureInterface]
    bbox: NotRequired[Bounds]
    id: NotRequired[Union[str, int]]


class GeoType(Protocol):
    """Any compatible type that implements the __geo_interface__."""

    __geo_interface__: GeoInterface


class GeoCollectionType(Protocol):
    """Any compatible type that implements the __geo_interface__."""

    __geo_interface__: GeoCollectionInterface


__all__ = [
    "Bounds",
    "CoordinatesType",
    "Exteriors",
    "GeoCollectionInterface",
    "GeoCollectionType",
    "GeoFeatureCollectionInterface",
    "GeoFeatureInterface",
    "GeoInterface",
    "GeoType",
    "LineType",
    "MultiCoordinatesType",
    "MultiGeometryType",
    "Point2D",
    "Point3D",
    "PointType",
    "PolygonType",
]
