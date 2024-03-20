"""Test the geometry factories."""

import pytest

from pygeoif import factories
from pygeoif import geometry


def test_num_int() -> None:
    assert factories.num("1") == 1
    assert isinstance(factories.num("1"), int)


def test_num_intf() -> None:
    assert factories.num("1.0") == 1
    assert isinstance(factories.num("1.0"), int)


def test_num_float() -> None:
    assert factories.num("1.1") == 1.1
    assert isinstance(factories.num("1.1"), float)


def test_force_2d_point() -> None:
    # 2d point to 2d point (no actual change)
    p = geometry.Point(-1, 1)
    p2d = factories.force_2d(p)
    assert p2d.x == -1
    assert p2d.y == 1
    assert not p2d.has_z

    # 3d point to 2d point
    p = geometry.Point(-1, 1, 2)
    p2d = factories.force_2d(p)
    assert p2d.x == -1
    assert p2d.y == 1
    assert not p2d.has_z


def test_force_2d_multipoint() -> None:
    # 2d to 2d (no actual change)
    p = geometry.MultiPoint([(-1, 1), (2, 3)])
    p2d = factories.force_2d(p)
    assert list(p2d.geoms) == [geometry.Point(-1, 1), geometry.Point(2, 3)]


def test_force_2d_linestring() -> None:
    # 2d line string to 2d line string (no actual change)
    ls = geometry.LineString([(1, 2), (3, 4)])
    l2d = factories.force_2d(ls)
    assert l2d.coords == ((1, 2), (3, 4))

    # 3d line string to 2d line string
    ls = geometry.LineString([(1, 2, 3), (4, 5, 6)])
    l2d = factories.force_2d(ls)
    assert l2d.coords == ((1, 2), (4, 5))


def test_force_2d_linearring() -> None:
    # 2d linear ring to 2d linear ring (no actual change)
    r = geometry.LinearRing([(1, 2), (3, 4)])
    r2d = factories.force_2d(r)
    assert r2d.coords == ((1, 2), (3, 4), (1, 2))

    # 3d linear ring to 2d linear ring
    r = geometry.LinearRing([(1, 2, 3), (4, 5, 6)])
    r2d = factories.force_2d(r)
    assert r2d.coords == ((1, 2), (4, 5), (1, 2))


def test_force_2d_multilinestring() -> None:
    # 2d multi line string to 2d multi line string (no actual change)
    mls = geometry.MultiLineString([[(1, 2), (3, 4)], [(5, 6), (7, 8)]])
    mls2d = factories.force_2d(mls)
    assert list(mls2d.geoms) == list(mls.geoms)

    # 3d multi line string to 2d multi line string
    mls = geometry.MultiLineString([[(1, 2, 3), (4, 5, 6)], [(7, 8, 9), (10, 11, 12)]])
    mls2d = factories.force_2d(mls)
    assert list(mls2d.geoms) == [
        geometry.LineString([(1, 2), (4, 5)]),
        geometry.LineString([(7, 8), (10, 11)]),
    ]


def test_force_2d_polygon() -> None:
    # 2d to 2d (no actual change)
    external = [(0, 0), (0, 2), (2, 2), (2, 0), (0, 0)]
    internal = [(0.5, 0.5), (0.5, 1.5), (1.5, 1.5), (1.5, 0.5), (0.5, 0.5)]
    p = geometry.Polygon(external, [internal])
    p2d = factories.force_2d(p)
    assert p2d.coords[0] == (((0, 0), (0, 2), (2, 2), (2, 0), (0, 0)))
    assert p2d.coords[1] == (
        ((0.5, 0.5), (0.5, 1.5), (1.5, 1.5), (1.5, 0.5), (0.5, 0.5)),
    )
    assert not p2d.has_z

    # 3d to 2d
    external = [(0, 0, 1), (0, 2, 1), (2, 2, 1), (2, 0, 1), (0, 0, 1)]
    internal = [
        (0.5, 0.5, 1),
        (0.5, 1.5, 1),
        (1.5, 1.5, 1),
        (1.5, 0.5, 1),
        (0.5, 0.5, 1),
    ]

    p = geometry.Polygon(external, [internal])
    p2d = factories.force_2d(p)
    assert p2d.coords[0] == (((0, 0), (0, 2), (2, 2), (2, 0), (0, 0)))
    assert p2d.coords[1] == (
        ((0.5, 0.5), (0.5, 1.5), (1.5, 1.5), (1.5, 0.5), (0.5, 0.5)),
    )
    assert not p2d.has_z


