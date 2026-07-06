---
title: "Features And Collections"
description: "Learn how pygeoif wraps geometries in GeoJSON-style Feature and FeatureCollection containers."
---

The geometry classes model spatial shapes. `Feature` and `FeatureCollection`, defined in `pygeoif/feature.py`, model the next layer up: a geometry plus application data. This concept exists because spatial applications almost never ship raw polygons or points alone. They attach identifiers, names, categories, or arbitrary metadata to those shapes and often group them into collections for transport and storage.

In `pygeoif`, `Feature` is a thin wrapper around a geometry plus a `properties` dictionary and optional `feature_id`. `FeatureCollection` groups many `Feature` objects and computes an aggregate bounding box from the geometries it contains. These objects relate to the `__geo_interface__` concept directly because both serialize into GeoJSON-like `Feature` and `FeatureCollection` mappings.

## How It Works Internally

`Feature.__geo_interface__` assembles a mapping with `type: "Feature"`, the geometry’s `bbox`, the geometry’s own `__geo_interface__`, and the properties dictionary. If `feature_id` is present it adds an `id` field. Equality delegates to `feature_geo_interface_equals()`, which compares the `id`, `type`, properties, nested geometry type, and nested coordinates using `compare_coordinates()` from `pygeoif/functions.py`.

`FeatureCollection` stores features as an immutable tuple, exposes iteration, and computes `.bounds` by zipping the bounds of every member geometry. Its equality path first checks that the other object looks like a compatible collection and has the same number of features, then compares the protocol mapping of each feature in order. That order sensitivity matches how features are stored and serialized.

## Basic Usage

```python
from pygeoif import Feature, FeatureCollection, Point

city_hall = Feature(
    Point(-73.9857, 40.7484),
    properties={"name": "City Hall", "kind": "landmark"},
    feature_id="city-hall",
)

places = FeatureCollection([city_hall])

print(city_hall.__geo_interface__["type"])
print(places.bounds)
```

## Advanced Usage

You can mix geometry types inside one `FeatureCollection`, which is often useful when building response payloads for map overlays.

```python
from pygeoif import Feature, FeatureCollection, LineString, Point, Polygon

features = FeatureCollection(
    [
        Feature(Point(0, 0), {"role": "start"}, feature_id=1),
        Feature(LineString([(0, 0), (2, 1)]), {"role": "route"}, feature_id=2),
        Feature(
            Polygon([(0, 0), (2, 0), (2, 2), (0, 2), (0, 0)]),
            {"role": "zone"},
            feature_id=3,
        ),
    ]
)

print(len(features))
print(features.__geo_interface__["bbox"])
```

<Callout type="warn">`Feature.properties` returns the stored dictionary directly, so the feature wrapper itself is not an immutable value object in the same sense as the geometry classes. If you mutate the properties mapping after construction, later `__geo_interface__` output reflects those changes. Also note that `FeatureCollection.bounds` assumes each feature geometry has bounds, so empty geometries are a poor fit for collection-wide extent calculations.</Callout>

<Accordions>
<Accordion title="Why Feature wraps only one geometry">
`Feature` stays close to the GeoJSON data model and always stores exactly one geometry plus metadata. That keeps serialization simple and makes it obvious how to map the object into APIs, files, and downstream libraries. If you need many geometries under one record, the intended pattern is to wrap a `GeometryCollection` in a `Feature`, not to invent a parallel container shape. The trade-off is that your domain model sometimes needs one extra object when a business entity naturally spans several shapes.
</Accordion>
<Accordion title="Mutable properties versus immutable geometry">
The geometry classes are intentionally immutable, but `Feature.properties` is a normal Python dictionary. That split is pragmatic: metadata often needs to be assembled or updated as an application pipeline progresses, while geometry coordinates benefit from staying stable once normalized. The trade-off is that `Feature` equality can change over time if you mutate `properties`, because equality compares the protocol mapping including the metadata payload. If you need fully stable feature values, copy or freeze the properties mapping before constructing the feature.
</Accordion>
</Accordions>
