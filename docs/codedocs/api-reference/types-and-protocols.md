---
title: "Types And Protocols"
description: "Reference for the public type aliases, TypedDict definitions, and protocols exported by pygeoif.types."
---

`pygeoif.types` exports the shared type vocabulary used by the rest of the package. These are Python typing constructs rather than TypeScript types, but they are still part of the public API and useful when you annotate your own wrappers or protocol adapters.

Import path: `from pygeoif.types import ...`

## Type Aliases

```python
Point2D = tuple[float, float]
Point3D = tuple[float, float, float]
PointType = Union[Point2D, Point3D]
LineType = Union[Sequence[Point2D], Sequence[Point3D]]
Interiors = Optional[Sequence[LineType]]
PolygonType = Union[
    Union[tuple[Sequence[Point2D], Sequence[Sequence[Point2D]]], tuple[Sequence[Point2D]]],
    Union[tuple[Sequence[Point3D], Sequence[Sequence[Point3D]]], tuple[Sequence[Point3D]]],
]
MultiGeometryType = Sequence[Union[PointType, LineType, PolygonType]]
Bounds = tuple[float, float, float, float]
CoordinatesType = Union[PointType, LineType, Sequence[LineType]]
MultiCoordinatesType = Sequence[CoordinatesType]
```

## TypedDict Definitions

```python
class GeoInterface(TypedDict):
    type: GeomType
    coordinates: Union[CoordinatesType, MultiCoordinatesType]
    bbox: NotRequired[Bounds]

class GeoCollectionInterface(TypedDict):
    type: Literal["GeometryCollection"]
    geometries: Sequence[Union[GeoInterface, "GeoCollectionInterface"]]
    bbox: NotRequired[Bounds]

class GeoFeatureInterface(TypedDict):
    type: Literal["Feature"]
    bbox: NotRequired[Bounds]
    properties: NotRequired[dict[str, Any]]
    id: NotRequired[Union[str, int]]
    geometry: GeoInterface

class GeoFeatureCollectionInterface(TypedDict):
    type: Literal["FeatureCollection"]
    features: Sequence[GeoFeatureInterface]
    bbox: NotRequired[Bounds]
    id: NotRequired[Union[str, int]]
```

## Protocols

```python
class GeoType(Protocol):
    @property
    def __geo_interface__(self) -> GeoInterface: ...

class GeoCollectionType(Protocol):
    @property
    def __geo_interface__(self) -> GeoCollectionInterface: ...
```

## When To Use Them

- Use `PointType`, `LineType`, and `PolygonType` when you accept raw coordinate tuples in your own helpers.
- Use `GeoInterface` and `GeoCollectionInterface` when you want to type GeoJSON-like dictionaries exchanged with `shape()` or `mapping()`.
- Use `GeoType` and `GeoCollectionType` when you accept foreign objects that implement `__geo_interface__` without depending on their concrete class.

## Example

```python
from pygeoif import shape
from pygeoif.types import GeoInterface

def build_geometry(payload: GeoInterface):
    return shape(payload)

point = build_geometry({"type": "Point", "coordinates": (1, 2)})
print(point.wkt)
```

## Notes

- The `GeomType` literal covers only the non-collection geometry names implemented in `pygeoif`.
- Feature-related TypedDicts live here even though feature classes themselves live in `pygeoif/feature.py`.
- These type exports are especially useful when integrating with static type checking tools such as mypy or pyright, both of which are configured in `pyproject.toml`.

## Related API

- [Factories](/docs/api-reference/factories)
- [Functions](/docs/api-reference/functions)
- [Feature](/docs/api-reference/feature)
