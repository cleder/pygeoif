---
title: "MultiLineString"
description: "Reference for pygeoif.MultiLineString, the immutable collection of line strings."
---

`MultiLineString` stores many `LineString` objects and is defined in `pygeoif/geometry.py`. Import it with `from pygeoif import MultiLineString`.

## Signature

```python
MultiLineString(lines: Sequence[LineType], unique: bool = False) -> None
```

## Constructor Parameters

| Parameter | Type | Default | Description |
|---|---|---|---|
| `lines` | `Sequence[LineType]` | — | Coordinate sequences used to build the member line strings. |
| `unique` | `bool` | `False` | Deduplicates lines using a set conversion. Ordering is not preserved. |

## Public API

| Name | Type | Description |
|---|---|---|
| `geoms` | `Iterator[LineString]` | Yields non-empty member lines. |
| `has_z` | `Optional[bool]` | True if any member line has Z values. |
| `is_empty` | `bool` | True when all members are empty. |
| `bounds` | `tuple[float, float, float, float] \| tuple[()]` | Aggregate XY extent. |
| `wkt` | `str` | WKT representation such as `MULTILINESTRING ((...),(...))`. |
| `__geo_interface__` | `GeoInterface` | GeoJSON-like mapping for the collection. |
| `__len__()` | `int` | Number of stored member lines. |

### Class Methods

```python
MultiLineString.from_linestrings(*args: LineString, unique: bool = False) -> MultiLineString
```

## Examples

Basic usage:

```python
from pygeoif import MultiLineString

lines = MultiLineString([[(0, 0), (1, 1)], [(2, 2), (3, 2)]])
print(len(lines))
print(lines.bounds)
```

Building from `LineString` instances:

```python
from pygeoif import LineString, MultiLineString

multi = MultiLineString.from_linestrings(
    LineString([(0, 0), (1, 1)]),
    LineString([(1, 1), (2, 1)]),
)

print([line.wkt for line in multi.geoms])
print(multi.__geo_interface__)
```

## Notes

- Deduplication with `unique=True` converts each line to a tuple and may reorder the result.
- The class aggregates hull input by yielding points from each member line.
- The public surface is intentionally small because `_MultiGeometry` provides most collection behavior.

## Related API

- [LineString](/docs/api-reference/linestring)
- [GeometryCollection](/docs/api-reference/geometrycollection)
- [Functions](/docs/api-reference/functions)
