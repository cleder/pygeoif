"""Geometry Factories."""
import re
from typing import Union

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


def orient(polygon: Polygon, sign=1.0) -> Polygon:
    s = float(sign)
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


def as_shape(geometry) -> Union[Geometry, GeometryCollection]:
    """creates a pygeoif geometry from an object that
    provides the __geo_interface__ or a dictionary that
    is __geo_interface__ compatible"""
    gi = None
    if isinstance(geometry, dict):
        is_geometryCollection = geometry["type"] == "GeometryCollection"
        is_feature = geometry["type"] == "Feature"
        if (
            "coordinates" in geometry
            and "type" in geometry
            or is_geometryCollection
            and "geometries" in geometry
            or is_feature
        ):
            gi = geometry
    elif hasattr(geometry, "__geo_interface__"):
        gi = geometry.__geo_interface__
    else:
        try:
            # maybe we can convert it into a valid __geo_interface__ dict
            cdict = dict(geometry)
            is_geometryCollection = cdict["type"] == "GeometryCollection"
            if (
                "coordinates" in cdict
                and "type" in cdict
                or is_geometryCollection
                and "geometries" in cdict
            ):
                gi = cdict
        except:
            pass
    if not gi:
        raise TypeError("Object does not implement __geo_interface__")

    ft = gi["type"]
    if ft == "GeometryCollection":
        geometries = [as_shape(fi) for fi in gi["geometries"]]
        return GeometryCollection(geometries)
    if ft == "Feature":
        return Feature(
            as_shape(gi["geometry"]),
            properties=gi.get("properties", {}),
            feature_id=gi.get("id", None),
        )
    if ft == "FeatureCollection":
        features = [as_shape(fi) for fi in gi["features"]]
        return FeatureCollection(features)
    coords = gi["coordinates"]
    if ft == "Point":
        return Point(coords)
    elif ft == "LineString":
        return LineString(coords)
    elif ft == "LinearRing":
        return LinearRing(coords)
    elif ft == "Polygon":
        return Polygon(coords)
    elif ft == "MultiPoint":
        return MultiPoint(coords)
    elif ft == "MultiLineString":
        return MultiLineString(coords)
    elif ft == "MultiPolygon":
        polygons = [Polygon(icoords[0], icoords[1:]) for icoords in coords]
        return MultiPolygon(polygons)
    else:
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


def from_wkt(geo_str: str):
    """
    Create a geometry from its WKT representation
    """

    wkt = geo_str.strip()
    wkt = " ".join([l.strip() for l in wkt.splitlines()])
    wkt = wkt_regex.match(wkt).group("wkt")
    ftype = wkt_regex.match(wkt).group("type")
    outerstr = outer.search(wkt)
    coordinates = outerstr.group(1)
    if ftype == "POINT":
        coords = coordinates.split()
        return Point(coords)
    elif ftype == "LINESTRING":
        coords = coordinates.split(",")
        return LineString([c.split() for c in coords])
    elif ftype == "LINEARRING":
        coords = coordinates.split(",")
        return LinearRing([c.split() for c in coords])
    elif ftype == "POLYGON":
        coords = []
        for interior in inner.findall(coordinates):
            coords.append((interior[1:-1]).split(","))
        if len(coords) > 1:
            # we have a polygon with holes
            exteriors = []
            for ext in coords[1:]:
                exteriors.append([c.split() for c in ext])
        else:
            exteriors = None
        return Polygon([c.split() for c in coords[0]], exteriors)

    elif ftype == "MULTIPOINT":
        coords1 = coordinates.split(",")
        coords = []
        for coord in coords1:
            if "(" in coord:
                coord = coord[coord.find("(") + 1 : coord.rfind(")")]
            coords.append(coord.strip())
        return MultiPoint([c.split() for c in coords])
    elif ftype == "MULTILINESTRING":
        coords = []
        for lines in inner.findall(coordinates):
            coords.append([c.split() for c in lines[1:-1].split(",")])
        return MultiLineString(coords)
    elif ftype == "MULTIPOLYGON":
        polygons = []
        m = mpre.split(coordinates)
        for polygon in m:
            if len(polygon) < 3:
                continue
            coords = []
            for interior in inner.findall("(" + polygon + ")"):
                coords.append((interior[1:-1]).split(","))
            if len(coords) > 1:
                # we have a polygon with holes
                exteriors = []
                for ext in coords[1:]:
                    exteriors.append([c.split() for c in ext])
            else:
                exteriors = None
            polygons.append(Polygon([c.split() for c in coords[0]], exteriors))
        return MultiPolygon(polygons)
    elif ftype == "GEOMETRYCOLLECTION":
        gc_types = gcre.findall(coordinates)
        gc_coords = gcre.split(coordinates)[1:]
        assert len(gc_types) == len(gc_coords)
        geometries = []
        for (gc_type, gc_coord) in zip(gc_types, gc_coords):
            gc_wkt = gc_type + gc_coord[: gc_coord.rfind(")") + 1]
            geometries.append(from_wkt(gc_wkt))
        return GeometryCollection(geometries)
    else:
        raise NotImplementedError


def mapping(ob: GeoType) -> Union[GeoCollectionInterface, GeoInterface]:
    return ob.__geo_interface__
