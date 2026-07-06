---
title: "Factories"
description: "Reference for the public conversion and normalization helpers in pygeoif.factories."
---

`pygeoif.factories` contains the main conversion helpers that turn external representations into geometry values or normalize existing geometry objects.

Import paths:

- `from pygeoif import shape, mapping, from_wkt, force_2d, force_3d, orient`
- `from pygeoif.factories import box`

## Public Functions

### `orient`

```python
orient(polygon: Polygon, ccw: bool = True) -> Polygon
```

Returns a new polygon whose exterior and interior rings are oriented consistently. When `ccw=True`, the exterior ring is counter-clockwise and holes are clockwise.

### `box`

```python
box(minx: float, miny: float, maxx: float, maxy: float, ccw: bool = True) -> Polygon
```

Builds a rectangular polygon from a bounding box.

### `shape`

```python
shape(
    context: Union[GeoType, GeoCollectionType, GeoInterface, GeoCollectionInterface]
) -> Union[Geometry, GeometryCollection]
```

Copies coordinates from a GeoJSON-like mapping or any object with `__geo_interface__` and returns a new geometry.

### `from_wkt`

```python
from_wkt(geo_str: str) -> Optional[Union[Geometry, GeometryCollection]]
```

Parses supported WKT into a geometry object. Raises `WKTParserError` on malformed or unsupported input.

### `mapping`

```python
mapping(ob: Union[GeoType, GeoCollectionType]) -> Union[GeoCollectionInterface, GeoInterface]
```

Returns the object's `__geo_interface__` mapping directly.

### `force_2d`

```python
force_2d(context: Union[GeoType, GeoCollectionType]) -> Union[Geometry, GeometryCollection]
```

Drops Z values recursively by rebuilding the geometry from a moved protocol mapping.

### `force_3d`

```python
force_3d(
    context: Union[GeoType, GeoCollectionType],
    z: float = 0,
) -> Union[Geometry, GeometryCollection]
```

Adds Z values recursively or overwrites missing Z components with the supplied default.

## Parameters

| Function | Parameter | Type | Default | Description |
|---|---|---|---|---|
| `orient` | `polygon` | `Polygon` | — | Polygon to reorient. |
| `orient` | `ccw` | `bool` | `True` | Exterior winding direction target. |
| `box` | `minx`, `miny`, `maxx`, `maxy` | `float` | — | Bounding box limits. |
| `box` | `ccw` | `bool` | `True` | Output ring winding direction. |
| `shape` | `context` | `Union[GeoType, GeoCollectionType, GeoInterface, GeoCollectionInterface]` | — | Mapping or protocol object to copy. |
| `from_wkt` | `geo_str` | `str` | — | WKT string to parse. |
| `mapping` | `ob` | `Union[GeoType, GeoCollectionType]` | — | Protocol-compatible object to inspect. |
| `force_2d` | `context` | `Union[GeoType, GeoCollectionType]` | — | Geometry or collection to normalize. |
| `force_3d` | `context` | `Union[GeoType, GeoCollectionType]` | — | Geometry or collection to normalize. |
| `force_3d` | `z` | `float` | `0` | Default Z value for 2D coordinates. |

## Examples

Converting from a mapping:

```python
from pygeoif import mapping, shape

payload = {"type": "Point", "coordinates": (1, 2)}
point = shape(payload)
print(mapping(point))
```

Dimensional normalization:

```python
from pygeoif import LineString, force_2d, force_3d

line = LineString([(0, 0), (1, 1)])
print(force_3d(line z=10).wkt)
print(force_2d(force_3d(line z=10)).wkt)
```

## Source Notes

- `shape()` dispatches by the input mapping's `type` field.
- `from_wkt()` uses a regular expression plus type-specific parsers for each supported geometry.
- `force_2d()` and `force_3d()` delegate recursive coordinate work to `move_geo_interface()` in `pygeoif/functions.py`.

## Related API

- [Functions](/docs/api-reference/functions)
- [Exceptions](/docs/api-reference/exceptions)
- [Types And Protocols](/docs/api-reference/types-and-protocols)
