---
title: "Hypothesis Testing"
description: "Generate realistic random geometries with pygeoif.hypothesis.strategies for property-based tests."
---

If your project already uses Hypothesis, `pygeoif` includes a purpose-built strategy module for generating geometry objects and coordinate sequences. This guide shows how to install the optional dependency set and use those strategies to test geometry-heavy code without hand-rolling data generators.

<Steps>
<Step>
### Install the optional testing dependencies

```bash
pip install "pygeoif[hypothesis]"
```

</Step>
<Step>
### Generate geometry objects directly

```python
from hypothesis import given
from pygeoif.hypothesis.strategies import points, polygons


@given(points(has_z=False), polygons(max_points=8, has_z=False))
def test_bounds_are_ordered(point, polygon):
    minx, miny, maxx, maxy = point.bounds
    assert minx <= maxx
    assert miny <= maxy
    pminx, pminy, pmaxx, pmaxy = polygon.bounds
    assert pminx <= pmaxx
    assert pminy <= pmaxy
```

</Step>
<Step>
### Constrain generated coordinates

Use `Srs` and the `srs=` parameter when you need realistic coordinate ranges.

```python
from hypothesis import given
from pygeoif.hypothesis.strategies import Srs, point_coords

web_mercator_like = Srs(
    name="Local",
    min_xyz=(-1000.0, -1000.0, 0.0),
    max_xyz=(1000.0, 1000.0, 500.0),
)


@given(point_coords(srs=web_mercator_like, has_z=True))
def test_points_stay_in_range(coord):
    assert -1000.0 <= coord[0] <= 1000.0
    assert -1000.0 <= coord[1] <= 1000.0
    assert 0.0 <= coord[2] <= 500.0
```

</Step>
<Step>
### Generate nested collections when needed

```python
from hypothesis import given
from pygeoif.hypothesis.strategies import geometry_collections


@given(geometry_collections(max_geoms=4, max_points=6, max_leaves=2))
def test_collection_serializes(collection):
    payload = collection.__geo_interface__
    assert payload["type"] == "GeometryCollection"
    assert len(payload["geometries"]) <= 4
```

</Step>
</Steps>

Complete example:

```python
from hypothesis import given
from pygeoif import mapping, shape
from pygeoif.hypothesis.strategies import multi_polygons


@given(multi_polygons(max_polygons=2, max_points=6, min_interiors=0, max_interiors=1))
def test_round_trip_via_protocol(geom):
    payload = mapping(geom)
    restored = shape(payload)
    assert restored == geom
```

The strategy module mirrors the public geometry model closely, so your tests stay aligned with real library behavior. That is especially useful when you want to stress round-tripping, bounds, or shape conversion logic across many geometry shapes and dimensional combinations.

Because the strategies return real `pygeoif` objects, the same test can cover constructor behavior, protocol serialization, and conversion helpers in one place. That makes the optional Hypothesis integration more than a convenience module; it is a practical way to test the exact edge cases the library itself is built around.
