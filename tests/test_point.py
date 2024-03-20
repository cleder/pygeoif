"""Test Point."""

import math
from unittest import mock

import pytest

from pygeoif import geometry
from pygeoif.exceptions import DimensionError


def test_empty() -> None:
    point = geometry.Point(1, None)

    assert point.is_empty


def test_empty_nan() -> None:
    point = geometry.Point(1, math.nan, math.nan)

    assert point.is_empty


def test_bool() -> None:
    point = geometry.Point(1.0, 0.0)

    assert point


def test_bool_empty() -> None:
    point = geometry.Point(None, None)

    assert not point


def test_empty_wkt() -> None:
    point = geometry.Point(None, None)

    assert point.wkt == "POINT EMPTY"


def test_bounds() -> None:
    point = geometry.Point(1.0, 0.0)

    assert point.bounds == (1.0, 0, 1, 0)


def test_bounds3d() -> None:
    point = geometry.Point(1.0, 0.0, 3.0)  # pragma: no mutate

    assert point.bounds == (1, 0, 1, 0)


def test_xy() -> None:
    point = geometry.Point(1.0, 0.0)

    assert point.x == 1
    assert point.y == 0


def test_xy_raises_error_accessing_z() -> None:
    point = geometry.Point(1, 0)

    with pytest.raises(
        DimensionError,
        match=r"^The Point\(1, 0\) geometry does not have z values$",
    ):
        assert point.z


def test_xyz() -> None:
    point = geometry.Point(1.0, 0.0, 2.0)

    assert point.x == 1
    assert point.y == 0
    assert point.z == 2


def test_repr_empty() -> None:
    point = geometry.Point(None, None)

    assert repr(point) == "Point()"


def test_repr2d() -> None:
    point = geometry.Point(1, 0)

    assert repr(point) == "Point(1, 0)"
    assert not point.has_z


def test_repr3d() -> None:
    point = geometry.Point(1.0, 2.0, 3.0)

    assert repr(point) == "Point(1.0, 2.0, 3.0)"
    assert point.has_z


def test_has_z_2d() -> None:
    point = geometry.Point(1, 0)

    assert not point.has_z


def test_has_z_3d() -> None:
    point = geometry.Point(1.0, 2.0, 3.0)

    assert point.has_z


def test_repr_eval() -> None:
    point = geometry.Point(1.0, 2.0, 3.0)

    assert eval(repr(point), {}, {"Point": geometry.Point}) == point


def test_wkt2d() -> None:
    point = geometry.Point(1, 0)

    assert str(point) == "POINT (1 0)"


def test_wkt3d() -> None:
    point = geometry.Point(1.0, 0.0, 3.0)

    assert str(point) == "POINT Z (1.0 0.0 3.0)"


def test_coords_get() -> None:
    point = geometry.Point(1.0, 0.0, 3.0)

    assert point.coords == ((1, 0, 3),)


def test_geo_interface() -> None:
    point = geometry.Point(0, 1, 2)

    assert point.__geo_interface__ == {
        "type": "Point",
        "bbox": (0, 1, 0, 1),  # pragma: no mutate
        "coordinates": (0.0, 1.0, 2.0),
    }


def test_geo_interface_empty() -> None:
    point = geometry.Point(None, None)

    with pytest.raises(AttributeError, match="^Empty Geometry$"):
        assert point.__geo_interface__


def test_from_dict() -> None:
    point = geometry.Point._from_dict({"type": "Point", "coordinates": (0.0, 1.0, 2.0)})

    assert point.coords == ((0, 1, 2),)


def test_from_dict_wrong_type() -> None:
    with pytest.raises(ValueError, match="^You cannot assign Xoint to Point"):
        geometry.Point._from_dict(
            {"type": "Xoint", "coordinates": (0.0, 1.0, 2.0)},  # pragma: no mutate
        )


def test_from_compatible() -> None:
    not_a_geometry = mock.Mock()
    not_a_geometry.__geo_interface__ = {
        "type": "Point",
        "bbox": (0, 1, 0, 1),  # pragma: no mutate
        "coordinates": (0.0, 1.0, 2.0),
    }

    point = geometry.Point._from_interface(not_a_geometry)

    assert isinstance(point, geometry.Point)
    assert point.coords == ((0, 1, 2),)


def test_eq_interface() -> None:
    not_a_geometry = mock.Mock()
    not_a_geometry.__geo_interface__ = {
        "type": "Point",
        "coordinates": (0.0, 1.0, 2.0),
    }
    point = geometry.Point(0, 1, 2)

    assert point == not_a_geometry


def test_eq_floats() -> None:
    point1 = geometry.Point(0.3, 0.6)
    point2 = geometry.Point(0.2 + 0.1, 0.3 * 2)

    assert point1 == point2


def test_neq_missing_interface() -> None:
    point = geometry.Point(0, 1, 2)

    assert point != object()


def test_neq_interface_coords() -> None:
    not_a_geometry = mock.Mock()
    not_a_geometry.__geo_interface__ = {
        "type": "Point",
        "coordinates": (0.0, 1.0, 2.0),
    }
    point = geometry.Point(0, 0, 2)

    assert point != not_a_geometry


def test_convex_hull() -> None:
    point = geometry.Point(1, 0)

    assert point.convex_hull == point


def test_convex_hull_3d() -> None:
    point = geometry.Point(1, 2, 3)

    assert point.convex_hull == geometry.Point(1, 2)


def test_from_coordinates() -> None:
    point = geometry.Point(1, 2)

    assert geometry.Point.from_coordinates(point.coords) == point


def test_from_coordinates_3d() -> None:
    point = geometry.Point(1, 2, 3)

    assert geometry.Point.from_coordinates(point.coords) == point


def test_empty_bounds() -> None:
    point = geometry.Point(None, None)

    assert point.bounds == ()
