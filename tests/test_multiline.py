"""Test MultiLineString."""

from pygeoif import geometry


def test_geoms() -> None:
    lines = geometry.MultiLineString(
        ([(0, 0), (1, 1), (1, 2), (2, 2)], [[0.0, 0.0], [1.0, 2.0]]),
    )

    for line in lines.geoms:
        assert type(line) is geometry.LineString


def test_len() -> None:
    lines = geometry.MultiLineString(
        ([(0, 0), (1, 1), (1, 2), (2, 2)], [[0.0, 0.0], [1.0, 2.0]]),
    )

    assert len(lines) == 2


def test_geo_interface() -> None:
    lines = geometry.MultiLineString(
        ([(0, 0), (1, 1), (1, 2), (2, 2)], [[0.0, 0.0], [1.0, 2.0]]),
    )

    assert lines.__geo_interface__ == {
        "type": "MultiLineString",
        "bbox": (0, 0, 2, 2),
        "coordinates": (((0, 0), (1, 1), (1, 2), (2, 2)), ((0.0, 0.0), (1.0, 2.0))),
    }


def test_from_dict() -> None:
    lines = geometry.MultiLineString._from_dict(
        {
            "type": "MultiLineString",
            "bbox": (0, 0, 2, 2),
            "coordinates": (((0, 0), (1, 1), (1, 2), (2, 2)), ((0.0, 0.0), (1.0, 2.0))),
        },
    )

    assert lines.__geo_interface__ == {
        "type": "MultiLineString",
        "bbox": (0, 0, 2, 2),
        "coordinates": (((0, 0), (1, 1), (1, 2), (2, 2)), ((0.0, 0.0), (1.0, 2.0))),
    }


def test_wkt() -> None:
    lines = geometry.MultiLineString(
        ([(0, 0), (1, 1), (1, 2), (2, 2)], [[0.0, 0.0], [1.0, 2.0]]),
    )

    assert lines.wkt == "MULTILINESTRING ((0 0, 1 1, 1 2, 2 2),(0.0 0.0, 1.0 2.0))"


def test_wkt_single_line() -> None:
    lines = geometry.MultiLineString(([(0, 0), (1, 1), (1, 2), (2, 2)],))

    assert lines.wkt == "MULTILINESTRING ((0 0, 1 1, 1 2, 2 2))"


def test_repr() -> None:
    lines = geometry.MultiLineString(([(0, 0), (1, 1)], [[0.0, 0.0], [1.0, 2.0]]))

    assert (
        repr(lines) == "MultiLineString((((0, 0), (1, 1)), ((0.0, 0.0), (1.0, 2.0))))"
    )


def test_repr_single_line() -> None:
    lines = geometry.MultiLineString(([(0, 0), (1, 1), (1, 2), (2, 2)],))

    assert repr(lines) == "MultiLineString((((0, 0), (1, 1), (1, 2), (2, 2)),))"


def test_unique() -> None:
    lines = geometry.MultiLineString(
        ([(0, 0), (1, 1), (1, 2), (2, 2)], [(0, 0), (1.0, 1.0), (1.0, 2.0), (2, 2)]),
        unique=True,
    )
    assert len(lines) == 1


def test_repr_eval() -> None:
    lines = geometry.MultiLineString(([(0, 0), (1, 1)], [[0.0, 0.0], [1.0, 2.0]]))

    assert (
        eval(
            repr(lines),
            {},
            {"MultiLineString": geometry.MultiLineString},
        ).__geo_interface__
        == lines.__geo_interface__
    )


def test_repr_eval_single_line() -> None:
    lines = geometry.MultiLineString(([(0, 0), (1, 1), (1, 2), (2, 2)],))

    assert (
        eval(
            repr(lines),
            {},
            {"MultiLineString": geometry.MultiLineString},
        ).__geo_interface__
        == lines.__geo_interface__
    )


def test_convex_hull() -> None:
    lines = geometry.MultiLineString(([(0, 0), (1, 1)], [[0.0, 0.0], [2.0, 2.0]]))

    assert lines.convex_hull == geometry.LineString([(0, 0), (2, 2)])


def test_convex_hull_3d() -> None:
    lines = geometry.MultiLineString(([(0, 0, 0), (1, 1, 1)], [[0, 0, 1], [2, 2, 2]]))

    assert lines.convex_hull == geometry.LineString([(0, 0), (2, 2)])


def test_convex_hull_3d_collapsed_to_point() -> None:
    lines = geometry.MultiLineString(([(0, 0, 0), (0, 0, 1)], [[0, 0, 2], [0, 0, 3]]))

    assert lines.convex_hull == geometry.Point(0, 0)


def test_convex_hull_linear_ring() -> None:
    lines = geometry.MultiLineString(([(0, 0), (1, 0)], [[1, 1], [2, 2]]))

    assert lines.convex_hull == geometry.Polygon([(0, 0), (1, 0), (2, 2), (0, 0)])


def test_from_linestrings() -> None:
    line1 = geometry.LineString([(0, 0, 0), (1, 1, 3), (2, 2, 6)])
    line2 = geometry.LineString([(0, 0), (1, 1), (2, 2)])
    lines = geometry.MultiLineString.from_linestrings(line1, line2)

    assert lines == geometry.MultiLineString(
        (((0, 0, 0), (1, 1, 3), (2, 2, 6)), ((0, 0), (1, 1), (2, 2))),
    )


def test_from_linestrings_unique() -> None:
    line1 = geometry.LineString([(0, 0, 0), (1, 1, 3), (2, 2, 6)])
    line2 = geometry.LineString([(0, 0), (1, 1), (2, 2)])
    lines = geometry.MultiLineString.from_linestrings(
        line1,
        line2,
        line1,
        line2,
        line1,
        unique=True,
    )

    assert lines == geometry.MultiLineString(
        (((0, 0, 0), (1, 1, 3), (2, 2, 6)), ((0, 0), (1, 1), (2, 2))),
        unique=True,
    )


def test_from_linestrings_non_unique() -> None:
    line1 = geometry.LineString([(0, 0, 0), (1, 1, 3), (2, 2, 6)])
    line2 = geometry.LineString([(0, 0), (1, 1), (2, 2)])
    lines = geometry.MultiLineString.from_linestrings(
        line1,
        line2,
        line1,
        line2,
        line1,
    )

    assert lines == geometry.MultiLineString(
        (
            ((0, 0, 0), (1, 1, 3), (2, 2, 6)),
            ((0, 0), (1, 1), (2, 2)),
            ((0, 0, 0), (1, 1, 3), (2, 2, 6)),
            ((0, 0), (1, 1), (2, 2)),
            ((0, 0, 0), (1, 1, 3), (2, 2, 6)),
        ),
        unique=False,
    )


def test_is_empty() -> None:
    lines = geometry.MultiLineString([])

    assert lines.is_empty


def test_repr_empty() -> None:
    lines = geometry.MultiLineString([])

    assert repr(lines) == "MultiLineString(())"


def test_empty_bounds() -> None:
    lines = geometry.MultiLineString([])

    assert lines.bounds == ()
