---
title: "GeometryCollection"
description: "Reference for pygeoif.GeometryCollection, the heterogeneous collection type for nested geometry structures."
---

`GeometryCollection` stores many geometry values, including nested collections. It is defined in `pygeoif/geometry.py` and exported as `pygeoif.GeometryCollection`.

## Signature

```python
GeometryCollection(
    geometries: Iterable[
        Union[
            Point,
            LineString,
            LinearRing,
            Polygon,
            MultiPoint,
            MultiLineString,
            MultiPolygon,
            GeometryCollection,
        ]
    ]
) -> None
```

## Constructor Parameters

| Parameter | Type | Default | Description |
|---|---|---|---|
| `geometries` | `Iterable[Union[Geometry, GeometryCollection]]` | — | Geometry instances to store; falsey empty geometries are filtered out. |

## Public API

| Name | Type | Description |
|---|---|---|
| `geoms` | `Iterator[Geometry \| GeometryCollection]` | Yields non-empty member geometries. |
| `has_z` | `Optional[bool]` | True if any member geometry has Z values. |
| `is_empty` | `bool` | True when every stored member is empty. |
| `bounds` | `tuple[float, float, float, float] \| tuple[()]` | Aggregate XY extent. |
| `wkt` | `str` | WKT representation using `GEOMETRYCOLLECTION`. |
| `__geo_interface__` | `GeoCollectionInterface` | GeoJSON-like mapping with a `geometries` array. |
| `__len__()` | `int` | Number of stored members. |

## Equality

Unlike the simpler multi-geometry classes, `GeometryCollection` overrides `__eq__` directly. It rejects empty collections, checks the other object's `type` and member count, then compares nested protocol mappings with `compare_geo_interface()` from `pygeoif/functions.py`.

## Examples

Basic usage:

```python
from pygeoif import GeometryCollection, LineString, Point

collection = GeometryCollection([Point(0, 0), LineString([(0, 0), (1, 1)])])
print(len(collection))
print(collection.__geo_interface__)
```

Nested collections:

```python
from pygeoif import GeometryCollection, MultiPoint, Point

nested = GeometryCollection(
    [
        MultiPoint([(0, 0), (1, 1)]),
        GeometryCollection([Point(5, 5)]),
    ]
)

print(nested.wkt)
print(nested.bounds)
```

## Notes

- `GeometryCollection` is supported by the library but called out in the source docstring as less common in mainstream GIS workflows.
- Empty member geometries are filtered out at construction time because the constructor keeps only truthy geometries.
- Use this type when heterogeneity matters; otherwise prefer the specific multi-geometry class that matches your data.

## Related API

- [MultiPoint](/docs/api-reference/multipoint)
- [MultiLineString](/docs/api-reference/multilinestring)
- [MultiPolygon](/docs/api-reference/multipolygon)
