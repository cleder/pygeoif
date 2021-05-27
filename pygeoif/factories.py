"""Geometry Factories."""
import re
from typing import Union, Optional

from pygeoif.types import GeoCollectionInterface
from pygeoif.types import GeoInterface
from pygeoif.types import GeoType

from .feature import Feature
from .feature import FeatureCollection
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
    geometry: Union[GeoType, GeoCollectionInterface, GeoCollectionInterface],
) -> Union[Geometry, GeometryCollection]:
    """Creates a pygeoif geometry from an object that
    provides the __geo_interface__ or a dictionary that
    is __geo_interface__ compatible"""
    mapping = {
        "Point": Point,
        "LineString": LineString,
        "LinearRing": LinearRing,
        "Polygon": Polygon,
        "MultiPoint": MultiPoint,
        "MultiLineString": MultiLineString,
        "MultiPolygon": MultiPolygon,
    }
    gi = None
    if isinstance(geometry, dict):
        is_geometryCollection = geometry["type"] == "GeometryCollection"
        if (
            "coordinates" in geometry
            and "type" in geometry
            or is_geometryCollection
            and "geometries" in geometry
        ):
            gi = geometry
    elif hasattr(geometry, "__geo_interface__"):
        gi = geometry.__geo_interface__
    if not gi:
        raise TypeError("Object does not implement __geo_interface__")

    func = mapping.get(gi["type"])
    if func:
        return func._from_dict(gi)
    if gi["type"] == "GeometryCollection":
        geometries = [shape(fi) for fi in gi["geometries"]]
        return GeometryCollection(geometries)

    raise NotImplementedError


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

outer = re.compile("\((.+)\)")
inner = re.compile("\([^)]*\)")
mpre = re.compile("\(\((.+?)\)\)")


def _point_from_wkt_coordinates(coordinates: str) -> Point:
    coords = [float(c) for c in coordinates.split()]
    return Point(*coords)


def _line_from_wkt_coordinates(coordinates: str) -> LineString:
    coords = coordinates.split(",")
    return LineString([[float(c) for c in coord.split()] for coord in coords])


def _ring_from_wkt_coordinates(coordinates: str) -> LinearRing:
    coords = coordinates.split(",")
    return LinearRing([[float(c) for c in coord.split()] for coord in coords])


def _polygon_from_wkt_coordinates(coordinates: str) -> Polygon:
    coords = [
        (interior.strip("()")).split(",") for interior in inner.findall(coordinates)
    ]

    if len(coords) > 1:
        # we have a polygon with holes
        exteriors = [
            [[float(c) for c in coord.split()] for coord in ext] for ext in coords[1:]
        ]
    else:
        exteriors = None
    return Polygon(
        [[float(c) for c in coord.split()] for coord in coords[0]], exteriors
    )


def _multipoint_from_wkt_coordinates(coordinates) -> MultiPoint:
    coords = [coord.strip().strip("()") for coord in coordinates.split(",")]
    return MultiPoint([[float(c) for c in coord.split()] for coord in coords])


def _multiline_from_wkt_coordinates(coordinates: str) -> MultiLineString:
    coords = [
        [[float(c) for c in coord.split()] for coord in lines[1:-1].split(",")]
        for lines in inner.findall(coordinates)
    ]
    return MultiLineString(coords)


def _multipolygon_from_wkt_coordinates(coordinates) -> MultiPolygon:
    polygons = []
    m = mpre.split(coordinates)
    for polygon in m:
        if len(polygon) < 3:
            continue
        coords = [
            (interior.strip("()")).split(",")
            for interior in inner.findall(f"({polygon})")
        ]
        if len(coords) > 1:
            # we have a polygon with holes
            exteriors = [
                [[float(c) for c in coord.split()] for coord in ext]
                for ext in coords[1:]
            ]
            polygons.append(
                [[[float(c) for c in coord.split()] for coord in coords[0]], exteriors]
            )
        else:
            polygons.append(
                [[[float(c) for c in coord.split()] for coord in coords[0]]]
            )
    return MultiPolygon(polygons)


def from_wkt(geo_str: str) -> Optional[Union[Geometry, GeometryCollection]]:
    """
    Create a geometry from its WKT representation
    """
    mapping = {
        "POINT": _point_from_wkt_coordinates,
        "LINESTRING": _line_from_wkt_coordinates,
        "LINEARRING": _ring_from_wkt_coordinates,
        "POLYGON": _polygon_from_wkt_coordinates,
        "MULTIPOINT": _multipoint_from_wkt_coordinates,
        "MULTILINESTRING": _multiline_from_wkt_coordinates,
        "MULTIPOLYGON": _multipolygon_from_wkt_coordinates,
    }

    wkt = geo_str.strip()
    wkt = " ".join(l.strip() for l in wkt.splitlines())
    wkt = wkt_regex.match(wkt).group("wkt")
    ftype = wkt_regex.match(wkt).group("type")
    outerstr = outer.search(wkt)
    coordinates = outerstr.group(1)
    if ftype == "GEOMETRYCOLLECTION":
        gc_types = gcre.findall(coordinates)
        gc_coords = gcre.split(coordinates)[1:]
        assert len(gc_types) == len(gc_coords)
        geometries = []
        for (gc_type, gc_coord) in zip(gc_types, gc_coords):
            gc_wkt = gc_type + gc_coord[: gc_coord.rfind(")") + 1]
            geometries.append(from_wkt(gc_wkt))
        return GeometryCollection(geometries)
    func = mapping.get(ftype)
    if func:
        return func(coordinates)


def mapping(ob: GeoType) -> Union[GeoCollectionInterface, GeoInterface]:
    return ob.__geo_interface__
