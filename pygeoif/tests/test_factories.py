"""Test the geometry factories."""

import pytest

from pygeoif import factories
from pygeoif import geometry


def test_orient_true():
    ext = [(0, 0), (0, 2), (2, 2), (2, 0), (0, 0)]
    int_1 = [(0.5, 0.25), (1.5, 0.25), (1.5, 1.25), (0.5, 1.25), (0.5, 0.25)]
    int_2 = [(0.5, 1.25), (1, 1.25), (1, 1.75), (0.5, 1.75), (0.5, 1.25)]
    p = geometry.Polygon(ext, [int_1, int_2])
    p1 = factories.orient(p, True)
    assert list(p1.exterior.coords) == ext[::-1]
    interiors = list(p1.interiors)
    assert list(interiors[0].coords) == int_1[::-1]
    assert list(interiors[1].coords) == int_2[::-1]


def test_orient_unchanged():
    exterior = ((0, 0), (2, 0), (2, 2), (0, 2), (0, 0))
    interiors = [
        ((0.5, 0.25), (0.5, 1.25), (1.5, 1.25), (1.5, 0.25), (0.5, 0.25)),
        ((0.5, 1.25), (0.5, 1.75), (1, 1.75), (1, 1.25), (0.5, 1.25)),
    ]

    p = geometry.Polygon(exterior, interiors)

    p1 = factories.orient(p, True)
    assert p1.exterior.coords == exterior
    new_interiors = list(p1.interiors)
    assert new_interiors[0].coords == interiors[0]
    assert new_interiors[1].coords == interiors[1]


def test_orient_false():
    exterior = ((0, 0), (2, 0), (2, 2), (0, 2), (0, 0))
    interiors = [
        ((0.5, 0.25), (0.5, 1.25), (1.5, 1.25), (1.5, 0.25), (0.5, 0.25)),
        ((0.5, 1.25), (0.5, 1.75), (1, 1.75), (1, 1.25), (0.5, 1.25)),
    ]

    p = geometry.Polygon(exterior, interiors)
    p1 = factories.orient(p, False)
    assert p1.exterior.coords == exterior[::-1]
    new_interiors = list(p1.interiors)
    assert new_interiors[0].coords == interiors[0][::-1]
    assert new_interiors[1].coords == interiors[1][::-1]


def test_box():
    poly = factories.box(1, 2, 3, 4)

    assert poly.__geo_interface__ == {
        "type": "Polygon",
        "bbox": (1, 2, 3, 4),
        "coordinates": (((3, 2), (3, 4), (1, 4), (1, 2), (3, 2)),),
    }


def test_box_cw():
    poly = factories.box(1, 2, 3, 4, ccw=False)

    assert poly.__geo_interface__ == {
        "type": "Polygon",
        "bbox": (1, 2, 3, 4),
        "coordinates": (((1, 2), (1, 4), (3, 4), (3, 2), (1, 2)),),
    }


def test_shell_holes_from_wkt_coords():
    shell, holes = factories._shell_holes_from_wkt_coords(
        [
            ["0 0", "10 20", "30 40", "0 0"],
        ],
    )
    assert holes is None
    assert shell == [(0.0, 0.0), (10.0, 20.0), (30.0, 40.0), (0.0, 0.0)]


