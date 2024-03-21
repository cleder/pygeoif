"""Test the Point class using Hypothesis."""

from hypothesis import given

from pygeoif import geometry
from pygeoif.factories import from_wkt
from pygeoif.factories import shape
from pygeoif.hypothesis.strategies import epsg4326
from pygeoif.hypothesis.strategies import point_types


@given(point_types(epsg4326))
def test_repr_eval_epsg_4326(point) -> None:
    point = geometry.Point(*point)

    assert eval(repr(point), {}, {"Point": geometry.Point}) == point


@given(point_types(epsg4326))
def test_shape_epsg_4326(point) -> None:
    point = geometry.Point(*point)

    assert point == shape(point)


@given(point_types(epsg4326))
def test_from_wkt_epsg_4326(point) -> None:
    point = geometry.Point(*point)

    assert point == from_wkt(str(point))
