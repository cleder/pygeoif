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
"""Geometry Factories."""
import re
from typing import List
from typing import Optional
from typing import Pattern
from typing import Tuple
from typing import Union
from typing import cast

from pygeoif.exceptions import WKTParserError
from pygeoif.functions import move_geo_interface
from pygeoif.functions import signed_area
from pygeoif.geometry import Geometry
from pygeoif.geometry import GeometryCollection
from pygeoif.geometry import LinearRing
from pygeoif.geometry import LineString
from pygeoif.geometry import MultiLineString
from pygeoif.geometry import MultiPoint
from pygeoif.geometry import MultiPolygon
from pygeoif.geometry import Point
from pygeoif.geometry import Polygon
from pygeoif.types import GeoCollectionInterface
from pygeoif.types import GeoCollectionType
from pygeoif.types import GeoInterface
from pygeoif.types import GeoType
from pygeoif.types import Interiors
from pygeoif.types import LineType
from pygeoif.types import PointType
from pygeoif.types import PolygonType

wkt_regex: Pattern[str] = re.compile(
    pattern=(
        r"^(SRID=(?P<srid>\d+);)?"
        "(?P<wkt>"
        "(?P<type>POINT|LINESTRING|LINEARRING|POLYGON|"
        "MULTIPOINT|MULTILINESTRING|MULTIPOLYGON|"
        "GEOMETRYCOLLECTION)"
        r"[ACEGIMLONPSRUTYZ\d,\.\-\(\) ]+)$"
    ),
    flags=re.I,
)
gcre: Pattern[str] = re.compile(
    r"POINT|LINESTRING|LINEARRING|POLYGON|MULTIPOINT|MULTILINESTRING|MULTIPOLYGON",
)
outer: Pattern[str] = re.compile(r"\((.+)\)")
inner: Pattern[str] = re.compile(r"\([^)]*\)")
mpre: Pattern[str] = re.compile(r"\(\((.+?)\)\)")


def get_oriented_ring(ring: LineType, ccw: bool) -> LineType:  # noqa: FBT001
    s = 1.0 if ccw else -1.0
    return ring if signed_area(ring) / s >= 0 else ring[::-1]


def orient(polygon: Polygon, ccw: bool = True) -> Polygon:  # noqa: FBT001, FBT002
    """
    Return a polygon with exteriors and interiors in the right orientation.

    if ccw is True than the exterior will be in counterclockwise orientation
    and the interiors will be in clockwise orientation, or
    the other way round when ccw is False.
    """
    shell = get_oriented_ring(polygon.exterior.coords, ccw)
    ccw = not ccw  # flip orientation for holes
    holes = [get_oriented_ring(ring.coords, ccw) for ring in polygon.interiors]
    return Polygon(shell=shell, holes=holes)