class TestWKT:

    # valid and supported WKTs
    wkt_ok = [
        "POINT(6 10)",
        "POINT M (1 1 80)",
        "LINESTRING(3 4,10 50,20 25)",
        "LINESTRING (30 10, 10 30, 40 40)",
        "MULTIPOLYGON (((10 10, 10 20, 20 20, 20 15, 10 10)),"
        "((60 60, 70 70, 80 60, 60 60 )))",
        """MULTIPOLYGON (((40 40, 20 45, 45 30, 40 40)),
              ((20 35, 45 20, 30 5, 10 10, 10 30, 20 35),
              (30 20, 20 25, 20 15, 30 20)))""",
        """MULTIPOLYGON (((30 20, 10 40, 45 40, 30 20)),
              ((15 5, 40 10, 10 20, 5 10, 15 5)))""",
        "MULTIPOLYGON(((0 0,10 0,10 10,0 10,0 0))," "((5 5,7 5,7 7,5 7, 5 5)))",
        "GEOMETRYCOLLECTION(POINT(10 10), POINT(30 30), " "LINESTRING(15 15, 20 20))",
    ]

    # these are valid WKTs but not supported
    wkt_fail = [
        "POINT ZM (1 1 5 60)",
        "POINT EMPTY",
        "MULTIPOLYGON EMPTY",
        "TIN (((0 0 0, 0 0 1, 0 1 0, 0 0 0)), ((0 0 0, 0 1 0, 1 1 0, 0 0 0)))",
    ]

    def test_point(self):
        p = factories.from_wkt("POINT (0.0 1.0)")
        assert isinstance(p, geometry.Point)
        assert p.x == 0.0
        assert p.y == 1.0
        assert p.wkt == "POINT (0.0 1.0)"
        assert str(p) == "POINT (0.0 1.0)"
        assert p.geom_type == "Point"

    def test_point_capitalized(self):
        pts = ["POINT (1 0)", "point (1 0)", "Point(1 0)", "pOinT(1 0)"]
        for pt in pts:
            assert factories.from_wkt(pt) == geometry.Point(1, 0)

    def test_linestring(self):
        line = factories.from_wkt(
            "LINESTRING(-72.991 46.177,-73.079 46.16,"
            "-73.146 46.124,-73.177 46.071,-73.164 46.044)",
        )
        assert (
            line.wkt == "LINESTRING (-72.991 46.177, "
            "-73.079 46.16, -73.146 46.124, "
            "-73.177 46.071, -73.164 46.044)"
        )
        assert isinstance(line, geometry.LineString)

    def test_linearring(self):
        r = factories.from_wkt("LINEARRING (0 0,0 1,1 0,0 0)")
        assert isinstance(r, geometry.LinearRing)
        assert r.wkt == "LINEARRING (0.0 0.0, 0.0 1.0, " "1.0 0.0, 0.0 0.0)"

    def test_polygon(self):
        p = factories.from_wkt(
            "POLYGON((-91.611 76.227,-91.543 76.217,"
            "-91.503 76.222,-91.483 76.221,-91.474 76.211,"
            "-91.484 76.197,-91.512 76.193,-91.624 76.2,"
            "-91.638 76.202,-91.647 76.211,-91.648 76.218,"
            "-91.643 76.221,-91.636 76.222,-91.611 76.227))",
        )
        assert p.exterior.coords[0][0] == -91.611
        assert p.exterior.coords[0] == p.exterior.coords[-1]
        assert len(p.exterior.coords) == 14
        p = factories.from_wkt(
            "POLYGON((1 1,5 1,5 5,1 5,1 1),(2 2, 3 2, 3 3, 2 3,2 2))",
        )
        assert p.exterior.coords[0] == p.exterior.coords[-1]
        assert p.exterior.coords[0] == (1.0, 1.0)
        assert len(list(p.interiors)) == 1
        assert list(p.interiors)[0].coords == (
            (2.0, 2.0),
            (3.0, 2.0),
            (3.0, 3.0),
            (2.0, 3.0),
            (2.0, 2.0),
        )
        assert (
            p.wkt == "POLYGON ((1.0 1.0, 5.0 1.0, 5.0 5.0, "
            "1.0 5.0, 1.0 1.0),(2.0 2.0, 3.0 2.0, "
            "3.0 3.0, 2.0 3.0, 2.0 2.0))"
        )
        p = factories.from_wkt("POLYGON ((30 10, 10 20, 20 40, 40 40, 30 10))")
        assert p.exterior.coords[0] == p.exterior.coords[-1]
        p = factories.from_wkt(
            """POLYGON ((35 10, 10 20, 15 40, 45 45, 35 10),
            (20 30, 35 35, 30 20, 20 30))""",
        )
        assert p.exterior.coords[0] == p.exterior.coords[-1]

    def test_multipoint(self):
        p = factories.from_wkt("MULTIPOINT(3.5 5.6,4.8 10.5)")
        assert isinstance(p, geometry.MultiPoint)
        assert list(p.geoms)[0].x == 3.5
        assert list(p.geoms)[1].y == 10.5
        assert p.wkt == "MULTIPOINT(3.5 5.6, 4.8 10.5)"
        p = factories.from_wkt("MULTIPOINT ((10 40), (40 30), " "(20 20), (30 10))")
        assert isinstance(p, geometry.MultiPoint)
        assert list(p.geoms)[0].x == 10.0
        assert list(p.geoms)[3].y == 10.0
        p = factories.from_wkt("MULTIPOINT (10 40, 40 30, 20 20, 30 10)")
        assert isinstance(p, geometry.MultiPoint)
        assert list(p.geoms)[0].x == 10.0
        assert list(p.geoms)[3].y == 10.0

    def test_multilinestring(self):
        p = factories.from_wkt(
            "MULTILINESTRING((3 4,10 50,20 25)," "(-5 -8,-10 -8,-15 -4))",
        )
        assert list(p.geoms)[0].coords == (((3, 4), (10, 50), (20, 25)))
        assert list(p.geoms)[1].coords == (((-5, -8), (-10, -8), (-15, -4)))
        assert (
            p.wkt == "MULTILINESTRING((3.0 4.0, 10.0 50.0, "
            "20.0 25.0),(-5.0 -8.0, "
            "-10.0 -8.0, -15.0 -4.0))"
        )
        p = factories.from_wkt(
            """MULTILINESTRING ((10 10, 20 20, 10 40),
            (40 40, 30 30, 40 20, 30 10))""",
        )

    def test_multipolygon(self):
        p = factories.from_wkt(
            "MULTIPOLYGON(((0 0,10 20,30 40,0 0),"
            "(1 1,2 2,3 3,1 1)),"
            "((100 100,110 110,120 120,100 100)))",
        )
        # two polygons: the first one has an interior ring
        assert len(list(p.geoms)) == 2
        assert list(p.geoms)[0].exterior.coords == (
            (0.0, 0.0),
            (10.0, 20.0),
            (30.0, 40.0),
            (0.0, 0.0),
        )
        assert list(list(p.geoms)[0].interiors)[0].coords == (
            (1.0, 1.0),
            (2.0, 2.0),
            (3.0, 3.0),
            (1.0, 1.0),
        )
        assert list(p.geoms)[1].exterior.coords == (
            (100.0, 100.0),
            (110.0, 110.0),
            (120.0, 120.0),
            (100.0, 100.0),
        )
        assert (
            p.wkt == "MULTIPOLYGON(((0.0 0.0, 10.0 20.0, "
            "30.0 40.0, 0.0 0.0),"
            "(1.0 1.0, 2.0 2.0, 3.0 3.0, 1.0 1.0)),"
            "((100.0 100.0, 110.0 110.0,"
            " 120.0 120.0, 100.0 100.0)))"
        )
        p = factories.from_wkt(
            "MULTIPOLYGON(((1 1,5 1,5 5,1 5,1 1),"
            "(2 2, 3 2, 3 3, 2 3,2 2)),((3 3,6 2,6 4,3 3)))",
        )
        assert len(list(p.geoms)) == 2
        p = factories.from_wkt(
            "MULTIPOLYGON (((30 20, 10 40, 45 40, 30 20)),"
            "((15 5, 40 10, 10 20, 5 10, 15 5)))",
        )
        assert p.__geo_interface__ == {
            "type": "MultiPolygon",
            "bbox": (5.0, 5.0, 45.0, 40.0),
            "coordinates": (
                (((30.0, 20.0), (10.0, 40.0), (45.0, 40.0), (30.0, 20.0)),),
                (
                    (
                        (15.0, 5.0),
                        (40.0, 10.0),
                        (10.0, 20.0),
                        (5.0, 10.0),
                        (15.0, 5.0),
                    ),
                ),
            ),
        }

    def test_geometrycollection(self):
        gc = factories.from_wkt(
            "GEOMETRYCOLLECTION(POINT(4 6), LINESTRING(4 6,7 10))",
        )
        assert len(list(gc.geoms)) == 2
        assert isinstance(list(gc.geoms)[0], geometry.Point)
        assert isinstance(list(gc.geoms)[1], geometry.LineString)
        assert (
            gc.wkt
            == "GEOMETRYCOLLECTION(POINT (4.0 6.0), LINESTRING (4.0 6.0, 7.0 10.0))"
        )

    def test_wkt_ok(self):
        for wkt in self.wkt_ok:
            factories.from_wkt(wkt)

    def test_wkt_fail(self):
        for wkt in self.wkt_fail:
            pytest.raises(factories.WKTParserError, factories.from_wkt, wkt)

    def test_wkt_tin(self):
        tin = "TIN (((0 0 0, 0 0 1, 0 1 0, 0 0 0)), ((0 0 0, 0 1 0, 1 1 0, 0 0 0)))"
        pytest.raises(factories.WKTParserError, factories.from_wkt, tin)


