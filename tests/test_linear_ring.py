"""Test LinearRing."""

from unittest import mock

import pytest

from pygeoif import exceptions
from pygeoif import functions
from pygeoif import geometry


def test_coords_get2d() -> None:
    ring = geometry.LinearRing([(0, 0), (1, 1), (2, 0)])

    assert ring.coords == ((0.0, 0.0), (1.0, 1.0), (2, 0), (0, 0))


def test_coords_get_3d() -> None:
    ring = geometry.LinearRing([(0, 0, 0), (1, 1, 1), (1, 2, 3)])

    assert ring.coords == ((0.0, 0.0, 0), (1.0, 1.0, 1), (1, 2, 3), (0, 0, 0))


def test_set_geoms_raises() -> None:
    ring = geometry.LinearRing([(0, 0), (1, 0)])  # pragma: no mutate

    with pytest.raises(
        exceptions.DimensionError,
        match="^All coordinates must have the same dimension$",
    ):
        ring._set_geoms([(0.0, 0.0, 0), (1.0, 1.0)])  # pragma: no mutate


def test_geo_interface() -> None:
    ring = geometry.LinearRing([(0, 0), (1, 1), (2, 2)])

    assert ring.__geo_interface__ == {
        "type": "LinearRing",
        "bbox": (0.0, 0.0, 2, 2),  # pragma: no mutate
        "coordinates": ((0.0, 0.0), (1.0, 1.0), (2, 2), (0, 0)),
    }


def test_bounds() -> None:
    ring = geometry.LinearRing([(1, 0), (3, 2)])

    assert ring.bounds == (1.0, 0.0, 3.0, 2.0)


def test_bounds3d() -> None:
    ring = geometry.LinearRing([(0, 0, 0), (1, 1, 3), (2, 2, 6)])  # pragma: no mutate

    assert ring.bounds == (0.0, 0.0, 2.0, 2.0)  # pragma: no mutate


def test_wkt() -> None:
    ring = geometry.LinearRing([(0, 0), (1, 1), (2, 2)])

    assert ring.wkt == "LINEARRING (0 0, 1 1, 2 2, 0 0)"


def test_wkt3d() -> None:
    ring = geometry.LinearRing([(0, 0, 0), (1, 1, 3), (2, 2, 6)])

    assert ring.wkt == "LINEARRING Z (0 0 0, 1 1 3, 2 2 6, 0 0 0)"


def test_from_dict() -> None:
    ring = geometry.LinearRing._from_dict(
        {
            "type": "LinearRing",
            "bbox": (0.0, 0.0, 1.0, 1.0),  # pragma: no mutate
            "coordinates": ((0.0, 0.0), (1.0, 1.0), (1, 2)),
        },
    )

    assert ring.coords == ((0.0, 0.0), (1.0, 1.0), (1, 2), (0, 0))


def test_from_compatible() -> None:
    not_a_geometry = mock.Mock(
        __geo_interface__={
            "type": "LinearRing",
            "coordinates": ((0.0, 0.0, 1.0), (1.0, 1.0, 2.0), (0, 4, 3)),
        },
    )

    ring = geometry.LinearRing._from_interface(not_a_geometry)

    assert isinstance(ring, geometry.LinearRing)
    assert ring.coords == ((0.0, 0.0, 1.0), (1.0, 1.0, 2.0), (0, 4, 3), (0, 0, 1))


def test_repr2d() -> None:
    ring = geometry.LinearRing([(0, 0), (1, 1), (2, 2)])

    assert repr(ring) == "LinearRing(((0, 0), (1, 1), (2, 2), (0, 0)))"


def test_repr3d() -> None:
    ring = geometry.LinearRing([(0, 0, 0), (1, 1, 3), (2, 2, 6)])

    assert repr(ring) == "LinearRing(((0, 0, 0), (1, 1, 3), (2, 2, 6), (0, 0, 0)))"


def test_repr_eval() -> None:
    ring = geometry.LinearRing([(0, 0, 0), (1, 1, 3), (2, 2, 6)])

    assert (
        eval(repr(ring), {}, {"LinearRing": geometry.LinearRing}).__geo_interface__
        == ring.__geo_interface__
    )


def test_signed_area() -> None:
    assert functions.signed_area(((0.0, 0.0), (1.0, 1.0), (2, 0), (0, 0))) == -1.0
    assert functions.signed_area(((0, 0, 5), (1, 0, 6), (1, 1, 7), (0, 0, 5))) == 0.5


def test_from_points() -> None:
    p1 = geometry.Point(0, 0)
    p2 = geometry.Point(1, 1)
    p3 = geometry.Point(0, 1)

    ring = geometry.LinearRing.from_points(p1, p2, p3)

    assert ring.coords == ((0, 0), (1, 1), (0, 1), (0, 0))


def test_convex_hull() -> None:
    line = geometry.LinearRing([(0, 0), (1, 1), (2, 2)])

    assert line.convex_hull == geometry.LineString([(0, 0), (2, 2)])


def test_convex_hull_3d() -> None:
    line = geometry.LinearRing([(0, 0, 0), (1, 1, 1), (2, 2, 2)])

    assert line.convex_hull == geometry.LineString([(0, 0), (2, 2)])


def test_convex_hull_3d_collapsed_to_point() -> None:
    line = geometry.LinearRing([(0, 0, 0), (0, 0, 1), (0, 0, 2)])

    assert line.convex_hull == geometry.Point(0, 0)


def test_convex_hull_linear_ring() -> None:
    line = geometry.LinearRing([(0, 0), (1, 0), (2, 2)])

    assert line.convex_hull == geometry.Polygon([(0, 0), (1, 0), (2, 2), (0, 0)])


def test_is_ccw() -> None:
    line = geometry.LinearRing([(0, 0), (1, 0), (1, 1), (0, 0)])

    assert line.is_ccw


def test_is_cw() -> None:
    line = geometry.LinearRing([(0, 0), (1, 1), (1, 0), (0, 0)])

    assert not line.is_ccw


def test_centroid_line() -> None:
    line = geometry.LinearRing([(0, 0), (0, 1)])

    assert line.centroid is None


def test_centroid_3d() -> None:
    line = geometry.LinearRing([(0, 0, 1), (2, 0, 2), (2, 2, 0), (0, 2, 0)])

    with pytest.raises(
        exceptions.DimensionError,
        match="^Centeroid is only implemented for 2D coordinates$",
    ):
        assert line.centroid


def test_centroid_crossing() -> None:
    line = geometry.LinearRing([(0, 0), (1, 0), (1, 1), (0, -1)])

    assert line.centroid is None


def test_centroid_valid() -> None:
    line = geometry.LinearRing([(0, 0), (4, 0), (4, 2), (0, 2)])

    assert line.centroid == geometry.Point(2, 1)


def test_empty() -> None:
    ring = geometry.LinearRing([])

    assert ring.is_empty


def test_empty_bounds() -> None:
    ring = geometry.LinearRing([])

    assert ring.bounds == ()