def box(
    minx: float,
    miny: float,
    maxx: float,
    maxy: float,
    ccw: bool = True,  # noqa: FBT001, FBT002
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
        GeoInterface,
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
    geometry = context if isinstance(context, dict) else mapping(context)
    if not geometry:
        msg = (  # type: ignore [unreachable]
            "Object does not implement __geo_interface__"
        )
        raise TypeError(msg)

    if constructor := type_map.get(geometry["type"]):
        return constructor._from_dict(  # type: ignore [attr-defined, no-any-return]
            geometry,
        )
    if geometry["type"] == "GeometryCollection":
        geometries = [shape(fi) for fi in geometry["geometries"]]
        return GeometryCollection(geometries)
    msg = f"[{geometry['type']} is not implemented"
    raise NotImplementedError(msg)


def num(number: str) -> float:
    """
    Return a float or integer from a string.

    Parameters
    ----------
    number : str
        a string representing a number

    Returns
    -------
    float or an integer if the string can be converted to an integer

    """
    f = float(number)
    return int(f) if int(f) == f else f


def _point_from_wkt_coordinates(coordinates: str) -> Point:
    coords = [num(c) for c in coordinates.split()]
    return Point(*coords)


def _line_from_wkt_coordinates(coordinates: str) -> LineString:
    coords = coordinates.split(",")
    return LineString(
        cast(
            LineType,  #
            [tuple(num(c) for c in coord.split()) for coord in coords],
        ),
    )


def _ring_from_wkt_coordinates(coordinates: str) -> LinearRing:
    coords = coordinates.split(",")
    return LinearRing(
        cast(
            LineType,
            [tuple(num(c) for c in coord.split()) for coord in coords],
        ),
    )


def _shell_holes_from_wkt_coords(
    coords: List[str],
) -> Tuple[LineType, Interiors]:
    """Extract shell and holes from polygon wkt coordinates."""
    exterior: LineType = cast(
        LineType,
        [tuple(num(c) for c in coord.split()) for coord in coords[0]],
    )
    if len(coords) > 1:
        # we have a polygon with holes
        interiors = [
            cast(
                LineType,
                [
                    cast(PointType, tuple(num(c) for c in coord.split()))
                    for coord in ext
                ],
            )
            for ext in coords[1:]
        ]
    else:
        interiors = None
    return exterior, interiors


def _polygon_from_wkt_coordinates(coordinates: str) -> Polygon:
    coords = [
        interior.strip("()").split(",") for interior in inner.findall(coordinates)
    ]
    interior, exteriors = _shell_holes_from_wkt_coords(coords)
    return Polygon(
        shell=interior,
        holes=exteriors,
    )


def _multipoint_from_wkt_coordinates(coordinates: str) -> MultiPoint:
    coords = [coord.strip().strip("()") for coord in coordinates.split(",")]
    return MultiPoint(
        [cast(PointType, tuple(num(c) for c in coord.split())) for coord in coords],
    )


def _multiline_from_wkt_coordinates(coordinates: str) -> MultiLineString:
    coords = [
        cast(
            LineType,
            [
                tuple(num(c) for c in coord.split())
                for coord in lines.strip("()").split(",")
            ],
        )
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
    geometries: List[Geometry] = []
    for gc_type, gc_coord in zip(gc_types, gc_coords):
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

    wkt = geo_str.upper().strip()
    wkt = " ".join(line.strip() for line in wkt.splitlines())
    try:
        wkt = wkt_regex.match(wkt).group("wkt")  # type: ignore [union-attr]
        geometry_type = wkt_regex.match(wkt).group("type")  # type: ignore [union-attr]
        outerstr = outer.search(wkt)
        coordinates = outerstr.group(1)  # type: ignore [union-attr]
    except AttributeError as exc:
        msg = f"Cannot parse {wkt}"
        raise WKTParserError(msg) from exc
    constructor = type_map[geometry_type]
    try:
        return constructor(coordinates)  # type: ignore [return-value]
    except TypeError as exc:
        msg = f"Cannot parse {wkt}"
        raise WKTParserError(msg) from exc


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
    {'type': 'Point', 'bbox': (0, 0, 0, 0), 'coordinates': (0, 0)}

    """
    return ob.__geo_interface__


def force_2d(
    context: Union[GeoType, GeoCollectionType],
) -> Union[Geometry, GeometryCollection]:
    """
    Force the dimensionality of a geometry to 2D.

    >>> force_2d(Point(0, 0, 1))
    Point(0, 0)
    >>> force_2d(Point(0, 0))
    Point(0, 0)
    >>> force_2d(LineString([(0, 0, 0), (0, 1, 1), (1, 1, 2)]))
    LineString(((0, 0), (0, 1), (1, 1)))
    """
    geometry = mapping(context)
    return shape(move_geo_interface(geometry, (0, 0)))


def force_3d(
    context: Union[GeoType, GeoCollectionType],
    z: float = 0,
) -> Union[Geometry, GeometryCollection]:
    """
    Force the dimensionality of a geometry to 3D.

    >>> force_3d(Point(0, 0))
    Point(0, 0, 0)
    >>> force_3d(Point(0, 0), 1)
    Point(0, 0, 1)
    >>> force_3d(Point(0, 0, 0))
    Point(0, 0, 0)
    >>> force_3d(LineString([(0, 0), (0, 1), (1, 1)]))
    LineString(((0, 0, 0), (0, 1, 0), (1, 1, 0)))
    """
    geometry = mapping(context)
    return shape(move_geo_interface(geometry, (0, 0, z)))


__all__ = [
    "force_2d",
    "force_3d",
    "box",
    "from_wkt",
    "mapping",
    "orient",
    "shape",
]
