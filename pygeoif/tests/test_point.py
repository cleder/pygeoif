"""Test Point."""
import pytest
from pygeoif import geometry


def test_bounds():
    point = geometry.Point(1.0, 0.0)

    assert point.bounds == (1.0, 0, 1, 0)


def test_xy():
    point = geometry.Point(1.0, 0.0)

    assert point.x == 1
    assert point.y == 0
    with pytest.raises(IndexError):
        point.z


def test_xyz():
    point = geometry.Point(1.0, 0.0, 2.0)

    assert point.x == 1
    assert point.y == 0
    assert point.z == 2


def test_repr2d():
    point = geometry.Point(1, 0)

    assert repr(point) == "Point(1, 0)"


def test_repr3d():
    point = geometry.Point(1.0, 2.0, 3.0)

    assert repr(point) == "Point(1.0, 2.0, 3.0)"


def test_wkt2d():
    point = geometry.Point(1, 0)

    assert str(point) == "POINT (1 0)"


def test_wkt3d():
    point = geometry.Point(1.0, 0.0, 3.0)

    assert str(point) == "POINT (1.0 0.0 3.0)"


def test_coords_get():
    point = geometry.Point(1.0, 0.0, 3.0)

    assert point.coords == ((1, 0, 3),)


def test_coords_set():
    point = geometry.Point(1.0, 0.0, 3.0)
    point.coords = ((4, 5))

    assert point.coords == ((4, 5),)
