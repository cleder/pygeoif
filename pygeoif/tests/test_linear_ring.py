"""Test LinearRing."""
from unittest import mock

import pytest

from pygeoif import exceptions
from pygeoif import functions
from pygeoif import geometry


def test_coords_get2d():
    ring = geometry.LinearRing([(0, 0), (1, 1), (2, 0)])

    assert ring.coords == ((0.0, 0.0), (1.0, 1.0), (2, 0), (0, 0))


def test_coords_get_3d():
    ring = geometry.LinearRing([(0, 0, 0), (1, 1, 1), (1, 2, 3)])

    assert ring.coords == ((0.0, 0.0, 0), (1.0, 1.0, 1), (1, 2, 3), (0, 0, 0))


def test_set_geoms_raises():
    ring = geometry.LinearRing([(0, 0), (1, 0)])  # pragma: no mutate

    with pytest.raises(
        exceptions.DimensionError,
        match="^All coordinates must have the same dimension$",
    ):
        ring._set_geoms([(0.0, 0.0, 0), (1.0, 1.0)])  # pragma: no mutate


def test_geo_interface():
    ring = geometry.LinearRing([(0, 0), (1, 1), (2, 2)])

    assert ring.__geo_interface__ == {
        "type": "LinearRing",
        "bbox": (0.0, 0.0, 2, 2),  # pragma: no mutate
        "coordinates": ((0.0, 0.0), (1.0, 1.0), (2, 2), (0, 0)),
    }


def test_bounds():
    ring = geometry.LinearRing([(1, 0), (3, 2)])

    assert ring.bounds == (1.0, 0.0, 3.0, 2.0)


def test_bounds3d():
    ring = geometry.LinearRing([(0, 0, 0), (1, 1, 3), (2, 2, 6)])  # pragma: no mutate

    assert ring.bounds == (0.0, 0.0, 2.0, 2.0)  # pragma: no mutate


def test_wkt():
    ring = geometry.LinearRing([(0, 0), (1, 1), (2, 2)])

    assert ring.wkt == "LINEARRING (0 0, 1 1, 2 2, 0 0)"


def test_wkt3d():
    ring = geometry.LinearRing([(0, 0, 0), (1, 1, 3), (2, 2, 6)])

    assert ring.wkt == "LINEARRING Z (0 0 0, 1 1 3, 2 2 6, 0 0 0)"


def test_from_dict():
    ring = geometry.LinearRing._from_dict(
        {
            "type": "LinearRing",
            "bbox": (0.0, 0.0, 1.0, 1.0),  # pragma: no mutate
            "coordinates": ((0.0, 0.0), (1.0, 1.0), (1, 2)),
        },
    )

    assert ring.coords == ((0.0, 0.0), (1.0, 1.0), (1, 2), (0, 0))


def test_from_compatible():
    not_a_geometry = mock.Mock(
        __geo_interface__={
            "type": "LinearRing",
            "coordinates": ((0.0, 0.0, 1.0), (1.0, 1.0, 2.0), (0, 4, 3)),
        },
    )

    ring = geometry.LinearRing._from_interface(not_a_geometry)

    assert ring.coords == ((0.0, 0.0, 1.0), (1.0, 1.0, 2.0), (0, 4, 3), (0, 0, 1))


def test_repr2d():
    ring = geometry.LinearRing([(0, 0), (1, 1), (2, 2)])

    assert repr(ring) == "LinearRing(((0, 0), (1, 1), (2, 2), (0, 0)))"


def test_repr3d():
    ring = geometry.LinearRing([(0, 0, 0), (1, 1, 3), (2, 2, 6)])

    assert repr(ring) == "LinearRing(((0, 0, 0), (1, 1, 3), (2, 2, 6), (0, 0, 0)))"


def test_repr_eval():
    ring = geometry.LinearRing([(0, 0, 0), (1, 1, 3), (2, 2, 6)])

    assert (
        eval(repr(ring), {}, {"LinearRing": geometry.LinearRing}).__geo_interface__
        == ring.__geo_interface__
    )


