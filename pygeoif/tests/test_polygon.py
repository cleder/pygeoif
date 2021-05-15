"""Test Polygon."""
from unittest import mock

import pytest

from pygeoif import geometry


def test_geo_interface_shell_only():
    polygon = geometry.Polygon([(0, 0), (1, 1), (1, 0), (0, 0)])

    assert polygon.__geo_interface__, {
        "type": "Polygon",
        "bbox": (0.0, 0.0, 1.0, 1.0),
        "coordinates": (((0.0, 0.0), (1.0, 1.0), (1.0, 0.0), (0.0, 0.0)),),
    }


def test_geo_interface_with_holes():
    e = [(0, 0), (0, 2), (2, 2), (2, 0), (0, 0)]
    i = [(1, 0), (0.5, 0.5), (1, 1), (1.5, 0.5), (1, 0)]
    polygon = geometry.Polygon(e, [i])

    assert polygon.__geo_interface__ == {
        "type": "Polygon",
        "bbox": (0.0, 0.0, 2.0, 2.0),
        "coordinates": (
            ((0.0, 0.0), (0.0, 2.0), (2.0, 2.0), (2.0, 0.0), (0.0, 0.0)),
            ((1.0, 0.0), (0.5, 0.5), (1.0, 1.0), (1.5, 0.5), (1.0, 0.0)),
        ),
    }


def test_exteriors():
    polygon = geometry.Polygon([(0, 0), (0, 2), (2, 2), (2, 0), (0, 0)])

    assert polygon.exterior.coords == ((0, 0), (0, 2), (2, 2), (2, 0), (0, 0))


def test_interiors():
    e = [(0, 0), (0, 2), (2, 2), (2, 0), (0, 0)]
    i = [(1, 0), (0.5, 0.5), (1, 1), (1.5, 0.5), (1, 0)]
    polygon = geometry.Polygon(e, [i])

    assert list(polygon.interiors)[0].coords == (
        (1, 0),
        (0.5, 0.5),
        (1, 1),
        (1.5, 0.5),
        (1, 0),
    )


def test_bounds():
    polygon = geometry.Polygon([(0, 0), (1, 1), (1, 0), (0, 0)])

    assert polygon.bounds == (0.0, 0.0, 1.0, 1.0)


def test_wkt_shell_only():
    polygon = geometry.Polygon([(0, 0), (1, 1), (1, 0), (0, 0)], [])

    assert polygon.wkt == "POLYGON ((0 0, 1 1, 1 0, 0 0))"


def test_wkt_with_holes():
    e = [(0, 0), (0, 2), (2, 2), (2, 0), (0, 0)]
    i = [(1, 0), (0.5, 0.5), (1, 1), (1.5, 0.5), (1, 0)]
    polygon = geometry.Polygon(e, [i])

    assert (
        polygon.wkt
        == "POLYGON ((0 0, 0 2, 2 2, 2 0, 0 0),(1 0, 0.5 0.5, 1 1, 1.5 0.5, 1 0))"
    )


def test_wkt_shell_only_3d():
    polygon = geometry.Polygon([(0, 0, 0), (1, 1, 0), (1, 0, 0), (0, 0, 0)])

    assert polygon.wkt == "POLYGON Z ((0 0 0, 1 1 0, 1 0 0, 0 0 0))"


def test_repr():
    e = [(0, 0), (0, 2), (2, 2), (2, 0), (0, 0)]
    i = [(1, 0), (0.5, 0.5), (1, 1), (1.5, 0.5), (1, 0)]
    polygon = geometry.Polygon(e, [i])

    assert repr(polygon) == (
        "Polygon(((0, 0), (0, 2), (2, 2), (2, 0), (0, 0)), "
        "(((1, 0), (0.5, 0.5), (1, 1), (1.5, 0.5), (1, 0)),))"
    )


def test_repr_shell_only():
    polygon = geometry.Polygon([(0, 0, 0), (1, 1, 0), (1, 0, 0), (0, 0, 0)])

    assert repr(polygon) == "Polygon(((0, 0, 0), (1, 1, 0), (1, 0, 0), (0, 0, 0)), )"


def test_repr_eval():
    e = [(0, 0), (0, 2), (2, 2), (2, 0), (0, 0)]
    i = [(1, 0), (0.5, 0.5), (1, 1), (1.5, 0.5), (1, 0)]
    polygon = geometry.Polygon(e, [i])

    assert (
        eval(repr(polygon), {}, {"Polygon": geometry.Polygon}).__geo_interface__
        == polygon.__geo_interface__
    )


def test_repr_eval_shell_only():
    polygon = geometry.Polygon([(0, 0, 0), (1, 1, 0), (1, 0, 0), (0, 0, 0)])

    assert (
        eval(repr(polygon), {}, {"Polygon": geometry.Polygon}).__geo_interface__
        == polygon.__geo_interface__
    )
