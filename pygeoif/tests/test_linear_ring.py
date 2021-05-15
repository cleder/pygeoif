"""Test LinearRing."""
from unittest import mock

import pytest

from pygeoif import geometry


def test_coords_get2d():
    ring = geometry.LinearRing([(0, 0), (1, 1), (2, 0)])

    assert ring.coords == ((0.0, 0.0), (1.0, 1.0), (2, 0), (0, 0))


def test_coords_get_3d():
    ring = geometry.LinearRing([(0, 0, 0), (1, 1, 1), (1, 2, 3)])

    assert ring.coords == ((0.0, 0.0, 0), (1.0, 1.0, 1), (1, 2, 3), (0, 0, 0))


def test_coords_set2d():
    ring = geometry.LinearRing([(0, 0), (1, 2), (0, 2)])  # pragma: no mutate
    ring.coords = ((0.0, 0.0), (1.0, 1.0), (2, 2))

    assert ring.coords == ((0.0, 0.0), (1.0, 1.0), (2, 2), (0, 0))


def test_coords_set_3d():
    ring = geometry.LinearRing([(0, 0), (1, 0), (1, 1)])  # pragma: no mutate
    ring.coords = ((0.0, 0.0, 0), (1.0, 1.0, 1), (1, 2, 1))

    assert ring.coords == ((0.0, 0.0, 0), (1.0, 1.0, 1), (1, 2, 1), (0, 0, 0))


def test_set_geoms_raises():
    ring = geometry.LinearRing([(0, 0), (1, 0)])  # pragma: no mutate

    with pytest.raises(
        ValueError, match="All coordinates must have the same dimension"
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
    ring = geometry.LinearRing([(0, 0), (1, 1)])

    assert ring.bounds == (0.0, 0.0, 1.0, 1.0)


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


def test_set_orientation():
    ring = geometry.LinearRing(((0, 0), (1, 1), (1, 0), (0, 0)))

    ring._set_orientation()

    assert ring.coords == ((0, 0), (1, 0), (1, 1), (0, 0))


def test_set_orientation_clockwise():
    ring = geometry.LinearRing(((0, 0), (1, 0), (1, 1), (0, 0)))

    ring._set_orientation(True)

    assert ring.coords == ((0, 0), (1, 1), (1, 0), (0, 0))


def test_set_orientation_3d():
    ring = geometry.LinearRing(((0, 0, 3), (1, 1, 2), (1, 0, 3), (0, 0, 3)))

    ring._set_orientation(False)

    assert ring.coords == ((0, 0, 3), (1, 0, 3), (1, 1, 2), (0, 0, 3))


def test_set_orientation_3d_clockwise():
    ring = geometry.LinearRing(((0, 0, 5), (1, 0, 6), (1, 1, 7), (0, 0, 5)))

    ring._set_orientation(True)

    assert ring.coords == ((0, 0, 5), (1, 1, 7), (1, 0, 6), (0, 0, 5))
