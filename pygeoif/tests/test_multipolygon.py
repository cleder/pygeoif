"""Test MultiPolygon."""
from pygeoif import geometry


def test_geoms():
    polys = geometry.MultiPolygon(
        [
            (
                ((0.0, 0.0), (0.0, 1.0), (1.0, 1.0), (1.0, 0.0)),
                [((0.25, 0.25), (0.25, 0.5), (0.5, 0.5), (0.5, 0.25))],
            ),
        ],
    )

    for poly in polys.geoms:
        assert type(poly) is geometry.Polygon


def test_len():
    polys = geometry.MultiPolygon(
        [
            (
                ((0.0, 0.0), (0.0, 1.0), (1.0, 1.0), (1.0, 0.0)),
                [((0.1, 0.1), (0.1, 0.2), (0.2, 0.2), (0.2, 0.1))],
            ),
            (((0.0, 0.0), (0.0, 1.0), (1.0, 1.0), (1.0, 0.0)),),
        ],
    )

    assert len(polys) == 2


def test_geo_interface():
    polys = geometry.MultiPolygon(
        [
            (
                ((0.0, 0.0), (0.0, 1.0), (1.0, 1.0), (1.0, 0.0)),
                [((0.1, 0.1), (0.1, 0.2), (0.2, 0.2), (0.2, 0.1))],
            ),
        ],
    )
    assert polys.__geo_interface__ == {
        "type": "MultiPolygon",
        "bbox": (0.0, 0.0, 1.0, 1.0),
        "coordinates": (
            (
                ((0.0, 0.0), (0.0, 1.0), (1.0, 1.0), (1.0, 0.0), (0.0, 0.0)),
                ((0.1, 0.1), (0.1, 0.2), (0.2, 0.2), (0.2, 0.1), (0.1, 0.1)),
            ),
        ),
    }


def test_from_dict():
    polys = geometry.MultiPolygon._from_dict(
        {
            "type": "MultiPolygon",
            "bbox": (0.0, 0.0, 1.0, 1.0),
            "coordinates": (
                (
                    ((0.0, 0.0), (0.0, 1.0), (1.0, 1.0), (1.0, 0.0), (0.0, 0.0)),
                    ((0.1, 0.1), (0.1, 0.2), (0.2, 0.2), (0.2, 0.1), (0.1, 0.1)),
                ),
            ),
        },
    )

    assert polys.__geo_interface__ == {
        "type": "MultiPolygon",
        "bbox": (0.0, 0.0, 1.0, 1.0),
        "coordinates": (
            (
                ((0.0, 0.0), (0.0, 1.0), (1.0, 1.0), (1.0, 0.0), (0.0, 0.0)),
                ((0.1, 0.1), (0.1, 0.2), (0.2, 0.2), (0.2, 0.1), (0.1, 0.1)),
            ),
        ),
    }


def test_wkt():
    polys = geometry.MultiPolygon(
        [
            (
                ((0.0, 0.0), (0.0, 1.0), (1.0, 1.0), (1.0, 0.0)),
                [((0.1, 0.1), (0.1, 0.2), (0.2, 0.2), (0.2, 0.1))],
            ),
            (((0.0, 0.0), (0.0, 1.0), (1.0, 1.0), (1.0, 0.0)),),
        ],
    )

    assert polys.wkt == (
        "MULTIPOLYGON(((0.0 0.0, 0.0 1.0, 1.0 1.0, 1.0 0.0, 0.0 0.0),"
        "(0.1 0.1, 0.1 0.2, 0.2 0.2, 0.2 0.1, 0.1 0.1)),"
        "((0.0 0.0, 0.0 1.0, 1.0 1.0, 1.0 0.0, 0.0 0.0)))"
    )


def test_repr():
    polys = geometry.MultiPolygon(
        [
            (
                ((0.0, 0.0), (0.0, 1.0), (1.0, 1.0), (1.0, 0.0)),
                [((0.1, 0.1), (0.1, 0.2), (0.2, 0.2), (0.2, 0.1))],
            ),
            (((0.0, 0.0), (0.0, 1.0), (1.0, 1.0), (1.0, 0.0)),),
        ],
    )

    assert repr(polys) == (
        "MultiPolygon(((((0.0, 0.0), (0.0, 1.0), (1.0, 1.0), (1.0, 0.0), (0.0, 0.0)), "
        "(((0.1, 0.1), (0.1, 0.2), (0.2, 0.2), (0.2, 0.1), (0.1, 0.1)),)), "
        "(((0.0, 0.0), (0.0, 1.0), (1.0, 1.0), (1.0, 0.0), (0.0, 0.0)),)))"
    )


def test_repr_eval():
    polys = geometry.MultiPolygon(
        [
            (
                ((0.0, 0.0), (0.0, 1.0), (1.0, 1.0), (1.0, 0.0)),
                [((0.1, 0.1), (0.1, 0.2), (0.2, 0.2), (0.2, 0.1))],
            ),
            (((0.0, 0.0), (0.0, 1.0), (1.0, 1.0), (1.0, 0.0)),),
        ],
    )

    assert (
        eval(
            repr(polys),
            {},
            {"MultiPolygon": geometry.MultiPolygon},
        ).__geo_interface__
        == polys.__geo_interface__
    )