def test_force_2d_multipolygon() -> None:
    # 2d to 2d (no actual change)
    external = [(0, 0), (0, 2), (2, 2), (2, 0), (0, 0)]
    internal = [(0.5, 0.5), (0.5, 1.5), (1.5, 1.5), (1.5, 0.5), (0.5, 0.5)]
    mp = geometry.MultiPolygon([(external, [internal]), (external, [internal])])
    mp2d = factories.force_2d(mp)

    assert list(mp2d.geoms) == list(mp.geoms)


def test_force2d_collection() -> None:
    # 2d to 2d (no actual change)
    gc = geometry.GeometryCollection([geometry.Point(-1, 1), geometry.Point(-2, 2)])
    gc2d = factories.force_2d(gc)
    assert list(gc2d.geoms) == list(gc.geoms)

    # 3d to 2d
    gc = geometry.GeometryCollection(
        [geometry.Point(-1, 1, 0), geometry.Point(-2, 2, 0)],
    )
    gc2d = factories.force_2d(gc)
    assert list(gc2d.geoms) == [geometry.Point(-1, 1), geometry.Point(-2, 2)]


def test_force_2d_nongeo() -> None:
    pytest.raises(AttributeError, factories.force_2d, (1, 2, 3))


def test_force_3d_point() -> None:
    p = geometry.Point(0, 0)
    p3d = factories.force_3d(p)
    assert p3d.x == 0
    assert p3d.y == 0
    assert p3d.z == 0
    assert p3d.has_z


def test_force_3d_collection() -> None:
    gc = geometry.GeometryCollection(
        [geometry.Point(-1, 1), geometry.Point(-2, 2)],
    )
    gc3d = factories.force_3d(gc)
    assert list(gc3d.geoms) == [geometry.Point(-1, 1, 0), geometry.Point(-2, 2, 0)]


def test_force_3d_point_with_z() -> None:
    p = geometry.Point(0, 0, 1)
    p3d = factories.force_3d(p)
    assert p3d.x == 0
    assert p3d.y == 0
    assert p3d.z == 1
    assert p3d.has_z


def test_force_3d_point_noop() -> None:
    p = geometry.Point(1, 2, 3)
    p3d = factories.force_3d(p)
    assert p3d.x == 1
    assert p3d.y == 2
    assert p3d.z == 3
    assert p3d.has_z


def test_force_3d_nongeo() -> None:
    pytest.raises(AttributeError, factories.force_3d, (1, 2))


def test_orient_true() -> None:
    ext = [(0, 0), (0, 2), (2, 2), (2, 0), (0, 0)]
    int_1 = [(0.5, 0.25), (1.5, 0.25), (1.5, 1.25), (0.5, 1.25), (0.5, 0.25)]
    int_2 = [(0.5, 1.25), (1, 1.25), (1, 1.75), (0.5, 1.75), (0.5, 1.25)]
    p = geometry.Polygon(ext, [int_1, int_2])
    p1 = factories.orient(p, True)
    assert list(p1.exterior.coords) == ext[::-1]
    interiors = list(p1.interiors)
    assert list(interiors[0].coords) == int_1[::-1]
    assert list(interiors[1].coords) == int_2[::-1]


def test_orient_unchanged() -> None:
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


def test_orient_false() -> None:
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


def test_box() -> None:
    poly = factories.box(1, 2, 3, 4)

    assert poly.__geo_interface__ == {
        "type": "Polygon",
        "bbox": (1, 2, 3, 4),
        "coordinates": (((3, 2), (3, 4), (1, 4), (1, 2), (3, 2)),),
    }


