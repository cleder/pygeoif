---
title: "FeatureCollection"
description: "Reference for pygeoif.FeatureCollection, the ordered collection of Feature objects."
---

`FeatureCollection` groups multiple `Feature` objects and serializes them as a GeoJSON-style feature collection. It is implemented in `pygeoif/feature.py` and exported as `pygeoif.FeatureCollection`.

## Signature

```python
FeatureCollection(features: Sequence[Feature]) -> None
```

## Constructor Parameters

| Parameter | Type | Default | Description |
|---|---|---|---|
| `features` | `Sequence[Feature]` | — | Ordered feature instances stored as an immutable tuple. |

## Public API

| Name | Type | Description |
|---|---|---|
| `features` | `Generator[Feature, None, None]` | Yields features in stored order. |
| `bounds` | `Bounds` | Aggregate XY extent across member geometries. |
| `__geo_interface__` | `GeoFeatureCollectionInterface` | GeoJSON-like feature collection mapping. |
| `__len__()` | `int` | Number of features. |
| `__iter__()` | `Iterator[Feature]` | Iterates over stored features. |

## Examples

Basic usage:

```python
from pygeoif import Feature, FeatureCollection, Point

collection = FeatureCollection(
    [
        Feature(Point(0, 0), {"name": "a"}, feature_id=1),
        Feature(Point(2, 3), {"name": "b"}, feature_id=2),
    ]
)

print(len(collection))
print(collection.bounds)
```

Combining different geometry types:

```python
from pygeoif import Feature, FeatureCollection, LineString, Point

collection = FeatureCollection(
    [
        Feature(Point(0, 0), {"kind": "origin"}),
        Feature(LineString([(0, 0), (3, 4)]), {"kind": "path"}),
    ]
)

print([feature.geometry.geom_type for feature in collection])
print(collection.__geo_interface__)
```

## Notes

- Bounds are computed from `feature.geometry.bounds`, not from feature properties.
- Equality is order-sensitive because the implementation zips features in sequence order.
- The collection itself is immutable in structure because stored features are converted to a tuple.

## Source Behavior

`FeatureCollection.bounds` in `pygeoif/feature.py` aggregates bounds by zipping the `(minx, miny, maxx, maxy)` tuples from every member geometry and then taking the min or max of each column. The implementation is simple and fast for normal collections, but it assumes you are storing features with meaningful geometry bounds. In other words, `FeatureCollection` is designed as a transport and grouping layer for actual spatial data, not as a generic list container that happens to accept features.

## Related API

- [Feature](/docs/api-reference/feature)
- [Types And Protocols](/docs/api-reference/types-and-protocols)
- [Functions](/docs/api-reference/functions)
