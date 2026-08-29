#
#   Copyright (C) 2012 - 2024 Christian Ledermann
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
#   along with this library; if not, see <https://www.gnu.org/licenses/>.
#
"""Types for geometries."""

from collections.abc import Sequence
from typing import Any
from typing import Literal
from typing import Union

from typing_extensions import NotRequired
from typing_extensions import Protocol
from typing_extensions import TypedDict  # for Python <3.11 with (Not)Required

Point2D = tuple[float, float]
Point3D = tuple[float, float, float]
PointType = Point2D | Point3D
Line2D = Sequence[Point2D]
Line3D = Sequence[Point3D]
LineType = Line2D | Line3D
Interiors = Sequence[LineType] | None
Poly2d = tuple[Line2D, Sequence[Line2D]] | tuple[Line2D]
Poly3d = tuple[Line3D, Sequence[Line3D]] | tuple[Line3D]
PolygonType = Poly2d | Poly3d

MultiGeometryType = Sequence[PointType | LineType | PolygonType]
Bounds = tuple[float, float, float, float]

CoordinatesType = PointType | LineType | Sequence[LineType]
MultiCoordinatesType = Sequence[CoordinatesType]

GeomType = Literal[
    "Point",
    "LineString",
    "LinearRing",
    "Polygon",
    "MultiPoint",
    "MultiLineString",
    "MultiPolygon",
]


class GeoInterface(TypedDict):
    """Required keys for the GeoInterface."""

    type: GeomType
    coordinates: CoordinatesType | MultiCoordinatesType
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
    properties: NotRequired[dict[str, Any]]
    id: NotRequired[str | int]
    geometry: GeoInterface


class GeoFeatureCollectionInterface(TypedDict):
    """Bbox and id are optional keys for the GeoFeatureCollectionInterface."""

    type: Literal["FeatureCollection"]
    features: Sequence[GeoFeatureInterface]
    bbox: NotRequired[Bounds]
    id: NotRequired[str | int]


class GeoType(Protocol):
    """Any compatible type that implements the __geo_interface__."""

    @property
    def __geo_interface__(self) -> GeoInterface:
        """Return the GeoInterface."""


class GeoCollectionType(Protocol):
    """Any compatible type that implements the __geo_interface__."""

    @property
    def __geo_interface__(self) -> GeoCollectionInterface:
        """Return the GeoInterface."""


__all__ = [
    "Bounds",
    "CoordinatesType",
    "GeoCollectionInterface",
    "GeoCollectionType",
    "GeoFeatureCollectionInterface",
    "GeoFeatureInterface",
    "GeoInterface",
    "GeoType",
    "Interiors",
    "LineType",
    "MultiCoordinatesType",
    "MultiGeometryType",
    "Point2D",
    "Point3D",
    "PointType",
    "PolygonType",
]
