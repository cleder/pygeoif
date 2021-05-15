"""Test MultiPoint."""
from unittest import mock

import pytest

from pygeoif import geometry


def test_geoms():
    multipoint = geometry.MultiPoint([(0, 0), (1, 1), (1, 2), (2, 2)])

    for point in multipoint.geoms:
        assert type(point) == geometry.Point


def test_len():
    multipoint = geometry.MultiPoint(
        [(0, 0), (1, 1), (1, 2), (2, 2), (0, 0), (1, 1), (1, 2), (2, 2)],
    )

    assert len(multipoint) == 8


def test_geo_interface():
    multipoint = geometry.MultiPoint([(0, 0), (1, 1), (1, 2), (2, 2)])

    assert multipoint.__geo_interface__ == {
        "type": "MultiPoint",
        "bbox": (0, 0, 2, 2),
        "coordinates": ((0, 0), (1, 1), (1, 2), (2, 2)),
    }


def test_coords():
    multipoint = geometry.MultiPoint([(0, 0), (1, 1), (1, 2), (2, 2)])

    with pytest.raises(
        NotImplementedError,
        match="Multi-part geometries do not provide a coordinate sequence",
    ):
        multipoint.coords


def test_unique():
    multipoint = geometry.MultiPoint(
        [(0, 0), (1, 1), (1, 2), (2, 2), (0, 0), (1, 1), (1, 2), (2, 2)],
    )

    multipoint.unique()

    assert len(multipoint) == 4


def test_wkt():
    multipoint = geometry.MultiPoint([(0, 0), (1, 1), (1, 2), (2, 2)])

    assert multipoint.wkt == "MULTIPOINT(0 0, 1 1, 1 2, 2 2)"


def test_repr():
    multipoint = geometry.MultiPoint([(0, 0), (1, 1), (1, 2), (2, 2)])

    assert repr(multipoint) == "MultiPoint(((0, 0), (1, 1), (1, 2), (2, 2)))"


def test_repr_eval():
    multipoint = geometry.MultiPoint([(0, 0), (1, 1), (1, 2), (2, 2)])

    assert (
        eval(
            repr(multipoint),
            {},
            {"MultiPoint": geometry.MultiPoint},
        ).__geo_interface__
        == multipoint.__geo_interface__
    )
