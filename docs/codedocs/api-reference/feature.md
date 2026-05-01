---
title: "Feature"
description: "Reference for pygeoif.Feature, the GeoJSON-style geometry-plus-properties wrapper."
---

`Feature` wraps one geometry with a property mapping and optional identifier. It is implemented in `pygeoif/feature.py` and exported as `pygeoif.Feature`.

## Signature

```python
Feature(
    geometry: Geometry,
    properties: Optional[dict[str, Any]] = None,
    feature_id: Optional[Union[str, int]] = None,
) -> None
```

## Constructor Parameters

| Parameter | Type | Default | Description |
|---|---|---|---|
| `geometry` | `Geometry` | — | The geometry value wrapped by the feature. |
| `properties` | `Optional[dict[str, Any]]` | `None` | Property mapping stored on the feature; defaults to an empty dict. |
| `feature_id` | `Optional[Union[str, int]]` | `None` | Optional `id` field included in `__geo_interface__`. |

## Public Properties

| Name | Type | Description |
|---|---|---|
| `id` | `Optional[Union[str, int]]` | Returns the feature identifier. |
| `geometry` | `Geometry` | Returns the wrapped geometry. |
| `properties` | `dict[str, Any]` | Returns the stored properties dictionary. |
| `__geo_interface__` | `GeoFeatureInterface` | GeoJSON-like feature mapping. |

## Examples

Basic usage:

```python
from pygeoif import Feature, Point

feature = Feature(Point(1, 2), {"name": "sensor-a"}, feature_id="sensor-a")
print(feature.geometry.wkt)
print(feature.__geo_interface__)
```

Mutating properties after construction:

```python
from pygeoif import Feature, Point

feature = Feature(Point(1, 2), {"status": "new"})
feature.properties["status"] = "ready"

print(feature.__geo_interface__["properties"])
```

## Notes

- Equality is based on the feature's GeoJSON-like mapping, including `id`, properties, nested geometry type, and nested coordinates.
- Properties remain mutable because `Feature` stores the original dictionary or an empty replacement dict.
- The feature's `bbox` in `__geo_interface__` comes directly from `geometry.bounds`.

## Source Behavior

The implementation in `pygeoif/feature.py` is intentionally thin. The constructor stores three fields, and the protocol mapping is assembled on demand instead of cached. That design keeps `Feature` aligned with whatever geometry and properties it currently references, which is especially useful when you progressively enrich metadata in an application pipeline. The trade-off is that the feature wrapper itself is not a frozen value object the way the geometry classes are.

## Related API

- [FeatureCollection](/docs/api-reference/featurecollection)
- [Types And Protocols](/docs/api-reference/types-and-protocols)
- [Functions](/docs/api-reference/functions)
