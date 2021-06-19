"""Test Feature and FeatureCollection."""
import unittest

from pygeoif import feature
from pygeoif import geometry


class FeatureTestCase(unittest.TestCase):
    def setUp(self):
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

    def test_feature_eq(self):
        self.assertEqual(self.f1, feature.Feature(self.a))
        self.assertEqual(self.f3, feature.Feature(self.a, {}, feature_id="1"))

    def test_feature_neq_no_geo_interface(self):
        self.assertNotEqual(self.f1, None)

    def test_feature_neq_no_geo_interface_geometry(self):
        self.assertNotEqual(self.f1, unittest.mock.Mock(__geo_interface__={}))

    def test_feature_neq_no_geo_interface_type(self):
        self.assertNotEqual(
            self.f1,
            unittest.mock.Mock(__geo_interface__={"type": "foo"}),
        )

    def test_feature_neq_no_geo_interface_features(self):
        self.assertNotEqual(
            self.f1,
            unittest.mock.Mock(__geo_interface__={"type": "Feature"}),
        )

    def test_feature(self):
        self.assertRaises(TypeError, feature.Feature)
        self.assertEqual(
            self.f1.__geo_interface__,
            {
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
            },
        )
        self.f1.properties["coords"] = {"cube": (0, 0, 0)}
        self.assertEqual(
            self.f1.__geo_interface__,
            {
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
            },
        )
        self.assertEqual(self.f1.geometry.bounds, (0.0, 0.0, 1.0, 1.0))
        del self.f1.properties["coords"]

    def test_feature_with_id(self):
        self.assertEqual(self.f3.id, "1")
        self.assertEqual(
            self.f3.__geo_interface__,
            {
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
            },
        )

    def test_feature_repr(self):
        self.assertEqual(
            repr(self.f3),
            "Feature("  # noqa: P103
            "Polygon(((0.0, 0.0), (0.0, 1.0), (1.0, 1.0), (1.0, 0.0), (0.0, 0.0)),),"
            " {}, '1')",
        )

    def test_feature_repr_eval(self):
        self.assertEqual(
            eval(
                repr(self.f2),
                {},
                {"Polygon": geometry.Polygon, "Feature": feature.Feature},
            ).__geo_interface__,
            self.f2.__geo_interface__,
        )

    def test_featurecollection(self):
        self.assertRaises(TypeError, feature.FeatureCollection)
        self.assertRaises(TypeError, feature.FeatureCollection, None)
        self.assertEqual(len(list(self.fc.features)), 2)
        self.assertEqual(len(self.fc), 2)
        self.assertEqual(self.fc.bounds, (0.0, 0.0, 2.0, 2.0))
        self.assertEqual([self.f1, self.f2], list(self.fc))
        self.assertEqual(
            self.fc.__geo_interface__,
            {
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
            },
        )

    def test_featurecollection_eq(self):
        self.assertEqual(self.fc, feature.FeatureCollection([self.f1, self.f2]))

    def test_featurecollection_neq_no_geo_interface(self):
        self.assertNotEqual(self.fc, None)

    def test_featurecollection_neq_no_geo_interface_geometry(self):
        self.assertNotEqual(self.fc, unittest.mock.Mock(__geo_interface__={}))

    def test_featurecollection_neq_no_geo_interface_features(self):
        self.assertNotEqual(
            self.fc,
            unittest.mock.Mock(__geo_interface__={"type": "FeatureCollection"}),
        )

    def test_featurecollection_neq_no_geo_interface_len_features(self):
        self.assertNotEqual(self.fc, feature.FeatureCollection([self.f1]))

    def test_featurecollection_repr(self):
        self.assertEqual(
            repr(self.fc),
            "FeatureCollection("  # noqa: P103
            "(Feature("
            "Polygon(((0.0, 0.0), (0.0, 1.0), (1.0, 1.0), (1.0, 0.0), (0.0, 0.0)),),"
            " {}, None), "
            "Feature("
            "Polygon(((0.0, 0.0), (0.0, 2.0), (2.0, 1.0), (2.0, 0.0), (0.0, 0.0)),), "
            "{}, None)))",
        )

    def test_featurecollection_repr_eval(self):
        self.assertEqual(
            eval(
                repr(self.fc),
                {},
                {
                    "Polygon": geometry.Polygon,
                    "Feature": feature.Feature,
                    "FeatureCollection": feature.FeatureCollection,
                },
            ).__geo_interface__,
            self.fc.__geo_interface__,
        )

    def test_featurecollection_bounds(self):
        ls1 = geometry.LineString(((0, 1), (1, 1)))
        ls2 = geometry.LineString(((2, 3), (3, 4)))
        fc = feature.FeatureCollection([feature.Feature(ls1), feature.Feature(ls2)])

        self.assertEqual(fc.bounds, (0, 1, 3, 4))
