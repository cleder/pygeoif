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
"""Geometry Factories."""
import re
from typing import List
from typing import Optional
from typing import Tuple
from typing import Union
from typing import cast

from pygeoif.types import GeoCollectionInterface
from pygeoif.types import GeoCollectionType
from pygeoif.types import GeoInterface
from pygeoif.types import GeoType
from pygeoif.types import LineType
from pygeoif.types import PointType
from pygeoif.types import PolygonType

from .geometry import Geometry
from .geometry import GeometryCollection
from .geometry import LinearRing
from .geometry import LineString
from .geometry import MultiLineString
from .geometry import MultiPoint
from .geometry import MultiPolygon
from .geometry import Point
from .geometry import Polygon
from .geometry import signed_area

Exteriors = Optional[List[LineType]]
wkt_regex = re.compile(
    r"^(SRID=(?P<srid>\d+);)?"
    r"(?P<wkt>"
    r"(?P<type>POINT|LINESTRING|LINEARRING|POLYGON|"
    r"MULTIPOINT|MULTILINESTRING|MULTIPOLYGON|"
    r"GEOMETRYCOLLECTION)"
    r"[ACEGIMLONPSRUTYZ\d,\.\-\(\) ]+)$",
    re.I,
)
gcre = re.compile(r"POINT|LINESTRING|LINEARRING|POLYGON")
outer = re.compile(r"\((.+)\)")
inner = re.compile(r"\([^)]*\)")
mpre = re.compile(r"\(\((.+?)\)\)")


class WKTParserError(AttributeError):
    """WKT not supported or cannot be parsed."""


def orient(polygon: Polygon, ccw: bool = True) -> Polygon:
    """
    Return a polygon with exteriors and interiors in the right orientation.

    if ccw is True than the exteriror will be in counterclockwise orientation
    and the interiors will be in clockwise orientation, or
    the other way round when ccw is False.
    """
    s = 1.0
    if not ccw:
        s = -1.0
    rings = []
    ring = polygon.exterior
    if signed_area(ring.coords) / s >= 0.0:
        rings.append(ring.coords)
    else:
        rings.append(list(ring.coords)[::-1])
    for ring in polygon.interiors:
        if signed_area(ring.coords) / s <= 0.0:
            rings.append(ring.coords)
        else:
            rings.append(list(ring.coords)[::-1])
    return Polygon(rings[0], rings[1:])


def box(
    minx: float,
    miny: float,
    maxx: float,
    maxy: float,
    ccw: bool = True,
) -> Polygon:
    """Return a rectangular polygon with configurable normal vector."""
    coords = [(maxx, miny), (maxx, maxy), (minx, maxy), (minx, miny)]
    if not ccw:
        coords = coords[::-1]
    return Polygon(coords)


def shape(
    context: Union[
        GeoType,
        GeoCollectionType,
        GeoCollectionInterface,
        GeoCollectionInterface,
    ],
) -> Union[Geometry, GeometryCollection]:
    """
    Return a new geometry with coordinates *copied* from the context.

    Changes to the original context will not be reflected in the
    geometry object.

    Parameters
    ----------
    context :
        a GeoJSON-like dict, which provides a "type" member describing the type
        of the geometry and "coordinates" member providing a list of coordinates,
        or an object which implements __geo_interface__.

    Returns
    -------
    Geometry object
    Example
    -------
    Create a Point from GeoJSON, and then create a copy using __geo_interface__.
    >>> context = {'type': 'Point', 'coordinates': [0, 1]}
    >>> geom = shape(context)
    >>> geom.geom_type == 'Point'
    True
    >>> geom.wkt
    'POINT (0 1)'
    >>> geom2 = shape(geom)
    >>> geom == geom2
    True
    """
    type_map = {
        "Point": Point,
        "LineString": LineString,
        "LinearRing": LinearRing,
        "Polygon": Polygon,
        "MultiPoint": MultiPoint,
        "MultiLineString": MultiLineString,
        "MultiPolygon": MultiPolygon,
    }
    geometry = context if isinstance(context, dict) else mapping(context)  # noqa: IF100
    if not geometry:
        raise TypeError("Object does not implement __geo_interface__")

    constructor = type_map.get(geometry["type"])
    if constructor:
        return constructor._from_dict(geometry)  # type: ignore
    if geometry["type"] == "GeometryCollection":
        geometries = [shape(fi) for fi in geometry["geometries"]]  # type: ignore
        return GeometryCollection(geometries)  # type: ignore
    raise NotImplementedError(f"[{geometry['type']} is nor implemented")


def _point_from_wkt_coordinates(coordinates: str) -> Point:
    coords = [float(c) for c in coordinates.split()]
    return Point(*coords)


def _line_from_wkt_coordinates(coordinates: str) -> LineString:
    coords = coordinates.split(",")
    return LineString(
        [cast(PointType, tuple(float(c) for c in coord.split())) for coord in coords],
    )


