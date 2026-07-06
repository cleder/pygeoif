---
title: "Point"
description: "Reference for pygeoif.Point, the immutable zero-dimensional geometry type."
---

`Point` represents a single 2D or 3D coordinate and is defined in `pygeoif/geometry.py`. Import it from the package root with `from pygeoif import Point` or from the implementation module with `from pygeoif.geometry import Point`.

## Signature

```python
Point(x: float, y: float, z: Optional[float] = None) -> None
```

Source: `pygeoif/geometry.py`

## Constructor Parameters

| Parameter | Type | Default | Description |
|---|---|---|---|
| `x` | `float` | — | X or longitude coordinate. |
| `y` | `float` | — | Y or latitude coordinate. |
| `z` | `Optional[float]` | `None` | Optional elevation or third dimension. |

## Public Properties And Methods

### Properties

| Name | Type | Description |
|---|---|---|
| `x` | `float` | Returns the first coordinate. |
| `y` | `float` | Returns the second coordinate. |
| `z` | `Optional[float]` | Returns the third coordinate or raises `DimensionError` if absent. |
| `coords` | `tuple[PointType] \| tuple[()]` | Returns `((x, y),)` or `((x, y, z),)` for non-empty points. |
| `is_empty` | `bool` | True when any stored coordinate is `None` or `NaN`. |
| `has_z` | `bool` | True when the point stores three coordinates. |
| `bounds` | `tuple[float, float, float, float] \| tuple[()]` | `(minx, miny, maxx, maxy)` for non-empty points. |
| `convex_hull` | `Point \| LineString \| Polygon \| None` | Returns the point itself for non-empty points. |
| `wkt` | `str` | WKT representation such as `POINT (1 2)` or `POINT Z (1 2 3)`. |
| `__geo_interface__` | `GeoInterface` | GeoJSON-like mapping with `type`, `bbox`, and `coordinates`. |

### Class Methods

```python
Point.from_coordinates(coordinates: Sequence[PointType]) -> Point
```

Build a point from the first coordinate tuple in a coordinate sequence.

## Return Value

The constructor returns an immutable `Point` instance. Equality is value-based and uses coordinate comparison rather than object identity.

## Examples

Basic usage:

```python
from pygeoif import Point

point = Point(1.5, -3.0)
print(point.x, point.y)
print(point.bounds)
print(point.wkt)
```

Three-dimensional usage:

```python
from pygeoif import Point

point = Point(10, 20, 5)
print(point.has_z)
print(point.coords)
print(point.__geo_interface__)
```

## Notes

- Empty points are possible if a coordinate is `None` or `NaN`; in that case `bool(point)` is `False`.
- Accessing `.z` on a 2D point raises `pygeoif.exceptions.DimensionError`.
- `Point.__geo_interface__` raises `AttributeError("Empty Geometry")` for empty points, matching the base geometry behavior in `pygeoif/geometry.py`.

## Related API

- [LineString](/docs/api-reference/linestring)
- [Functions](/docs/api-reference/functions)
- [Factories](/docs/api-reference/factories)