def test_signed_area():
    assert functions.signed_area(((0.0, 0.0), (1.0, 1.0), (2, 0), (0, 0))) == -1.0
    assert functions.signed_area(((0, 0, 5), (1, 0, 6), (1, 1, 7), (0, 0, 5))) == 0.5


def test_from_points():
    p1 = geometry.Point(0, 0)
    p2 = geometry.Point(1, 1)
    p3 = geometry.Point(0, 1)

    ring = geometry.LinearRing.from_points(p1, p2, p3)

    assert ring.coords == ((0, 0), (1, 1), (0, 1), (0, 0))


def test_convex_hull():
    line = geometry.LinearRing([(0, 0), (1, 1), (2, 2)])

    assert line.convex_hull == geometry.LineString([(0, 0), (2, 2)])


def test_convex_hull_3d():
    line = geometry.LinearRing([(0, 0, 0), (1, 1, 1), (2, 2, 2)])

    assert line.convex_hull == geometry.LineString([(0, 0), (2, 2)])


def test_convex_hull_3d_collapsed_to_point():
    line = geometry.LinearRing([(0, 0, 0), (0, 0, 1), (0, 0, 2)])

    assert line.convex_hull == geometry.Point(0, 0)


def test_convex_hull_linear_ring():
    line = geometry.LinearRing([(0, 0), (1, 0), (2, 2)])

    assert line.convex_hull == geometry.Polygon([(0, 0), (1, 0), (2, 2), (0, 0)])


def test_maybe_valid_cossing():
    line = geometry.LinearRing([(0, 0), (1, 0), (1, 1), (0, -1)])

    assert not line.maybe_valid


def test_maybe_valid_no_area():
    line = geometry.LinearRing([(0, 0), (1, 1)])

    assert not line.maybe_valid


def test_maybe_valid_x_line():
    line = geometry.LinearRing([(0, 0), (1, 0)])

    assert not line.maybe_valid


def test_maybe_valid_y_line():
    line = geometry.LinearRing([(0, 0), (0, 1)])

    assert not line.maybe_valid


def test_maybe_valid_happy():
    line = geometry.LinearRing([(0, 0), (1, 0), (1, 1), (0, 0)])

    assert line.maybe_valid


def test_valid_3d():
    line = geometry.LinearRing([(0, 0, 1), (2, 0, 2), (2, 2, 0), (0, 2, 0)])

    with pytest.raises(
        exceptions.DimensionError,
        match="^Validation is only implemented for 2D coordinates$",
    ):
        assert line.maybe_valid


def test_is_ccw():
    line = geometry.LinearRing([(0, 0), (1, 0), (1, 1), (0, 0)])

    assert line.is_ccw


def test_is_cw():
    line = geometry.LinearRing([(0, 0), (1, 1), (1, 0), (0, 0)])

    assert not line.is_ccw


def test_centroid_line():
    line = geometry.LinearRing([(0, 0), (0, 1)])

    assert line.centroid is None


def test_centroid_3d():
    line = geometry.LinearRing([(0, 0, 1), (2, 0, 2), (2, 2, 0), (0, 2, 0)])

    with pytest.raises(
        exceptions.DimensionError,
        match="^Centeroid is only implemented for 2D coordinates$",
    ):
        assert line.centroid


def test_centroid_crossing():
    line = geometry.LinearRing([(0, 0), (1, 0), (1, 1), (0, -1)])

    assert line.centroid is None


def test_centroid_valid():
    line = geometry.LinearRing([(0, 0), (2, 0), (2, 2), (0, 2)])

    assert line.centroid == geometry.Point(1, 1)


def test_centroid_invalid():
    ring = geometry.LinearRing([(0, 0), (2, 0), (2, 2), (0, 2)])
    line = geometry.LineString(
        [
            (28, 16),
            (37, 31),
            (21, 50),
            (-21, 64),
            (-84, 64),
            (-148, 46),
            (-95, 10),
            (-72, 46),
            (-40, 64),
            (-9, 64),
            (12, 50),
            (20, 31),
            (15, 16),
        ],
    )
    ring._geoms = line._geoms

    assert ring.centroid is None


def test_empty():
    ring = geometry.LinearRing([])

    assert ring.is_empty
