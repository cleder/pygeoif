"""Test MultiLineString."""
from pygeoif import geometry


def test_geoms():
    lines = geometry.MultiLineString(
        ([(0, 0), (1, 1), (1, 2), (2, 2)], [[0.0, 0.0], [1.0, 2.0]]),
    )

    for line in lines.geoms:
        assert type(line) == geometry.LineString


def test_len():
    lines = geometry.MultiLineString(
        ([(0, 0), (1, 1), (1, 2), (2, 2)], [[0.0, 0.0], [1.0, 2.0]]),
    )

    assert len(lines) == 2


def test_geo_interface():
    lines = geometry.MultiLineString(
        ([(0, 0), (1, 1), (1, 2), (2, 2)], [[0.0, 0.0], [1.0, 2.0]]),
    )

    assert lines.__geo_interface__ == {
        "type": "MultiLineString",
        "bbox": (0, 0, 2, 2),
        "coordinates": (((0, 0), (1, 1), (1, 2), (2, 2)), ((0.0, 0.0), (1.0, 2.0))),
    }


def test_from_dict():
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


def test_wkt():
    lines = geometry.MultiLineString(
        ([(0, 0), (1, 1), (1, 2), (2, 2)], [[0.0, 0.0], [1.0, 2.0]]),
    )

    assert lines.wkt == "MULTILINESTRING((0 0, 1 1, 1 2, 2 2),(0.0 0.0, 1.0 2.0))"


def test_wkt_single_line():
    lines = geometry.MultiLineString(([(0, 0), (1, 1), (1, 2), (2, 2)],))

    assert lines.wkt == "MULTILINESTRING((0 0, 1 1, 1 2, 2 2))"


def test_repr():
    lines = geometry.MultiLineString(([(0, 0), (1, 1)], [[0.0, 0.0], [1.0, 2.0]]))

    assert (
        repr(lines) == "MultiLineString((((0, 0), (1, 1)), ((0.0, 0.0), (1.0, 2.0))))"
    )


def test_repr_single_line():
    lines = geometry.MultiLineString(([(0, 0), (1, 1), (1, 2), (2, 2)],))

    assert repr(lines) == "MultiLineString((((0, 0), (1, 1), (1, 2), (2, 2)),))"


def test_repr_eval():
    lines = geometry.MultiLineString(([(0, 0), (1, 1)], [[0.0, 0.0], [1.0, 2.0]]))

    assert (
        eval(
            repr(lines),
            {},
            {"MultiLineString": geometry.MultiLineString},
        ).__geo_interface__
        == lines.__geo_interface__
    )


def test_repr_eval_single_line():
    lines = geometry.MultiLineString(([(0, 0), (1, 1), (1, 2), (2, 2)],))

    assert (
        eval(
            repr(lines),
            {},
            {"MultiLineString": geometry.MultiLineString},
        ).__geo_interface__
        == lines.__geo_interface__
    )
