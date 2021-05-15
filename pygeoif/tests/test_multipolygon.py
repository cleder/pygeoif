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
