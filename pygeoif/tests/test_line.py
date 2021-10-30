"""Test LineString."""
from unittest import mock

import pytest

from pygeoif import exceptions
from pygeoif import geometry


def test_coords_get2d():
    line = geometry.LineString([(0, 0), (1, 1)])

    assert line.coords == ((0.0, 0.0), (1.0, 1.0))


def test_coords_get_3d():
    line = geometry.LineString([(0, 0, 0), (1, 1, 1)])

    assert line.coords == ((0.0, 0.0, 0), (1.0, 1.0, 1))


def test_set_geoms_raises():
    line = geometry.LineString([(0, 0), (1, 0)])  # pragma: no mutate

    with pytest.raises(
        exceptions.DimensionError,
        match="^All coordinates must have the same dimension$",
    ):
        line._set_geoms([(0.0, 0.0, 0), (1.0, 1.0)])  # pragma: no mutate


def test_geo_interface():
    line = geometry.LineString([(0, 0), (1, 1)])

    assert line.__geo_interface__ == {
        "type": "LineString",
        "bbox": (0.0, 0.0, 1.0, 1.0),  # pragma: no mutate
        "coordinates": ((0.0, 0.0), (1.0, 1.0)),
    }


def test_bounds():
    line = geometry.LineString([(0, 0), (1, 1)])

    assert line.bounds == (0.0, 0.0, 1.0, 1.0)


def test_bounds3d():
    line = geometry.LineString([(0, 0, 0), (1, 1, 3), (2, 2, 6)])  # pragma: no mutate

    assert line.bounds == (0.0, 0.0, 2.0, 2.0)  # pragma: no mutate


def test_wkt():
    line = geometry.LineString([(0, 0), (1, 1), (2, 2)])

    assert line.wkt == "LINESTRING (0 0, 1 1, 2 2)"


def test_wkt3d():
    line = geometry.LineString([(0, 0, 0), (1, 1, 3), (2, 2, 6)])

    assert line.wkt == "LINESTRING Z (0 0 0, 1 1 3, 2 2 6)"


def test_from_dict():
    line = geometry.LineString._from_dict(
        {
            "type": "LineString",
            "bbox": (0.0, 0.0, 1.0, 1.0),  # pragma: no mutate
            "coordinates": ((0.0, 0.0), (1.0, 1.0)),
        },
    )

    assert line.coords == ((0.0, 0.0), (1.0, 1.0))


def test_from_compatible():
    not_a_geometry = mock.Mock(
        __geo_interface__={
            "type": "LineString",
            "coordinates": ((0.0, 0.0, 1.0), (1.0, 1.0, 2.0)),
        },
    )
    line = geometry.LineString._from_interface(not_a_geometry)
    assert line.coords == ((0.0, 0.0, 1.0), (1.0, 1.0, 2.0))


def test_repr2d():
    line = geometry.LineString([(0, 0), (1, 1), (2, 2)])

    assert repr(line) == "LineString(((0, 0), (1, 1), (2, 2)))"


def test_repr3d():
    line = geometry.LineString([(0, 0, 0), (1, 1, 3), (2, 2, 6)])

    assert repr(line) == "LineString(((0, 0, 0), (1, 1, 3), (2, 2, 6)))"


def test_repr_eval():
    line = geometry.LineString([(0, 0, 0), (1, 1, 3), (2, 2, 6)])

    assert (
        eval(repr(line), {}, {"LineString": geometry.LineString}).__geo_interface__
        == line.__geo_interface__
    )


def test_has_z_2d():
    line = geometry.LineString([(0, 0), (1, 1), (2, 2)])

    assert not line.has_z


def test_has_z_3d():
    line = geometry.LineString([(0, 0, 0), (1, 1, 3), (2, 2, 6)])

    assert line.has_z


def test_from_points():
    p1 = geometry.Point(0, 0)
    p2 = geometry.Point(1, 1)

    line = geometry.LineString.from_points(p1, p2)

    assert line.coords == ((0, 0), (1, 1))


def test_from_points_3d():
    p1 = geometry.Point(0, 0, 1)
    p2 = geometry.Point(1, 1, 2)

    line = geometry.LineString.from_points(p1, p2)

    assert line.coords == ((0, 0, 1), (1, 1, 2))


def test_from_points_mixed():
    p1 = geometry.Point(0, 0, 1)
    p2 = geometry.Point(1, 1)

    with pytest.raises(exceptions.DimensionError):
        geometry.LineString.from_points(p1, p2)


def test_convex_hull():
    line = geometry.LineString([(0, 0), (1, 1), (2, 2)])

    assert line.convex_hull == geometry.LineString([(0, 0), (2, 2)])


def test_convex_hull_3d():
    line = geometry.LineString([(0, 0, 0), (1, 1, 1), (2, 2, 2)])

    assert line.convex_hull == geometry.LineString([(0, 0), (2, 2)])


def test_convex_hull_3d_collapsed_to_point():
    line = geometry.LineString([(0, 0, 0), (0, 0, 1), (0, 0, 2)])

    assert line.convex_hull == geometry.Point(0, 0)


def test_convex_hull_linear_ring():
    line = geometry.LineString([(0, 0), (1, 0), (2, 2)])

    assert line.convex_hull == geometry.Polygon([(0, 0), (1, 0), (2, 2), (0, 0)])


def test_convex_hull_empty():
    line = geometry.LineString([])

    assert line.convex_hull is None


def test_from_coordinates():
    line = geometry.LineString([(0, 0), (1, 0), (2, 2)])

    assert geometry.LineString.from_coordinates(line.coords) == line


def test_maybe_valid():
    line = geometry.LineString([(0, 0), (1, 0)])

    assert line.maybe_valid


def test_maybe_valid_point():
    line = geometry.LineString([(0, 0), (0, 0)])

    assert not line.maybe_valid


def test_maybe_empty():
    line = geometry.LineString([])

    assert not line.maybe_valid


def test_empty():
    line = geometry.LineString([])

    assert line.is_empty


def test_empty_1_pt():
    line = geometry.LineString([(0, 0)])

    assert line.is_empty
