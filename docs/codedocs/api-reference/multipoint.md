---
title: "MultiPoint"
description: "Reference for pygeoif.MultiPoint, the immutable collection of point geometries."
---

`MultiPoint` is a homogeneous collection of `Point` objects defined in `pygeoif/geometry.py` and exported at the package root as `pygeoif.MultiPoint`.

## Signature

```python
MultiPoint(points: Sequence[PointType], unique: bool = False) -> None
```

## Constructor Parameters

| Parameter | Type | Default | Description |
|---|---|---|---|
| `points` | `Sequence[PointType]` | — | Point coordinate tuples used to build the collection. |
| `unique` | `bool` | `False` | Removes duplicates by converting the input to a set. Order is not preserved. |

## Public API

### Properties And Methods

| Name | Type | Description |
|---|---|---|
| `geoms` | `Iterator[Point]` | Yields non-empty points in the collection. |
| `has_z` | `Optional[bool]` | True if any stored point has Z values. |
| `is_empty` | `bool` | True when all stored members are empty. |
| `bounds` | `tuple[float, float, float, float] \| tuple[()]` | Aggregate XY extent. |
| `wkt` | `str` | WKT representation such as `MULTIPOINT ((0 0), (1 1))`. |
| `__geo_interface__` | `GeoInterface` | GeoJSON-like mapping for the collection. |
| `__len__()` | `int` | Number of stored point objects. |

### Class Methods

```python
MultiPoint.from_points(*args: Point, unique: bool = False) -> MultiPoint
```

## Examples

Basic usage:

```python
from pygeoif import MultiPoint

points = MultiPoint([(0, 0), (1, 1), (2, 2)])
print(len(points))
print([p.coords for p in points.geoms])
```

Deduplicated creation:

```python
from pygeoif import MultiPoint, Point

points = MultiPoint.from_points(Point(0, 0), Point(0, 0), Point(1, 1) unique=True)
print(len(points))
print(points.__geo_interface__)
```

## Notes

- `unique=True` removes duplicates but does not preserve input ordering because it uses a set.
- The collection inherits bounds and hull behavior from `_MultiGeometry`.
- `MultiPoint` does not expose a flat `.coords` property; iterate `geoms` instead.

## Related API

- [Point](/docs/api-reference/point)
- [GeometryCollection](/docs/api-reference/geometrycollection)
- [Functions](/docs/api-reference/functions)
