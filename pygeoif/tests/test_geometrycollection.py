"""Test Baseclass."""

import pytest

from pygeoif import geometry


def test_geo_interface():
    poly1 = geometry.Polygon([(0, 0), (1, 1), (1, 0), (0, 0)])
    e = [(0, 0), (0, 2), (2, 2), (2, 0), (0, 0)]
    i = [(1, 0), (0.5, 0.5), (1, 1), (1.5, 0.5), (1, 0)]
    poly2 = geometry.Polygon(e, [i])
    p0 = geometry.Point(0, 0)
    p1 = geometry.Point(-1, -1)
    ring = geometry.LinearRing([(0, 0), (1, 1), (1, 0), (0, 0)])
    line = geometry.LineString([(0, 0), (1, 1)])
    gc = geometry.GeometryCollection([poly1, poly2, p0, p1, ring, line])

    assert gc.__geo_interface__ == {
        "geometries": (
            {
                "bbox": (0, 0, 1, 1),
                "coordinates": (((0, 0), (1, 1), (1, 0), (0, 0)),),
                "type": "Polygon",
            },
            {
                "bbox": (0, 0, 2, 2),
                "coordinates": (
                    ((0, 0), (0, 2), (2, 2), (2, 0), (0, 0)),
                    ((1, 0), (0.5, 0.5), (1, 1), (1.5, 0.5), (1, 0)),
                ),
                "type": "Polygon",
            },
            {"bbox": (0, 0, 0, 0), "coordinates": (0, 0), "type": "Point"},
            {"bbox": (-1, -1, -1, -1), "coordinates": (-1, -1), "type": "Point"},
            {
                "bbox": (0, 0, 1, 1),
                "coordinates": ((0, 0), (1, 1), (1, 0), (0, 0)),
                "type": "LinearRing",
            },
            {
                "bbox": (0, 0, 1, 1),
                "coordinates": ((0, 0), (1, 1)),
                "type": "LineString",
            },
        ),
        "type": "GeometryCollection",
    }


def test_geo_wkt():
    poly1 = geometry.Polygon([(0, 0), (1, 1), (1, 0), (0, 0)])
    e = [(0, 0), (0, 2), (2, 2), (2, 0), (0, 0)]
    i = [(1, 0), (0.5, 0.5), (1, 1), (1.5, 0.5), (1, 0)]
    poly2 = geometry.Polygon(e, [i])
    p0 = geometry.Point(0, 0)
    p1 = geometry.Point(-1, -1)
    ring = geometry.LinearRing([(0, 0), (1, 1), (1, 0), (0, 0)])
    line = geometry.LineString([(0, 0), (1, 1)])
    gc = geometry.GeometryCollection([poly1, poly2, p0, p1, ring, line])

    assert gc.wkt == (
        "GEOMETRYCOLLECTION"
        "(POLYGON ((0 0, 1 1, 1 0, 0 0)), "
        "POLYGON ((0 0, 0 2, 2 2, 2 0, 0 0),(1 0, 0.5 0.5, 1 1, 1.5 0.5, 1 0)), "
        "POINT (0 0), POINT (-1 -1), "
        "LINEARRING (0 0, 1 1, 1 0, 0 0), "
        "LINESTRING (0 0, 1 1))"
    )

def test_len():
    poly1 = geometry.Polygon([(0, 0), (1, 1), (1, 0), (0, 0)])
    e = [(0, 0), (0, 2), (2, 2), (2, 0), (0, 0)]
    i = [(1, 0), (0.5, 0.5), (1, 1), (1.5, 0.5), (1, 0)]
    poly2 = geometry.Polygon(e, [i])
    p0 = geometry.Point(0, 0)
    p1 = geometry.Point(-1, -1)
    ring = geometry.LinearRing([(0, 0), (1, 1), (1, 0), (0, 0)])
    line = geometry.LineString([(0, 0), (1, 1)])
    gc = geometry.GeometryCollection([poly1, poly2, p0, p1, ring, line])

    assert len(gc) == 6

def test_iter():
    poly1 = geometry.Polygon([(0, 0), (1, 1), (1, 0), (0, 0)])
    e = [(0, 0), (0, 2), (2, 2), (2, 0), (0, 0)]
    i = [(1, 0), (0.5, 0.5), (1, 1), (1.5, 0.5), (1, 0)]
    poly2 = geometry.Polygon(e, [i])
    p0 = geometry.Point(0, 0)
    p1 = geometry.Point(-1, -1)
    ring = geometry.LinearRing([(0, 0), (1, 1), (1, 0), (0, 0)])
    line = geometry.LineString([(0, 0), (1, 1)])
    gc = geometry.GeometryCollection([poly1, poly2, p0, p1, ring, line])

    for k, v in zip(gc, [poly1, poly2, p0, p1, ring, line]):
        assert k == v

def test_geoms():
    poly1 = geometry.Polygon([(0, 0), (1, 1), (1, 0), (0, 0)])
    e = [(0, 0), (0, 2), (2, 2), (2, 0), (0, 0)]
    i = [(1, 0), (0.5, 0.5), (1, 1), (1.5, 0.5), (1, 0)]
    poly2 = geometry.Polygon(e, [i])
    p0 = geometry.Point(0, 0)
    p1 = geometry.Point(-1, -1)
    ring = geometry.LinearRing([(0, 0), (1, 1), (1, 0), (0, 0)])
    line = geometry.LineString([(0, 0), (1, 1)])
    gc = geometry.GeometryCollection([poly1, poly2, p0, p1, ring, line])

    for k, v in zip(gc.geoms, [poly1, poly2, p0, p1, ring, line]):
        assert k == v
