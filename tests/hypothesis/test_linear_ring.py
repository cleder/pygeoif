"""Test LinearRings with Hypothesis."""

from hypothesis import given

from pygeoif import geometry
from pygeoif.factories import from_wkt
from pygeoif.factories import shape
from pygeoif.hypothesis.strategies import epsg4326
from pygeoif.hypothesis.strategies import linear_rings


@given(linear_rings(srs=epsg4326))
def test_from_wkt_epsg_4326(line: geometry.LinearRing) -> None:

    assert line == from_wkt(str(line))


@given(linear_rings())
def test_repr_eval(line: geometry.LinearRing) -> None:

    assert eval(repr(line), {}, {"LinearRing": geometry.LinearRing}) == line


@given(linear_rings())
def test_shape(line: geometry.LinearRing) -> None:
    assert line == shape(line)
