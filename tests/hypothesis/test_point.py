"""Test the Point class using Hypothesis."""

from hypothesis import given

from pygeoif import geometry
from pygeoif.factories import force_2d
from pygeoif.factories import from_wkt
from pygeoif.factories import shape
from pygeoif.hypothesis.strategies import epsg4326
from pygeoif.hypothesis.strategies import point_coords
from pygeoif.hypothesis.strategies import points
from pygeoif.types import PointType


@given(point_coords(srs=epsg4326))
def test_from_wkt_epsg_4326(point: PointType) -> None:
    point = geometry.Point(*point)

    assert point == from_wkt(str(point))


@given(points())
def test_repr_eval(point: geometry.Point) -> None:
    assert eval(repr(point), {}, {"Point": geometry.Point}) == point


@given(points())
def test_shape(point: geometry.Point) -> None:
    assert point == shape(point)


@given(points())
def test_bounds(point: geometry.Point) -> None:
    assert point.bounds == (point.x, point.y, point.x, point.y)
    assert point.bounds == force_2d(point).bounds


@given(points())
def test_convex_hull(point: geometry.Point) -> None:
    assert point.convex_hull == force_2d(point)
    assert point.convex_hull.bounds == point.bounds
