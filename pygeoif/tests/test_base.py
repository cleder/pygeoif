"""Test Baseclass."""

import pytest

from pygeoif import geometry


def test_geometry_interface():
    """The geo interface must be implemented in subclasses."""
    base_geo = geometry._Geometry()

    with pytest.raises(NotImplementedError):
        assert base_geo.__geo_interface__


def test_bounds():
    """Subclasses must implement bounds."""
    base_geo = geometry._Geometry()
    with pytest.raises(NotImplementedError):

        assert base_geo.bounds


def test_wkt():
    """Implement wkt in subclasses."""
    base_geo = geometry._Geometry()
    with pytest.raises(NotImplementedError):

        assert base_geo.wkt


def test_wkt_inset():
    base_geo = geometry._Geometry()
    with pytest.raises(NotImplementedError):

        assert base_geo.wkt
