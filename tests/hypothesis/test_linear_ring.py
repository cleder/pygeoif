"""Test LinearRings with Hypothesis."""

import pytest
from hypothesis import given

from pygeoif import geometry
from pygeoif.factories import from_wkt
from pygeoif.factories import shape
from pygeoif.hypothesis.strategies import epsg4326
from pygeoif.hypothesis.strategies import linear_rings


def test_max_points_lt_3() -> None:
    with pytest.raises(ValueError, match="^max_points must be greater than 3$"):
        linear_rings(max_points=3).example()


@given(linear_rings(srs=epsg4326))
def test_from_wkt_epsg_4326(line: geometry.LinearRing) -> None:
    assert line == from_wkt(str(line))


@given(linear_rings())
def test_repr_eval(line: geometry.LinearRing) -> None:
    assert eval(repr(line), {}, {"LinearRing": geometry.LinearRing}) == line


@given(linear_rings())
def test_shape(line: geometry.LinearRing) -> None:
    assert line == shape(line)
