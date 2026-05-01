---
title: "Functions"
description: "Reference for the low-level geometry algorithms and comparison helpers in pygeoif.functions."
---

`pygeoif.functions` contains the reusable geometry algorithms used throughout the package. These are public helpers, even though most applications consume them indirectly through geometry properties or factory helpers.

Import path: `from pygeoif.functions import centroid, compare_coordinates, compare_geo_interface, convex_hull, dedupe, move_coordinate, move_coordinates, signed_area`

## Public Functions

### `signed_area`

```python
signed_area(coords: LineType) -> float
```

Returns the signed area of a ring using an XY shoelace-style algorithm. Values greater than or equal to zero indicate counter-clockwise winding.

### `centroid`

```python
centroid(coords: LineType) -> tuple[Point2D, float]
```

Returns the XY centroid and signed area for a ring-like coordinate sequence. Degenerate shapes return `(nan, nan)` plus area `0` or `nan`.

### `dedupe`

```python
dedupe(coords: LineType) -> LineType
```

Removes consecutive duplicate coordinates.

### `convex_hull`

```python
convex_hull(points: Iterable[Point2D]) -> LineType
```

Builds a hull from 2D points using Andrew's monotone chain algorithm.

### `compare_coordinates`

```python
compare_coordinates(
    coords: Union[float, CoordinatesType, MultiCoordinatesType],
    other: Union[float, CoordinatesType, MultiCoordinatesType],
) -> bool
```

Recursively compares numeric coordinates using `math.isclose()` for scalar values.

### `compare_geo_interface`

```python
compare_geo_interface(
    first: Union[GeoInterface, GeoCollectionInterface],
    second: Union[GeoInterface, GeoCollectionInterface],
) -> bool
```

Compares two protocol mappings, handling nested geometry collections recursively.

### `move_coordinate`

```python
move_coordinate(coordinate: PointType, move_by: PointType) -> PointType
```

Translates one point tuple and forces the output dimension to match `move_by`.

### `move_coordinates`

```python
move_coordinates(coordinates: CoordinatesType, move_by: PointType) -> CoordinatesType
```

Recursively translates nested coordinate sequences.

## Examples

Orientation and centroid helpers:

```python
from pygeoif.functions import centroid, signed_area

ring = [(0, 0), (4, 0), (4, 2), (0, 2), (0, 0)]
print(signed_area(ring))
print(centroid(ring))
```

Recursive coordinate movement:

```python
from pygeoif.functions import move_coordinates

coords = (((0, 0), (1, 1)), ((2, 2), (3, 3)))
print(move_coordinates(coords, (10, -5, 100)))
```

## Notes

- `convex_hull()` is 2D-only and expects `Point2D` inputs; 3D callers project first.
- `compare_coordinates()` treats shape structure recursively, so mismatched nesting returns `False`.
- `move_coordinate()` can either add or drop a Z component depending on the `move_by` vector length.

## Related API

- [Factories](/docs/api-reference/factories)
- [Types And Protocols](/docs/api-reference/types-and-protocols)
- [LinearRing](/docs/api-reference/linearring)
