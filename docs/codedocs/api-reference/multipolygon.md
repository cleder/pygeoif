---
title: "MultiPolygon"
description: "Reference for pygeoif.MultiPolygon, the immutable collection of polygon geometries."
---

`MultiPolygon` represents a homogeneous collection of polygons. It is implemented in `pygeoif/geometry.py` and exported as `pygeoif.MultiPolygon`.

## Signature

```python
MultiPolygon(polygons: Sequence[PolygonType], unique: bool = False) -> None
```

## Constructor Parameters

| Parameter | Type | Default | Description |
|---|---|---|---|
| `polygons` | `Sequence[PolygonType]` | — | Polygon coordinate tuples in `(shell, holes?)` form. |
| `unique` | `bool` | `False` | Deduplicates polygons using a set conversion, losing order. |

## Public API

| Name | Type | Description |
|---|---|---|
| `geoms` | `Iterator[Polygon]` | Yields non-empty polygons. |
| `has_z` | `Optional[bool]` | True if any member polygon has Z values. |
| `is_empty` | `bool` | True when all members are empty. |
| `bounds` | `tuple[float, float, float, float] \| tuple[()]` | Aggregate XY extent. |
| `wkt` | `str` | WKT representation such as `MULTIPOLYGON (((...)), ((...)))`. |
| `__geo_interface__` | `GeoInterface` | GeoJSON-like mapping with one polygon coordinate sequence per member. |
| `__len__()` | `int` | Number of stored polygons. |

### Class Methods

```python
MultiPolygon.from_polygons(*args: Polygon, unique: bool = False) -> MultiPolygon
```

## Examples

Basic usage:

```python
from pygeoif import MultiPolygon

multi = MultiPolygon(
    [
        (((0, 0), (2, 0), (2, 2), (0, 2), (0, 0)),),
        (((10, 10), (12, 10), (12, 12), (10, 12), (10, 10)),),
    ]
)

print(len(multi))
print(multi.bounds)
```

Building from polygons:

```python
from pygeoif import MultiPolygon, Polygon

first = Polygon([(0, 0), (2, 0), (2, 2), (0, 2), (0, 0)])
second = Polygon([(3, 3), (4, 3), (4, 4), (3, 4), (3, 3)])
multi = MultiPolygon.from_polygons(first, second)

print([polygon.wkt for polygon in multi.geoms])
print(multi.__geo_interface__)
```

## Notes

- The class does not validate overlap between member polygons even though overlapping members are semantically invalid in many GIS contexts.
- `unique=True` uses set semantics and should only be used when ordering is irrelevant.
- Hull calculations flatten all polygon hull points from member geometries.

## Related API

- [Polygon](/docs/api-reference/polygon)
- [GeometryCollection](/docs/api-reference/geometrycollection)
- [Factories](/docs/api-reference/factories)