class TestAsShape:
    def test_point(self):
        f = geometry.Point(0, 1)
        s = factories.shape(f)
        assert f.__geo_interface__ == s.__geo_interface__

    def test_linestring(self):
        f = geometry.LineString([(0, 0), (1, 1)])
        s = factories.shape(f)
        assert f.__geo_interface__ == s.__geo_interface__

    def test_linearring(self):
        f = geometry.LinearRing([(0, 0), (1, 1), (1, 0), (0, 0)])
        s = factories.shape(f)
        assert f.__geo_interface__ == s.__geo_interface__

    def test_polygon(self):
        f = geometry.Polygon([(0, 0), (1, 1), (1, 0), (0, 0)])
        s = factories.shape(f)
        assert f.__geo_interface__ == s.__geo_interface__
        e = [(0, 0), (0, 2), (2, 2), (2, 0), (0, 0)]
        i = [(1, 0), (0.5, 0.5), (1, 1), (1.5, 0.5), (1, 0)]
        f = geometry.Polygon(e, [i])
        s = factories.shape(f)
        assert f.__geo_interface__ == s.__geo_interface__
        ext = [(0, 0), (0, 2), (2, 2), (2, 0), (0, 0)]
        int_1 = [(0.5, 0.25), (1.5, 0.25), (1.5, 1.25), (0.5, 1.25), (0.5, 0.25)]
        int_2 = [(0.5, 1.25), (1, 1.25), (1, 1.75), (0.5, 1.75), (0.5, 1.25)]
        f = geometry.Polygon(ext, [int_1, int_2])
        s = factories.shape(f)
        assert f.__geo_interface__ == s.__geo_interface__

    def test_multipoint(self):
        f = geometry.MultiPoint([[0.0, 0.0], [1.0, 2.0]])
        s = factories.shape(f)
        assert f.__geo_interface__ == s.__geo_interface__

    def test_multilinestring(self):
        f = geometry.MultiLineString([[[0.0, 0.0], [1.0, 2.0]]])
        s = factories.shape(f)
        assert f.__geo_interface__ == s.__geo_interface__
        assert (0, 0, 1, 2) == f.bounds

    def test_multipolygon(self):
        f = geometry.MultiPolygon(
            [
                (
                    ((0.0, 0.0), (0.0, 1.0), (1.0, 1.0), (1.0, 0.0)),
                    [((0.1, 0.1), (0.1, 0.2), (0.2, 0.2), (0.2, 0.1))],
                ),
            ],
        )
        s = factories.shape(f)
        assert f.__geo_interface__ == s.__geo_interface__

    def test_geometrycollection(self):
        p = geometry.Point(0, 1)
        line = geometry.LineString([(0, 0), (1, 1)])
        f = geometry.GeometryCollection([p, line])
        s = factories.shape(f)
        assert f.__geo_interface__ == s.__geo_interface__
        assert f.__geo_interface__["geometries"][0] == p.__geo_interface__
        assert f.__geo_interface__["geometries"][1] == line.__geo_interface__

    def test_nongeo(self):
        pytest.raises(AttributeError, factories.shape, "a")

    def test_empty_dict(self):
        pytest.raises(TypeError, factories.shape, {})

    def test_notimplemented_interface(self):
        f = {"type": "Tin", "geometries": (1, 2, 3)}
        pytest.raises(NotImplementedError, factories.shape, f)

    def test_dict_as_shape(self):
        f = geometry.MultiLineString([[[0.0, 0.0], [1.0, 2.0]]])
        s = factories.shape(f.__geo_interface__)
        assert f.__geo_interface__ == s.__geo_interface__
