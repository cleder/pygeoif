"""Test Polygons with Hypothesis."""

import pytest
from hypothesis import given

from pygeoif import geometry
from pygeoif.factories import force_2d
from pygeoif.factories import from_wkt
from pygeoif.factories import shape
from pygeoif.hypothesis.strategies import epsg4326
from pygeoif.hypothesis.strategies import polygons


def test_max_points_lt_3() -> None:
    with pytest.raises(ValueError, match=r"^max_points must be greater than 3"):
        polygons(max_points=3).example()


@given(polygons(srs=epsg4326))
def test_from_wkt_epsg_4326(poly: geometry.Polygon) -> None:
    assert poly == from_wkt(str(poly))


@given(polygons())
def test_repr_eval(poly: geometry.Polygon) -> None:
    assert eval(repr(poly), {}, {"Polygon": geometry.Polygon}) == poly


@given(polygons())
def test_shape(poly: geometry.Polygon) -> None:
    assert poly == shape(poly)


@given(polygons())
def test_bounds(poly: geometry.Polygon) -> None:
    assert poly.bounds == force_2d(poly).bounds


@given(polygons())
def test_convex_hull_bounds(poly: geometry.Polygon) -> None:
    """
    Test that the convex hull calculation preserves the original bounds.

    The bounds of the convex hull of a Polygon must be equal to the bounds of
    the Polygon itself.
    """
    assert poly.convex_hull
    assert poly.convex_hull.bounds == poly.bounds
    assert poly.exterior.convex_hull == poly.convex_hull


@given(polygons(min_interiors=1))
def test_interiors(poly: geometry.Polygon) -> None:
    """Test that the strategy generates Polygons with interiors."""
    assert tuple(poly.interiors)


@given(polygons(max_interiors=0))
def test_no_interiors(poly: geometry.Polygon) -> None:
    """Test that the strategy generates Polygons without interiors."""
    assert not tuple(poly.interiors)
