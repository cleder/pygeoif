"""Test MultiPolygons with Hypothesis."""

from hypothesis import given

from pygeoif import geometry
from pygeoif.factories import force_2d
from pygeoif.factories import force_3d
from pygeoif.factories import from_wkt
from pygeoif.factories import shape
from pygeoif.hypothesis.strategies import epsg4326
from pygeoif.hypothesis.strategies import multi_polygons


@given(multi_polygons(srs=epsg4326))
def test_from_wkt_epsg_4326(multi_poly: geometry.MultiPolygon) -> None:
    assert multi_poly == from_wkt(str(multi_poly))


@given(multi_polygons(srs=epsg4326))
def test_repr_eval(multi_poly: geometry.MultiPolygon) -> None:
    assert (
        eval(repr(multi_poly), {}, {"MultiPolygon": geometry.MultiPolygon})
        == multi_poly
    )


@given(multi_polygons(srs=epsg4326))
def test_shape(multi_poly: geometry.MultiPolygon) -> None:
    assert multi_poly == shape(multi_poly)


@given(multi_polygons(srs=epsg4326))
def test_bounds(multi_poly: geometry.MultiPolygon) -> None:
    assert multi_poly.bounds == force_2d(multi_poly).bounds


@given(multi_polygons(srs=epsg4326))
def test_convex_hull(multi_poly: geometry.MultiPolygon) -> None:
    assert multi_poly.convex_hull == force_2d(multi_poly.convex_hull)
    assert multi_poly.convex_hull == force_2d(multi_poly).convex_hull
    assert multi_poly.convex_hull == force_3d(multi_poly).convex_hull


@given(multi_polygons(srs=epsg4326))
def test_convex_hull_bounds(multi_poly: geometry.MultiPolygon) -> None:
    """
    Test that the convex hull calculation preserves the original bounds.

    The bounds of the convex hull of a MultiPolygon must be equal to the bounds of
    the MultiPolygon itself.
    """
    assert multi_poly.convex_hull
    assert multi_poly.convex_hull.bounds == multi_poly.bounds