def test_box_cw() -> None:
    poly = factories.box(1, 2, 3, 4, ccw=False)

    assert poly.__geo_interface__ == {
        "type": "Polygon",
        "bbox": (1, 2, 3, 4),
        "coordinates": (((1, 2), (1, 4), (3, 4), (3, 2), (1, 2)),),
    }


def test_shell_holes_from_wkt_coords() -> None:
    shell, holes = factories._shell_holes_from_wkt_coords(
        [
            ["0 0", "10 20", "30 40", "0 0"],  # type: ignore
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
        "MULTIPOLYGON (((0 0,10 0,10 10,0 10,0 0)),((5 5,7 5,7 7,5 7, 5 5)))",
        "GEOMETRYCOLLECTION (POINT(10 10), POINT(30 30), LINESTRING(15 15, 20 20))",
    ]

    # these are valid WKTs but not supported
    wkt_fail = [
        "POINT ZM (1 1 5 60)",
        "POINT EMPTY",
        "MULTIPOLYGON EMPTY",
        "TIN (((0 0 0, 0 0 1, 0 1 0, 0 0 0)), ((0 0 0, 0 1 0, 1 1 0, 0 0 0)))",
    ]

    def test_point(self) -> None:
        p = factories.from_wkt("POINT (0.0 1.0)")
        assert isinstance(p, geometry.Point)
        assert p.x == 0.0
        assert p.y == 1.0
        assert p.wkt == "POINT (0 1)"
        assert str(p) == "POINT (0 1)"
        assert p.geom_type == "Point"

    def test_point_capitalized(self) -> None:
        pts = ["POINT (1 0)", "point (1 0)", "Point(1 0)", "pOinT(1 0)"]
        for pt in pts:
            assert factories.from_wkt(pt) == geometry.Point(1, 0)

    def test_linestring(self) -> None:
        line = factories.from_wkt(
            "LINESTRING(-72.991 46.177,-73.079 46.16,"
            "-73.146 46.124,-73.177 46.071,-73.164 46.044)",
        )

        assert isinstance(line, geometry.LineString)
        assert (
            line.wkt == "LINESTRING (-72.991 46.177, "
            "-73.079 46.16, -73.146 46.124, "
            "-73.177 46.071, -73.164 46.044)"
        )

    def test_linearring(self) -> None:
        r = factories.from_wkt("LINEARRING (0 0,0 1,1 0,0 0)")

        assert isinstance(r, geometry.LinearRing)
        assert r.wkt == "LINEARRING (0 0, 0 1, 1 0, 0 0)"

    def test_polygon(self) -> None:
        p = factories.from_wkt(
            "POLYGON((-91.611 76.227,-91.543 76.217,"
            "-91.503 76.222,-91.483 76.221,-91.474 76.211,"
            "-91.484 76.197,-91.512 76.193,-91.624 76.2,"
            "-91.638 76.202,-91.647 76.211,-91.648 76.218,"
            "-91.643 76.221,-91.636 76.222,-91.611 76.227))",
        )

        assert isinstance(p, geometry.Polygon)
        assert p.exterior.coords[0][0] == -91.611
        assert p.exterior.coords[0] == p.exterior.coords[-1]
        assert len(p.exterior.coords) == 14

    def test_polygon_1(self) -> None:
        p = factories.from_wkt(
            "POLYGON((1 1,5 1,5 5,1 5,1 1),(2 2, 3 2, 3 3, 2 3,2 2))",
        )

        assert isinstance(p, geometry.Polygon)
        assert p.exterior.coords[0] == p.exterior.coords[-1]
        assert p.exterior.coords[0] == (1.0, 1.0)
        assert len(list(p.interiors)) == 1
        assert next(iter(p.interiors)).coords == (
            (2.0, 2.0),
            (3.0, 2.0),
            (3.0, 3.0),
            (2.0, 3.0),
            (2.0, 2.0),
        )
        assert (
            p.wkt == "POLYGON ((1 1, 5 1, 5 5, "
            "1 5, 1 1),(2 2, 3 2, "
            "3 3, 2 3, 2 2))"
        )

    def test_polygon_2(self) -> None:
        p = factories.from_wkt("POLYGON ((30 10, 10 20, 20 40, 40 40, 30 10))")

        assert isinstance(p, geometry.Polygon)
        assert p.exterior.coords[0] == p.exterior.coords[-1]

    def test_polygon_3(self) -> None:
        p = factories.from_wkt(
            """POLYGON ((35 10, 10 20, 15 40, 45 45, 35 10),
            (20 30, 35 35, 30 20, 20 30))""",
        )

        assert isinstance(p, geometry.Polygon)
        assert p.exterior.coords[0] == p.exterior.coords[-1]

    def test_multipoint(self) -> None:
        p = factories.from_wkt("MULTIPOINT(3.5 5.6,4.8 10.5)")
        assert isinstance(p, geometry.MultiPoint)
        assert next(iter(p.geoms)).x == 3.5
        assert list(p.geoms)[1].y == 10.5
        assert p.wkt == "MULTIPOINT (3.5 5.6, 4.8 10.5)"
        p = factories.from_wkt("MULTIPOINT ((10 40), (40 30), (20 20), (30 10))")
        assert isinstance(p, geometry.MultiPoint)
        assert next(iter(p.geoms)).x == 10.0
        assert list(p.geoms)[3].y == 10.0
        p = factories.from_wkt("MULTIPOINT (10 40, 40 30, 20 20, 30 10)")
        assert isinstance(p, geometry.MultiPoint)
        assert next(iter(p.geoms)).x == 10.0
        assert list(p.geoms)[3].y == 10.0

    def test_multilinestring(self) -> None:
        p = factories.from_wkt(
            "MULTILINESTRING ((3 4,10 50,20 25),(-5 -8,-10 -8,-15 -4))",
        )

        assert isinstance(p, geometry.MultiLineString)
        assert next(iter(p.geoms)).coords == (((3, 4), (10, 50), (20, 25)))
        assert list(p.geoms)[1].coords == (((-5, -8), (-10, -8), (-15, -4)))
        assert (
            p.wkt == "MULTILINESTRING ((3 4, 10 50, "
            "20 25),(-5 -8, "
            "-10 -8, -15 -4))"
        )

    def test_multilinestring_1(self) -> None:
        p = factories.from_wkt(
            """MULTILINESTRING ((10 10, 20 20, 10 40),
            (40 40, 30 30, 40 20, 30 10))""",
        )

        assert isinstance(p, geometry.MultiLineString)
        assert p.wkt == (
            "MULTILINESTRING ((10 10, 20 20, 10 40),(40 40, 30 30, 40 20, 30 10))"
        )

    def test_multipolygon(self) -> None:
        p = factories.from_wkt(
            "MULTIPOLYGON (((0 0,10 20,30 40,0 0),"
            "(1 1,2 2,3 3,1 1)),"
            "((100 100,110 110,120 120,100 100)))",
        )

        assert isinstance(p, geometry.MultiPolygon)
        # two polygons: the first one has an interior ring
        assert len(list(p.geoms)) == 2
        assert next(iter(p.geoms)).exterior.coords == (
            (0.0, 0.0),
            (10.0, 20.0),
            (30.0, 40.0),
            (0.0, 0.0),
        )
        assert next(iter(next(iter(p.geoms)).interiors)).coords == (
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
            p.wkt == "MULTIPOLYGON (((0 0, 10 20, "
            "30 40, 0 0),"
            "(1 1, 2 2, 3 3, 1 1)),"
            "((100 100, 110 110,"
            " 120 120, 100 100)))"
        )

    def test_multipolygon_1(self) -> None:
        p = factories.from_wkt(
            "MULTIPOLYGON(((1 1,5 1,5 5,1 5,1 1),"
            "(2 2, 3 2, 3 3, 2 3,2 2)),((3 3,6 2,6 4,3 3)))",
        )

        assert isinstance(p, geometry.MultiPolygon)
        assert len(list(p.geoms)) == 2

    def test_multipolygon_2(self) -> None:
        p = factories.from_wkt(
            "MULTIPOLYGON (((30 20, 10 40, 45 40, 30 20)),"
            "((15 5, 40 10, 10 20, 5 10, 15 5)))",
        )

        assert isinstance(p, geometry.MultiPolygon)
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

    def test_geometrycollection(self) -> None:
        gc = factories.from_wkt(
            "GEOMETRYCOLLECTION(POINT(4 6), LINESTRING(4 6,7 10))",
        )

        assert isinstance(gc, geometry.GeometryCollection)
        assert len(list(gc.geoms)) == 2
        assert isinstance(next(iter(gc.geoms)), geometry.Point)
        assert isinstance(list(gc.geoms)[1], geometry.LineString)
        assert gc.wkt == "GEOMETRYCOLLECTION (POINT (4 6), LINESTRING (4 6, 7 10))"

    def test_wkt_ok(self) -> None:
        for wkt in self.wkt_ok:
            factories.from_wkt(wkt)

    def test_wkt_fail(self) -> None:
        for wkt in self.wkt_fail:
            pytest.raises(factories.WKTParserError, factories.from_wkt, wkt)

    def test_wkt_tin(self) -> None:
        tin = "TIN (((0 0 0, 0 0 1, 0 1 0, 0 0 0)), ((0 0 0, 0 1 0, 1 1 0, 0 0 0)))"
        pytest.raises(factories.WKTParserError, factories.from_wkt, tin)


class TestAsShape:
    def test_point(self) -> None:
        f = geometry.Point(0, 1)
        s = factories.shape(f)
        assert f.__geo_interface__ == s.__geo_interface__

    def test_linestring(self) -> None:
        f = geometry.LineString([(0, 0), (1, 1)])
        s = factories.shape(f)
        assert f.__geo_interface__ == s.__geo_interface__

    def test_linearring(self) -> None:
        f = geometry.LinearRing([(0, 0), (1, 1), (1, 0), (0, 0)])
        s = factories.shape(f)
        assert f.__geo_interface__ == s.__geo_interface__

    def test_polygon(self) -> None:
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

    def test_multipoint(self) -> None:
        f = geometry.MultiPoint([[0.0, 0.0], [1.0, 2.0]])
        s = factories.shape(f)
        assert f.__geo_interface__ == s.__geo_interface__

    def test_multilinestring(self) -> None:
        f = geometry.MultiLineString([[[0.0, 0.0], [1.0, 2.0]]])
        s = factories.shape(f)
        assert f.__geo_interface__ == s.__geo_interface__
        assert f.bounds == (0, 0, 1, 2)

    def test_multipolygon(self) -> None:
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

    def test_geometrycollection(self) -> None:
        p = geometry.Point(0, 1)
        line = geometry.LineString([(0, 0), (1, 1)])
        f = geometry.GeometryCollection([p, line])
        s = factories.shape(f)
        assert f.__geo_interface__ == s.__geo_interface__
        assert f.__geo_interface__["geometries"][0] == p.__geo_interface__
        assert f.__geo_interface__["geometries"][1] == line.__geo_interface__

    def test_nongeo(self) -> None:
        pytest.raises(AttributeError, factories.shape, "a")

    def test_empty_dict(self) -> None:
        pytest.raises(TypeError, factories.shape, {})

    def test_notimplemented_interface(self) -> None:
        f = {"type": "Tin", "geometries": (1, 2, 3)}
        pytest.raises(NotImplementedError, factories.shape, f)

    def test_dict_as_shape(self) -> None:
        f = geometry.MultiLineString([[[0.0, 0.0], [1.0, 2.0]]])
        s = factories.shape(f.__geo_interface__)
        assert f.__geo_interface__ == s.__geo_interface__