def test_convex_hull():
    polys = geometry.MultiPolygon(
        [
            (
                ((0.0, 0.0), (0.0, 1.0), (0.0, 0.0)),
                [((0.1, 0.1), (0.1, 0.2), (0.2, 0.2), (0.2, 0.1))],
            ),
            (((0.0, 0.0), (0.0, 2.0), (0, 0)),),
        ],
    )

    assert polys.convex_hull == geometry.LineString([(0.0, 0.0), (0.0, 2.0)])


def test_convex_hull_3d():
    polys = geometry.MultiPolygon(
        [
            (((0, 0, 1), (1, 1, 2), (0, 0, 1)),),
            (((0, 0, 3), (2, 2, 4), (0, 0, 3)),),
        ],
    )

    assert polys.convex_hull == geometry.LineString([(0, 0), (2, 2)])


def test_convex_hull_3d_collapsed_to_point():
    polys = geometry.MultiPolygon(
        [
            (((0, 0, 1), (0, 0, 2), (0, 0, 3)),),
            (((0, 0, 3), (0, 0, 4), (0, 0, 5)),),
        ],
    )

    assert polys.convex_hull == geometry.Point(0, 0)


def test_convex_hull_linear_ring():
    polys = geometry.MultiPolygon(
        [
            (((0, 0), (1, 0), (2, 2)),),
            (((0, 0), (1, 1), (1, 2)),),
        ],
    )

    assert polys.convex_hull == geometry.Polygon(
        [(0, 0), (1, 0), (2, 2), (1, 2), (0, 0)],
    )


def test_unique():
    polys = geometry.MultiPolygon(
        [
            (
                ((0.0, 0.0), (0.0, 1.0), (1.0, 1.0), (1.0, 0.0)),
                (((0.1, 0.1), (0.1, 0.2), (0.2, 0.2), (0.2, 0.1)),),
            ),
            (((0, 0), (0, 1), (1, 1), (1, 0)),),
            (
                ((0, 0), (0, 1), (1, 1), (1, 0)),
                (((0.1, 0.1), (0.1, 0.2), (0.2, 0.2), (0.2, 0.1)),),
            ),
            (((0.0, 0.0), (0.0, 1.0), (1.0, 1.0), (1.0, 0.0)),),
        ],
        unique=True,
    )

    assert len(polys) == 2


def test_from_polygons():
    e1 = [(0, 0), (0, 2), (2, 2), (2, 0), (0, 0)]
    i1 = [(1, 0), (0.5, 0.5), (1, 1), (1.5, 0.5), (1, 0)]
    i2 = [(1, 0), (0.5, 0.5), (1, 1), (1.5, 0.5), (1, 0)]
    polygon1 = geometry.Polygon(e1, [i1, i2])
    polygon2 = geometry.Polygon([(0, 0, 0), (1, 1, 0), (1, 0, 0), (0, 0, 0)])
    e = [(0, 0), (0, 2), (2, 2), (2, 0), (0, 0)]
    i = [(1, 0), (0.5, 0.5), (1, 1), (1.5, 0.5), (1, 0)]
    polygon3 = geometry.Polygon(e, [i])

    polys = geometry.MultiPolygon.from_polygons(polygon1, polygon2, polygon3)

    assert polys == geometry.MultiPolygon(
        (
            (
                ((0, 0), (0, 2), (2, 2), (2, 0), (0, 0)),
                (
                    ((1, 0), (0.5, 0.5), (1, 1), (1.5, 0.5), (1, 0)),
                    ((1, 0), (0.5, 0.5), (1, 1), (1.5, 0.5), (1, 0)),
                ),
            ),
            (((0, 0, 0), (1, 1, 0), (1, 0, 0), (0, 0, 0)),),
            (
                ((0, 0), (0, 2), (2, 2), (2, 0), (0, 0)),
                (((1, 0), (0.5, 0.5), (1, 1), (1.5, 0.5), (1, 0)),),
            ),
        ),
    )


def test_from_polygons_unique():
    e1 = [(0, 0), (0, 2), (2, 2), (2, 0), (0, 0)]
    i1 = [(1, 0), (0.5, 0.5), (1, 1), (1.5, 0.5), (1, 0)]
    i2 = [(1, 0), (0.5, 0.5), (1, 1), (1.5, 0.5), (1, 0)]
    polygon1 = geometry.Polygon(e1, [i1, i2])
    polygon2 = geometry.Polygon([(0, 0, 0), (1, 1, 0), (1, 0, 0), (0, 0, 0)])
    e = [(0, 0), (0, 2), (2, 2), (2, 0), (0, 0)]
    i = [(1, 0), (0.5, 0.5), (1, 1), (1.5, 0.5), (1, 0)]
    polygon3 = geometry.Polygon(e, [i])

    polys = geometry.MultiPolygon.from_polygons(
        polygon1,
        polygon2,
        polygon3,
        unique=True,
    )
    polys2 = geometry.MultiPolygon.from_polygons(
        polygon1,
        polygon2,
        polygon3,
        polygon1,
        polygon2,
        polygon3,
        unique=True,
    )

    assert polys == polys2


def test_is_empty():
    polys = geometry.MultiPolygon([])

    assert polys.is_empty
