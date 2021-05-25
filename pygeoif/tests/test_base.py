"""Test Baseclass."""

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


def test_wkt_inset():
    base_geo = geometry._Geometry()

    assert base_geo._wkt_inset == ""


def test_wkt_cordinates():
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


def test_neq_no_interface():
    obj = object()
    base_geo = geometry._Geometry()

    assert base_geo != obj


def test_signed_area():
    a0 = [(0, 0), (0, 2), (2, 2), (2, 0), (0, 0)]
    a1 = [(0, 0, 1), (0, 2, 2), (2, 2, 3), (2, 0, 4), (0, 0, 1)]
    assert geometry.signed_area(a0) == geometry.signed_area(a1)


def test_signed_area_unequal_len():
    with pytest.raises(
        UnboundLocalError,
        match="^local variable 'xs' referenced before assignment$",
    ):
        a2 = [(0, 0, 1, 3), (0, 2, 2)]

        geometry.signed_area(a2)
