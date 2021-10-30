"""Test Baseclass."""
from unittest import mock

import pytest

from pygeoif import geometry


def test_geometry_interface():
    """The geo interface must be implemented in subclasses."""
    base_geo = geometry._Geometry()

    with pytest.raises(NotImplementedError, match="^Must be implemented by subclass$"):
        assert base_geo.__geo_interface__


def test_bounds():
    """Subclasses must implement bounds."""
    base_geo = geometry._Geometry()
    with pytest.raises(NotImplementedError, match="^Must be implemented by subclass$"):

        assert base_geo.bounds


def test_wkt():
    """Implement wkt in subclasses."""
    base_geo = geometry._Geometry()
    with pytest.raises(NotImplementedError, match="^Must be implemented by subclass$"):

        assert base_geo.wkt


def test_empty():
    base_geo = geometry._Geometry()
    with pytest.raises(NotImplementedError, match="^Must be implemented by subclass$"):

        assert base_geo.is_empty


def test_wkt_inset():
    base_geo = geometry._Geometry()

    assert base_geo._wkt_inset == ""


def test_wkt_coordinates():
    base_geo = geometry._Geometry()
    with pytest.raises(NotImplementedError, match="^Must be implemented by subclass$"):

        assert base_geo._wkt_coords


def test_from_dict():
    base_geo = geometry._Geometry()
    with pytest.raises(NotImplementedError, match="^Must be implemented by subclass$"):

        assert base_geo._from_dict({"type": "_Geometry"})


def test_has_z():
    base_geo = geometry._Geometry()
    with pytest.raises(NotImplementedError, match="^Must be implemented by subclass$"):

        assert base_geo.has_z


def test_convex_hull():
    with mock.patch("pygeoif.geometry._Geometry.has_z"):
        base_geo = geometry._Geometry()
        with pytest.raises(
            NotImplementedError,
            match="^Must be implemented by subclass$",
        ):

            assert base_geo.convex_hull
