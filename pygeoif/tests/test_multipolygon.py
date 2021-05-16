"""Test MultiPolygon."""
from unittest import mock

import pytest

from pygeoif import geometry


def test_geoms():
    polys = geometry.MultiPolygon(
        [
            (
                ((0.0, 0.0), (0.0, 1.0), (1.0, 1.0), (1.0, 0.0)),
                [((0.25, 0.25), (0.25, 0.5), (0.5, 0.5), (0.5, 0.25))],
            )
        ]
    )

    for poly in polys.geoms:
        assert type(poly) == geometry.Polygon


def test_len():
    polys = geometry.MultiPolygon(
        [
            (
                ((0.0, 0.0), (0.0, 1.0), (1.0, 1.0), (1.0, 0.0)),
                [((0.1, 0.1), (0.1, 0.2), (0.2, 0.2), (0.2, 0.1))],
            ),
            (((0.0, 0.0), (0.0, 1.0), (1.0, 1.0), (1.0, 0.0)),),
        ]
    )

    assert len(polys) == 2


def test_geo_interface():
    polys = geometry.MultiPolygon(
        [
            (
                ((0.0, 0.0), (0.0, 1.0), (1.0, 1.0), (1.0, 0.0)),
                [((0.1, 0.1), (0.1, 0.2), (0.2, 0.2), (0.2, 0.1))],
            )
        ]
    )
    assert polys.__geo_interface__ == {
        "type": "MultiPolygon",
        "bbox": (0.0, 0.0, 1.0, 1.0),
        "coordinates": (
            (
                ((0.0, 0.0), (0.0, 1.0), (1.0, 1.0), (1.0, 0.0), (0.0, 0.0)),
                ((0.1, 0.1), (0.1, 0.2), (0.2, 0.2), (0.2, 0.1), (0.1, 0.1)),
            ),
        ),
    }


def test_from_dict():
    polys = geometry.MultiPolygon._from_dict(
        {
            "type": "MultiPolygon",
            "bbox": (0.0, 0.0, 1.0, 1.0),
            "coordinates": (
                (
                    ((0.0, 0.0), (0.0, 1.0), (1.0, 1.0), (1.0, 0.0), (0.0, 0.0)),
                    ((0.1, 0.1), (0.1, 0.2), (0.2, 0.2), (0.2, 0.1), (0.1, 0.1)),
                ),
            ),
        },
    )

    assert polys.__geo_interface__ == {
        "type": "MultiPolygon",
        "bbox": (0.0, 0.0, 1.0, 1.0),
        "coordinates": (
            (
                ((0.0, 0.0), (0.0, 1.0), (1.0, 1.0), (1.0, 0.0), (0.0, 0.0)),
                ((0.1, 0.1), (0.1, 0.2), (0.2, 0.2), (0.2, 0.1), (0.1, 0.1)),
            ),
        ),
    }


def test_wkt():
    polys = geometry.MultiPolygon(
        [
            (
                ((0.0, 0.0), (0.0, 1.0), (1.0, 1.0), (1.0, 0.0)),
                [((0.1, 0.1), (0.1, 0.2), (0.2, 0.2), (0.2, 0.1))],
            ),
            (((0.0, 0.0), (0.0, 1.0), (1.0, 1.0), (1.0, 0.0)),),
        ]
    )

    assert polys.wkt == (
        "MULTIPOLYGON(((0.0 0.0, 0.0 1.0, 1.0 1.0, 1.0 0.0, 0.0 0.0),"
        "(0.1 0.1, 0.1 0.2, 0.2 0.2, 0.2 0.1, 0.1 0.1)),"
        "((0.0 0.0, 0.0 1.0, 1.0 1.0, 1.0 0.0, 0.0 0.0)))"
    )


def test_repr():
    polys = geometry.MultiPolygon(
        [
            (
                ((0.0, 0.0), (0.0, 1.0), (1.0, 1.0), (1.0, 0.0)),
                [((0.1, 0.1), (0.1, 0.2), (0.2, 0.2), (0.2, 0.1))],
            ),
            (((0.0, 0.0), (0.0, 1.0), (1.0, 1.0), (1.0, 0.0)),),
        ]
    )

    assert repr(polys) == (
        "MultiPolygon(((((0.0, 0.0), (0.0, 1.0), (1.0, 1.0), (1.0, 0.0), (0.0, 0.0)), "
        "(((0.1, 0.1), (0.1, 0.2), (0.2, 0.2), (0.2, 0.1), (0.1, 0.1)),)), "
        "(((0.0, 0.0), (0.0, 1.0), (1.0, 1.0), (1.0, 0.0), (0.0, 0.0)),)))"
    )


def test_repr_eval():
    polys = geometry.MultiPolygon(
        [
            (
                ((0.0, 0.0), (0.0, 1.0), (1.0, 1.0), (1.0, 0.0)),
                [((0.1, 0.1), (0.1, 0.2), (0.2, 0.2), (0.2, 0.1))],
            ),
            (((0.0, 0.0), (0.0, 1.0), (1.0, 1.0), (1.0, 0.0)),),
        ]
    )

    assert (
        eval(
            repr(polys),
            {},
            {"MultiPolygon": geometry.MultiPolygon},
        ).__geo_interface__
        == polys.__geo_interface__
    )
