import pytest
from pygeoif import geometry


def test_geometry_interface():
    """The geo interface must be implemented in subclasses."""
    base_geo = geometry._Geometry()
    assert base_geo.__geo_interface__ == {
        "type": "_Geometry",
        "coordinates": (),
    }


def test_bounds():
    """Subclasses must implement bounds."""
    base_geo = geometry._Geometry()
    with pytest.raises(NotImplementedError):
        base_geo.bounds


def test_wkt():
    """Implement wkt in subclasses."""
    base_geo = geometry._Geometry()
    with pytest.raises(NotImplementedError):
        base_geo.wkt