def _ring_from_wkt_coordinates(coordinates: str) -> LinearRing:
    coords = coordinates.split(",")
    return LinearRing(
        [cast(PointType, tuple(float(c) for c in coord.split())) for coord in coords],
    )


def _shell_holes_from_wkt_coords(
    coords: List[str],
) -> Tuple[LineType, Exteriors]:
    interior: LineType = [
        cast(PointType, tuple(float(c) for c in coord.split())) for coord in coords[0]
    ]
    if len(coords) > 1:
        # we have a polygon with holes
        exteriors = [
            cast(
                LineType,
                [
                    cast(PointType, tuple(float(c) for c in coord.split()))
                    for coord in ext
                ],
            )
            for ext in coords[1:]
        ]
    else:
        exteriors = None  # type: ignore
    return interior, exteriors


def _polygon_from_wkt_coordinates(coordinates: str) -> Polygon:
    coords = [
        interior.strip("()").split(",") for interior in inner.findall(coordinates)
    ]
    interior, exteriors = _shell_holes_from_wkt_coords(coords)
    return Polygon(
        interior,
        exteriors,
    )


def _multipoint_from_wkt_coordinates(coordinates: str) -> MultiPoint:
    coords = [coord.strip().strip("()") for coord in coordinates.split(",")]
    return MultiPoint(
        [cast(PointType, tuple(float(c) for c in coord.split())) for coord in coords],
    )


def _multiline_from_wkt_coordinates(coordinates: str) -> MultiLineString:
    coords = [
        [
            cast(PointType, tuple(float(c) for c in coord.split()))
            for coord in lines.strip("()").split(",")
        ]
        for lines in inner.findall(coordinates)
    ]
    return MultiLineString(coords)


def _multipolygon_from_wkt_coordinates(coordinates: str) -> MultiPolygon:
    polygons: List[PolygonType] = []
    m = mpre.split(coordinates)
    for polygon in m:
        if not polygon.strip(", "):
            continue
        coords = [
            interior.strip("()").split(",")
            for interior in inner.findall(f"({polygon})")
        ]
        interior, exteriors = _shell_holes_from_wkt_coords(coords)
        if exteriors:
            polygons.append(cast(PolygonType, [interior, exteriors]))
        else:
            polygons.append(cast(PolygonType, [interior]))
    return MultiPolygon(polygons)


def _multigeometry_from_wkt_coordinates(coordinates: str) -> GeometryCollection:
    gc_types = gcre.findall(coordinates)
    gc_coords = gcre.split(coordinates)[1:]
    assert len(gc_types) == len(gc_coords)  # noqa: S101
    geometries: List[Geometry] = []
    for (gc_type, gc_coord) in zip(gc_types, gc_coords):
        gc_wkt = gc_type + gc_coord[: gc_coord.rfind(")") + 1]
        geometries.append(cast(Geometry, from_wkt(gc_wkt)))
    return GeometryCollection(geometries)


def from_wkt(geo_str: str) -> Optional[Union[Geometry, GeometryCollection]]:
    """Create a geometry from its WKT representation."""
    type_map = {
        "POINT": _point_from_wkt_coordinates,
        "LINESTRING": _line_from_wkt_coordinates,
        "LINEARRING": _ring_from_wkt_coordinates,
        "POLYGON": _polygon_from_wkt_coordinates,
        "MULTIPOINT": _multipoint_from_wkt_coordinates,
        "MULTILINESTRING": _multiline_from_wkt_coordinates,
        "MULTIPOLYGON": _multipolygon_from_wkt_coordinates,
        "GEOMETRYCOLLECTION": _multigeometry_from_wkt_coordinates,
    }

    wkt = geo_str.strip()
    wkt = " ".join(line.strip() for line in wkt.splitlines())
    try:
        wkt = wkt_regex.match(wkt).group("wkt")  # type: ignore
        ftype = wkt_regex.match(wkt).group("type")  # type: ignore
        outerstr = outer.search(wkt)
        coordinates = outerstr.group(1)  # type: ignore
    except AttributeError:
        raise WKTParserError(f"Cannot parse {wkt}")
    constructor = type_map[ftype]
    try:
        return constructor(coordinates)  # type: ignore
    except TypeError:
        raise WKTParserError(f"Cannot parse {wkt}")


def mapping(
    ob: Union[GeoType, GeoCollectionType],
) -> Union[GeoCollectionInterface, GeoInterface]:
    """
    Return a GeoJSON-like mapping.

    Parameters
    ----------
    ob :
        An object which implements __geo_interface__.

    Returns
    -------
    dict
    Example
    -------
    >>> pt = Point(0, 0)
    >>> mapping(pt)
    {'type': 'Point', 'coordinates': (0.0, 0.0)}
    """
    return ob.__geo_interface__


__all__ = [
    'WKTParserError',
    'box',
    'from_wkt',
    'mapping',
    'orient',
    'shape',
]
