"""Test MultiPolygons with Hypothesis."""

from hypothesis import given

from pygeoif import geometry
from pygeoif.factories import from_wkt
from pygeoif.factories import shape
from pygeoif.hypothesis.strategies import epsg4326
from pygeoif.hypothesis.strategies import geometry_collections


@given(geometry_collections(srs=epsg4326))
def test_from_wkt_epsg_4326(multi_poly: geometry.GeometryCollection) -> None:
    assert multi_poly == from_wkt(str(multi_poly))


@given(geometry_collections(srs=epsg4326))
def test_repr_eval(multi_poly: geometry.GeometryCollection) -> None:
    assert (
        eval(
            repr(multi_poly),
            {},
            {
                "GeometryCollection": geometry.GeometryCollection,
                "MultiPolygon": geometry.MultiPolygon,
                "Polygon": geometry.Polygon,
                "Point": geometry.Point,
                "LineString": geometry.LineString,
                "LinearRing": geometry.LinearRing,
                "MultiPoint": geometry.MultiPoint,
                "MultiLineString": geometry.MultiLineString,
            },
        )
        == multi_poly
    )


@given(geometry_collections(srs=epsg4326, has_z=False))
def test_shape_2d(multi_poly: geometry.GeometryCollection) -> None:
    assert multi_poly == shape(multi_poly)


@given(geometry_collections(srs=epsg4326, has_z=True))
def test_shape_3d(multi_poly: geometry.GeometryCollection) -> None:
    assert multi_poly == shape(multi_poly)
