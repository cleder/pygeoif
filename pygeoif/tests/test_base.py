"""Test Baseclass."""
from unittest import mock

import pytest

from pygeoif import geometry


def test_geometry_interface() -> None:
    """The geo interface must be implemented in subclasses."""
    base_geo = geometry._Geometry()

    with pytest.raises(NotImplementedError, match="^Must be implemented by subclass$"):
        assert base_geo.__geo_interface__


def test_bounds() -> None:
    """Subclasses must implement bounds."""
    base_geo = geometry._Geometry()
    with pytest.raises(NotImplementedError, match="^Must be implemented by subclass$"):

        assert base_geo.bounds


def test_wkt() -> None:
    """Implement wkt in subclasses."""
    base_geo = geometry._Geometry()
    with pytest.raises(NotImplementedError, match="^Must be implemented by subclass$"):

        assert base_geo.wkt


def test_empty() -> None:
    base_geo = geometry._Geometry()
    with pytest.raises(NotImplementedError, match="^Must be implemented by subclass$"):

        assert base_geo.is_empty


def test_wkt_inset() -> None:
    base_geo = geometry._Geometry()

    assert base_geo._wkt_inset == ""


def test_wkt_coordinates() -> None:
    base_geo = geometry._Geometry()
    with pytest.raises(NotImplementedError, match="^Must be implemented by subclass$"):

        assert base_geo._wkt_coords


def test_from_dict() -> None:
    base_geo = geometry._Geometry()
    with pytest.raises(NotImplementedError, match="^Must be implemented by subclass$"):

        assert base_geo._from_dict({"type": "_Geometry"})


def test_has_z() -> None:
    base_geo = geometry._Geometry()
    with pytest.raises(NotImplementedError, match="^Must be implemented by subclass$"):

        assert base_geo.has_z


def test_convex_hull() -> None:
    with mock.patch("pygeoif.geometry._Geometry.has_z"):
        base_geo = geometry._Geometry()
        with pytest.raises(
            NotImplementedError,
            match="^Must be implemented by subclass$",
        ):

            assert base_geo.convex_hull


def test_get_bounds() -> None:
    base_geo = geometry._Geometry()
    with pytest.raises(NotImplementedError, match="^Must be implemented by subclass$"):

        assert base_geo._get_bounds()
