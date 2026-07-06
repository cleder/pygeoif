---
title: "Hypothesis Strategies"
description: "Reference for the optional property-based testing helpers in pygeoif.hypothesis.strategies."
---

`pygeoif.hypothesis.strategies` exposes Hypothesis composite strategies for generating coordinates and geometry instances. This module is optional at install time because the base package only depends on `typing_extensions`.

Import path: `from pygeoif.hypothesis.strategies import Srs, geometry_collections, line_coords, line_strings, linear_rings, multi_line_strings, multi_points, multi_polygons, point_coords, points, polygons`

## Public API

### `Srs`

```python
Srs(
    name: str,
    min_xyz: tuple[Optional[float], Optional[float], Optional[float]],
    max_xyz: tuple[Optional[float], Optional[float], Optional[float]],
)
```

Methods:

```python
Srs.longitudes() -> st.SearchStrategy[float]
Srs.latitudes() -> st.SearchStrategy[float]
Srs.elevations() -> st.SearchStrategy[float]
```

`Srs` constrains generated coordinates to a chosen coordinate range.

### Composite Strategies

```python
point_coords(draw: st.DrawFn, *, srs: Optional[Srs] = None, has_z: Optional[bool] = None) -> PointType
points(draw: st.DrawFn, *, srs: Optional[Srs] = None, has_z: Optional[bool] = None) -> Point
line_coords(
    draw: st.DrawFn,
    *,
    min_points: int,
    max_points: Optional[int] = None,
    srs: Optional[Srs] = None,
    has_z: Optional[bool] = None,
    unique: bool = False,
) -> LineType
line_strings(draw: st.DrawFn, *, max_points: Optional[int] = None, srs: Optional[Srs] = None, has_z: Optional[bool] = None) -> LineString
linear_rings(draw: st.DrawFn, *, max_points: Optional[int] = None, srs: Optional[Srs] = None, has_z: Optional[bool] = None) -> LinearRing
polygons(
    draw: st.DrawFn,
    *,
    max_points: Optional[int] = None,
    min_interiors: int = 0,
    max_interiors: int = 5,
    srs: Optional[Srs] = None,
    has_z: Optional[bool] = None,
) -> Polygon
multi_points(
    draw: st.DrawFn,
    *,
    min_points: int = 1,
    max_points: Optional[int] = None,
    srs: Optional[Srs] = None,
    has_z: Optional[bool] = None,
) -> MultiPoint
multi_line_strings(
    draw: st.DrawFn,
    *,
    min_lines: int = 1,
    max_lines: int = 5,
    max_points: int = 10,
    srs: Optional[Srs] = None,
    has_z: Optional[bool] = None,
) -> MultiLineString
multi_polygons(
    draw: st.DrawFn,
    *,
    min_polygons: int = 1,
    max_polygons: int = 3,
    max_points: int = 10,
    min_interiors: int = 0,
    max_interiors: int = 2,
    srs: Optional[Srs] = None,
    has_z: Optional[bool] = None,
) -> MultiPolygon
geometry_collections(
    draw: st.DrawFn,
    *,
    min_geoms: int = 1,
    max_geoms: int = 5,
    max_points: int = 20,
    min_interiors: int = 0,
    max_interiors: int = 5,
    max_leaves: int = 3,
    srs: Optional[Srs] = None,
    has_z: Optional[bool] = None,
) -> GeometryCollection
```

## Examples

Basic usage:

```python
from hypothesis import given
from pygeoif.hypothesis.strategies import points

@given(points(has_z=False))
def test_points_are_never_empty(point):
    assert not point.is_empty
```

Using an `Srs` constraint:

```python
from hypothesis import given
from pygeoif.hypothesis.strategies import Srs, point_coords

srs = Srs("Bounds", (-5.0, -10.0, 0.0), (5.0, 10.0, 100.0))

@given(point_coords(srs=srs, has_z=True))
def test_local_points(coord):
    assert -5.0 <= coord[0] <= 5.0
    assert -10.0 <= coord[1] <= 10.0
    assert 0.0 <= coord[2] <= 100.0
```

## Notes

- Coordinates are generated as 32-bit floats to limit precision issues, as stated in the module docstring.
- Several strategies raise `ValueError` for impossible limits such as `max_points < 2` for `line_strings()` or `max_points < 4` for `linear_rings()`.
- The collection strategy uses `st.recursive()` to allow nested geometry collections while bounding recursion through `max_leaves`.

## Related API

- [Hypothesis Testing Guide](/docs/guides/hypothesis-testing)
- [Types And Protocols](/docs/api-reference/types-and-protocols)
- [GeometryCollection](/docs/api-reference/geometrycollection)
