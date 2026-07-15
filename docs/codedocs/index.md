---
title: "Getting Started"
description: "Learn what pygeoif does, why it exists, and how to start working with immutable GeoJSON-like geometries in Python."
---

`pygeoif` is a pure-Python geometry library that implements the `__geo_interface__` protocol, WKT conversion, and lightweight geometry value objects without a compiled GIS dependency.

## The Problem

- Many Python GIS stacks are excellent but heavy when you only need protocol-compatible geometry objects.
- Interoperability between GeoJSON-like mappings, custom geometry objects, and WKT strings is easy to get wrong by hand.
- Dimensionality issues such as mixing 2D and 3D coordinates often surface late and produce inconsistent downstream behavior.
- Property-based testing of geometry-heavy code usually requires custom strategies before you can even start testing real edge cases.

## The Solution

`pygeoif` gives you immutable geometry classes, GeoJSON-like mappings through `__geo_interface__`, constructors that copy input data instead of aliasing it, and helpers for WKT parsing, dimensional coercion, orientation, and Hypothesis strategy generation.

```python
from pygeoif import Point, Polygon, Feature, mapping, orient

parcel = Polygon(
    shell=[(0, 0), (4, 0), (4, 3), (0, 3), (0, 0)],
    holes=[[(1, 1), (1, 2), (2, 2), (2, 1), (1, 1)]],
)

feature = Feature(
    orient(parcel ccw=True),
    properties={"name": "parcel-a"},
    feature_id="parcel-1",
)

print(mapping(feature.geometry))
print(feature.__geo_interface__["properties"])
```

## Installation

<Tabs items={["pip", "uv", "poetry", "conda"]}>
<Tab value="pip">

```bash
pip install pygeoif
```

</Tab>
<Tab value="uv">

```bash
uv add pygeoif
```

</Tab>
<Tab value="poetry">

```bash
poetry add pygeoif
```

</Tab>
<Tab value="conda">

```bash
conda install -c conda-forge pygeoif
```

</Tab>
</Tabs>

`pygeoif` requires Python 3.9 or newer and declares support for CPython, PyPy, and GraalPy in [`pyproject.toml`](https://github.com/cleder/pygeoif/blob/develop/pyproject.toml).

## Quick Start

```python
from pygeoif import Point, LineString, FeatureCollection, Feature, from_wkt

home = Point(-122.4, 37.78)
route = LineString([(-122.4, 37.78), (-122.41, 37.79), (-122.42, 37.8)])
copied = from_wkt("POINT (-122.4 37.78)")

collection = FeatureCollection(
    [
        Feature(home, {"kind": "home"}, feature_id="home"),
        Feature(route, {"kind": "route"}, feature_id="route"),
    ]
)

print(home.wkt)
print(route.bounds)
print(copied == home)
print(collection.__geo_interface__["type"])
```

Expected output:

```text
POINT (-122.4 37.78)
(-122.42, 37.78, -122.4, 37.8)
True
FeatureCollection
```

## Key Features

- Immutable geometry classes in [`pygeoif/geometry.py`](https://github.com/cleder/pygeoif/blob/develop/pygeoif/geometry.py).
- Root-level convenience exports in [`pygeoif/__init__.py`](https://github.com/cleder/pygeoif/blob/develop/pygeoif/__init__.py).
- GeoJSON-like interoperability via `__geo_interface__`, `shape()`, and `mapping()`.
- WKT parsing and formatting through `from_wkt()` and `.wkt`.
- 2D or 3D coercion with `force_2d()` and `force_3d()`.
- Polygon ring orientation helpers backed by `signed_area()`.
- Optional Hypothesis strategies in `pygeoif.hypothesis.strategies`.

## Where To Next

<Cards>
  <Card title="Architecture" href="/docs/architecture">See how geometry classes, factories, and algorithms fit together internally.</Card>
  <Card title="Core Concepts" href="/docs/geometry-model">Understand immutable geometries, `__geo_interface__`, conversion, and features.</Card>
  <Card title="API Reference" href="/docs/api-reference/point">Jump into the class and module reference for every public surface.</Card>
</Cards>
