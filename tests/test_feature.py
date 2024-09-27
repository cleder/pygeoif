"""Test Feature and FeatureCollection."""

import unittest

import pytest
from hypothesis import given
from hypothesis.strategies import composite
from hypothesis.strategies import dictionaries
from hypothesis.strategies import floats
from hypothesis.strategies import lists
from hypothesis.strategies import none
from hypothesis.strategies import one_of
from hypothesis.strategies import text
from hypothesis.strategies import tuples

from pygeoif import feature
from pygeoif import geometry


@composite
def polygons(draw):
    """Generate a polygon geometry"""
    """The polygon is closed"""
    coords = draw(coordinates())
    coords.append(coords[0])
    return geometry.Polygon(coords)


@composite
def coordinates(draw):
    """Generate a list of coordinates for geometries"""
    return draw(
        lists(
            tuples(
                floats(min_value=180, max_value=180), floats(min_value=90, max_value=90),
            ),
            min_size=3,
            max_size=10,
        ),
    )


@composite
def properties(draw):
    """Generate random properties"""
    return draw(dictionaries(text(), one_of(text(), floats(), none()), max_size=5))


class TestFeature:
    def setup_method(self) -> None:
        self.a = geometry.Polygon(
            ((0.0, 0.0), (0.0, 1.0), (1.0, 1.0), (1.0, 0.0), (0.0, 0.0)),
        )
        self.b = geometry.Polygon(
            ((0.0, 0.0), (0.0, 2.0), (2.0, 1.0), (2.0, 0.0), (0.0, 0.0)),
        )
        self.f1 = feature.Feature(self.a)
        self.f2 = feature.Feature(self.b)
        self.f3 = feature.Feature(self.a, {}, feature_id="1")
        self.fc = feature.FeatureCollection([self.f1, self.f2])

    def test_feature_eq(self) -> None:
        assert self.f1 == feature.Feature(self.a)
        assert self.f3 == feature.Feature(self.a, {}, feature_id="1")

    def test_feature_neq_no_geo_interface(self) -> None:
        assert self.f1 != object()

    def test_feature_neq_no_geo_interface_geometry(self) -> None:
        assert self.f1 != unittest.mock.Mock(__geo_interface__={})

    def test_feature_neq_no_geo_interface_type(self) -> None:
        assert self.f1 != unittest.mock.Mock(__geo_interface__={"type": "foo"})

    def test_feature_neq_no_geo_interface_features(self) -> None:
        assert self.f1 != unittest.mock.Mock(__geo_interface__={"type": "Feature"})

    def test_feature(self) -> None:
        pytest.raises(TypeError, feature.Feature)
        assert self.f1.__geo_interface__ == {
            "type": "Feature",
            "bbox": (0.0, 0.0, 1.0, 1.0),
            "geometry": {
                "type": "Polygon",
                "bbox": (0.0, 0.0, 1.0, 1.0),
                "coordinates": (
                    ((0.0, 0.0), (0.0, 1.0), (1.0, 1.0), (1.0, 0.0), (0.0, 0.0)),
                ),
            },
            "properties": {},
        }
        self.f1.properties["coords"] = {"cube": (0, 0, 0)}
        assert self.f1.__geo_interface__ == {
            "type": "Feature",
            "bbox": (0.0, 0.0, 1.0, 1.0),
            "geometry": {
                "type": "Polygon",
                "bbox": (0.0, 0.0, 1.0, 1.0),
                "coordinates": (
                    ((0.0, 0.0), (0.0, 1.0), (1.0, 1.0), (1.0, 0.0), (0.0, 0.0)),
                ),
            },
            "properties": {"coords": {"cube": (0, 0, 0)}},
        }
        assert self.f1.geometry.bounds == (0.0, 0.0, 1.0, 1.0)
        del self.f1.properties["coords"]

    def test_feature_with_id(self) -> None:
        assert self.f3.id == "1"
        assert self.f3.__geo_interface__ == {
            "type": "Feature",
            "bbox": (0.0, 0.0, 1.0, 1.0),
            "geometry": {
                "type": "Polygon",
                "bbox": (0.0, 0.0, 1.0, 1.0),
                "coordinates": (
                    ((0.0, 0.0), (0.0, 1.0), (1.0, 1.0), (1.0, 0.0), (0.0, 0.0)),
                ),
            },
            "id": "1",
            "properties": {},
        }

    def test_feature_repr(self) -> None:
        assert (
            repr(self.f3) == "Feature("
            "Polygon(((0.0, 0.0), (0.0, 1.0), (1.0, 1.0), (1.0, 0.0), (0.0, 0.0)),),"
            " {}, '1')"
        )

    def test_feature_repr_eval(self) -> None:
        assert (
            eval(
                repr(self.f2),
                {},
                {"Polygon": geometry.Polygon, "Feature": feature.Feature},
            ).__geo_interface__
            == self.f2.__geo_interface__
        )

    @given(polygon=polygons(), props=properties())
    def test_feature_with_random_data(self, polygon, props) -> None:
        f = feature.Feature(polygon, props)
        assert isinstance(f, feature.Feature)
        assert f.geometry == polygon
        assert f.properties == props

    @given(polygon=polygons())
    def test_feature_collection_with_random_features(self, polygon) -> None:
        f1 = feature.Feature(polygon)
        f2 = feature.Feature(polygon)
        fc = feature.FeatureCollection([f1, f2])
        assert isinstance(fc, feature.FeatureCollection)
        assert len(fc) == 2

    def test_featurecollection(self) -> None:
        pytest.raises(TypeError, feature.FeatureCollection)
        pytest.raises(TypeError, feature.FeatureCollection, None)
        assert len(list(self.fc.features)) == 2
        assert len(self.fc) == 2
        assert self.fc.bounds == (0.0, 0.0, 2.0, 2.0)
        assert [self.f1, self.f2] == list(self.fc)
        assert self.fc.__geo_interface__ == {
            "bbox": (0.0, 0.0, 2.0, 2.0),
            "features": (
                {
                    "bbox": (0.0, 0.0, 1.0, 1.0),
                    "geometry": {
                        "bbox": (0.0, 0.0, 1.0, 1.0),
                        "coordinates": (
                            (
                                (0.0, 0.0),
                                (0.0, 1.0),
                                (1.0, 1.0),
                                (1.0, 0.0),
                                (0.0, 0.0),
                            ),
                        ),
                        "type": "Polygon",
                    },
                    "properties": {},
                    "type": "Feature",
                },
                {
                    "bbox": (0.0, 0.0, 2.0, 2.0),
                    "geometry": {
                        "bbox": (0.0, 0.0, 2.0, 2.0),
                        "coordinates": (
                            (
                                (0.0, 0.0),
                                (0.0, 2.0),
                                (2.0, 1.0),
                                (2.0, 0.0),
                                (0.0, 0.0),
                            ),
                        ),
                        "type": "Polygon",
                    },
                    "properties": {},
                    "type": "Feature",
                },
            ),
            "type": "FeatureCollection",
        }

    def test_featurecollection_eq(self) -> None:
        assert self.fc == feature.FeatureCollection([self.f1, self.f2])

    def test_featurecollection_neq_no_geo_interface(self) -> None:
        assert self.fc != object()

    def test_featurecollection_neq_no_geo_interface_geometry(self) -> None:
        assert self.fc != unittest.mock.Mock(__geo_interface__={})

    def test_featurecollection_neq_no_geo_interface_features(self) -> None:
        assert self.fc != unittest.mock.Mock(
            __geo_interface__={"type": "FeatureCollection"},
        )

    def test_featurecollection_neq_no_geo_interface_len_features(self) -> None:
        assert self.fc != feature.FeatureCollection([self.f1])

    def test_featurecollection_repr(self) -> None:
        assert (
            repr(self.fc) == "FeatureCollection("
            "(Feature("
            "Polygon(((0.0, 0.0), (0.0, 1.0), (1.0, 1.0), (1.0, 0.0), (0.0, 0.0)),),"
            " {}, None), "
            "Feature("
            "Polygon(((0.0, 0.0), (0.0, 2.0), (2.0, 1.0), (2.0, 0.0), (0.0, 0.0)),), "
            "{}, None)))"
        )

    def test_featurecollection_repr_eval(self) -> None:
        assert (
            eval(
                repr(self.fc),
                {},
                {
                    "Polygon": geometry.Polygon,
                    "Feature": feature.Feature,
                    "FeatureCollection": feature.FeatureCollection,
                },
            ).__geo_interface__
            == self.fc.__geo_interface__
        )

    def test_featurecollection_bounds(self) -> None:
        ls1 = geometry.LineString(((0, 1), (1, 1)))
        ls2 = geometry.LineString(((2, 3), (3, 4)))
        fc = feature.FeatureCollection([feature.Feature(ls1), feature.Feature(ls2)])

        assert fc.bounds == (0, 1, 3, 4)
