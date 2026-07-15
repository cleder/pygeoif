---
title: "Polygon"
description: "Reference for pygeoif.Polygon, including shells, holes, and polygon-specific constructors."
---

`Polygon` models an exterior ring plus zero or more interior rings. It is defined in `pygeoif/geometry.py` and exported as `pygeoif.Polygon`.

## Signature

```python
Polygon(shell: LineType, holes: Optional[Sequence[LineType]] = None) -> None
```

## Constructor Parameters

| Parameter | Type | Default | Description |
|---|---|---|---|
| `shell` | `LineType` | — | Exterior ring coordinates. |
| `holes` | `Optional[Sequence[LineType]]` | `None` | Optional interior ring coordinate sequences. |

## Public Properties And Methods

### Properties

| Name | Type | Description |
|---|---|---|
| `exterior` | `LinearRing` | Exterior ring of the polygon. |
| `interiors` | `Iterator[LinearRing]` | Interior rings yielded lazily. |
| `coords` | `PolygonType` | Exterior ring, then optional interior ring tuple. |
| `is_empty` | `bool` | True when the exterior ring is empty. |
| `has_z` | `Optional[bool]` | Z-presence based on the exterior ring. |
| `bounds` | `tuple[float, float, float, float] \| tuple[()]` | XY extent of the exterior ring. |
| `convex_hull` | `Point \| LineString \| Polygon \| None` | Hull of the polygon's exterior coordinates projected to XY. |
| `wkt` | `str` | WKT representation with optional interior rings. |
| `__geo_interface__` | `GeoInterface` | Polygon mapping with shell then holes. |

### Class Methods

```python
Polygon.from_coordinates(coordinates: PolygonType) -> Polygon
Polygon.from_linear_rings(shell: LinearRing, *args: LinearRing) -> Polygon
```

## Examples

Basic usage:

```python
from pygeoif import Polygon

polygon = Polygon([(0, 0), (4, 0), (4, 3), (0, 3), (0, 0)])
print(polygon.exterior.coords)
print(polygon.bounds)
```

Polygon with holes:

```python
from pygeoif import LinearRing, Polygon

shell = LinearRing([(0, 0), (5, 0), (5, 5), (0, 5)])
hole = LinearRing([(1, 1), (2, 1), (2, 2), (1, 2)])
polygon = Polygon.from_linear_rings(shell, hole)

print([ring.coords for ring in polygon.interiors])
print(polygon.wkt)
```

## Notes

- `coords` is intentionally public even though Shapely does not expose polygon coordinates in the same way.
- Empty polygons can be constructed indirectly through `_from_dict()` when the incoming coordinates are empty.
- The class does not validate topology such as ring overlap or self-intersection.

## Related API

- [LinearRing](/docs/api-reference/linearring)
- [MultiPolygon](/docs/api-reference/multipolygon)
- [Factories](/docs/api-reference/factories)
