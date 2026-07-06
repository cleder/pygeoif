---
title: "LinearRing"
description: "Reference for pygeoif.LinearRing, the self-closing ring used by polygons."
---

`LinearRing` inherits from `LineString` and represents a closed ring. It is implemented in `pygeoif/geometry.py` and exported as `pygeoif.LinearRing`.

## Signature

```python
LinearRing(coordinates: LineType) -> None
```

## Constructor Parameters

| Parameter | Type | Default | Description |
|---|---|---|---|
| `coordinates` | `LineType` | — | Sequence of point tuples; the first coordinate is appended automatically if needed. |

## Public Properties

| Name | Type | Description |
|---|---|---|
| `coords` | `LineType` | Closed coordinate sequence. |
| `centroid` | `Optional[Point]` | 2D centroid of the ring, or `None` for degenerate rings. |
| `is_ccw` | `bool` | True when `signed_area(coords) >= 0`. |
| `bounds` | `tuple[float, float, float, float] \| tuple[()]` | XY extent inherited from `LineString`. |
| `wkt` | `str` | WKT representation using `LINEARRING`. |

## Internal Behavior

`LinearRing.__init__` first delegates to `LineString`, then appends the first point again if the line is not already closed. The `centroid` property uses `centroid()` and `signed_area()` from `pygeoif/functions.py`; it only works for 2D data and raises `DimensionError` for 3D rings.

## Examples

Basic usage:

```python
from pygeoif import LinearRing

ring = LinearRing([(0, 0), (2, 0), (2, 1), (0, 1)])
print(ring.coords)
print(ring.is_ccw)
```

Centroid calculation:

```python
from pygeoif import LinearRing

ring = LinearRing([(0, 0), (4, 0), (4, 2), (0, 2)])
center = ring.centroid

print(center)
print(center.__geo_interface__)
```

## Notes

- Rings self-close automatically, so you can omit the final repeated point in many cases.
- `LinearRing` does not validate self-intersection; invalid rings can still be constructed.
- `centroid` works only for 2D rings because the implementation is explicitly XY-only.

## When To Use It

Use `LinearRing` directly when you care about winding, centroid calculation, or reusable ring objects. In many applications you will meet it indirectly through `Polygon.exterior` and `Polygon.interiors`, but constructing rings yourself can still be useful when you normalize polygon input before building the polygon. Because the class inherits most behavior from `LineString`, it stays lightweight while still giving you ring-specific semantics.

## Related API

- [Polygon](/docs/api-reference/polygon)
- [Functions](/docs/api-reference/functions)
- [Factories](/docs/api-reference/factories)
