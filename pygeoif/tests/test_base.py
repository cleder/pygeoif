import unittest
from pygeoif import geometry


def test_geometry_interface():
    base_geo = geometry._Geometry()
    assert base_geo.__geo_interface__ == {
        "type": "_Geometry",
        "coordinates": (),
    }
