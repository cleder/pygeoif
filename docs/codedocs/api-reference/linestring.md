---
title: "LineString"
description: "Reference for pygeoif.LineString, the immutable ordered sequence of points."
---

`LineString` represents a one-dimensional geometry made from an ordered sequence of points. It is implemented in `pygeoif/geometry.py` and exported at the package root as `pygeoif.LineString`.

## Signature

```python
LineString(coordinates: LineType) -> None
```

## Constructor Parameters

| Parameter | Type | Default | Description |
|---|---|---|---|
| `coordinates` | `LineType` | — | Sequence of 2D or 3D point tuples. |

## Public Properties And Methods

### Properties

| Name | Type | Description |
|---|---|---|
| `geoms` | `tuple[Point, ...]` | Underlying point objects created from the coordinate sequence. |
| `coords` | `LineType` | Deduplicated coordinate tuples in the same order. |
| `is_empty` | `bool` | True when no valid points remain after normalization. |
| `has_z` | `Optional[bool]` | Z-presence based on the first point, or `None` when empty. |
| `bounds` | `tuple[float, float, float, float] \| tuple[()]` | XY extent of all points. |
| `convex_hull` | `Point \| LineString \| Polygon \| None` | Hull of the line's XY projection. |
| `wkt` | `str` | WKT representation such as `LINESTRING (0 0, 1 1)`. |
| `__geo_interface__` | `GeoInterface` | GeoJSON-like mapping for the line. |

### Class Methods

```python
LineString.from_coordinates(coordinates: LineType) -> LineString
LineString.from_points(*args: Point) -> LineString
```

## Behavior

Construction flows through the internal `_set_geoms()` helper in `pygeoif/geometry.py`. That helper removes consecutive duplicate coordinates with `dedupe()` from `pygeoif/functions.py`, creates `Point` objects, discards empty points, and raises `DimensionError` if dimensions are mixed inside the same line.

## Examples

Basic usage:

```python
from pygeoif import LineString

line = LineString([(0, 0), (1, 1), (2, 1)])
print(line.coords)
print(line.bounds)
print(line.wkt)
```

Building from `Point` objects:

```python
from pygeoif import LineString, Point

line = LineString.from_points(Point(0, 0), Point(1, 1), Point(2, 1))
print(tuple(p.wkt for p in line.geoms))
print(line.__geo_interface__)
```

## Notes

- Consecutive duplicate coordinates are removed during construction, but non-adjacent duplicates remain.
- Mixed 2D and 3D coordinates raise `pygeoif.exceptions.DimensionError`.
- `convex_hull` may return a `Point` or `Polygon` depending on the line geometry.

## Related API

- [LinearRing](/docs/api-reference/linearring)
- [MultiLineString](/docs/api-reference/multilinestring)
- [Functions](/docs/api-reference/functions)
