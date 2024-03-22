"""Test the MultiPoint class using Hypothesis."""

from hypothesis import given

from pygeoif import geometry
from pygeoif.factories import force_2d
from pygeoif.factories import from_wkt
from pygeoif.factories import shape
from pygeoif.hypothesis.strategies import epsg4326
from pygeoif.hypothesis.strategies import multi_points


@given(multi_points(srs=epsg4326))
def test_from_wkt_epsg_4326(multi_point: geometry.MultiPoint) -> None:

    assert multi_point == from_wkt(str(multi_point))


@given(multi_points())
def test_repr_eval(multi_point: geometry.MultiPoint) -> None:
    assert (
        eval(repr(multi_point), {}, {"MultiPoint": geometry.MultiPoint}) == multi_point
    )


@given(multi_points())
def test_shape(multi_point: geometry.MultiPoint) -> None:
    assert multi_point == shape(multi_point)


@given(multi_points())
def test_bounds(multi_point: geometry.MultiPoint) -> None:
    assert multi_point.bounds == force_2d(multi_point).bounds


@given(multi_points())
def test_convex_hull(multi_point: geometry.MultiPoint) -> None:
    assert multi_point.convex_hull == force_2d(multi_point).convex_hull
    assert multi_point.convex_hull.bounds == multi_point.bounds
