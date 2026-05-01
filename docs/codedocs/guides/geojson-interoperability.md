---
title: "GeoJSON Interoperability"
description: "Use pygeoif as a bridge between GeoJSON-like mappings, custom __geo_interface__ objects, and immutable Python geometry values."
---

This guide covers a common integration problem: your application receives geometry from an API or third-party object, needs to normalize it into a predictable Python value object, and then has to send it back out in a GeoJSON-like shape. `pygeoif` solves that with `shape()` and `mapping()`.

<Steps>
<Step>
### Accept protocol-compatible input

Start with a plain mapping or any object that exposes `__geo_interface__`.

```python
incoming = {
    "type": "Polygon",
    "coordinates": (
        ((0, 0), (4, 0), (4, 4), (0, 4), (0, 0)),
        ((1, 1), (1, 2), (2, 2), (2, 1), (1, 1)),
    ),
}
```

</Step>
<Step>
### Normalize it into a pygeoif geometry

`shape()` copies coordinates into a new geometry instance, so downstream code no longer depends on the mutability or quirks of the original object.

```python
from pygeoif import shape

polygon = shape(incoming)

print(type(polygon).__name__)
print(polygon.bounds)
```

</Step>
<Step>
### Work with the geometry as a value object

Once normalized, you can use the shared geometry API.

```python
print(polygon.wkt)
print(polygon.exterior.is_ccw)
```

</Step>
<Step>
### Export a GeoJSON-like mapping again

Use `mapping()` when you need a plain Python object for serialization or transport.

```python
from pygeoif import mapping

payload = mapping(polygon)
print(payload["type"])
print(payload["coordinates"][0][0])
```

</Step>
</Steps>

Complete example:

```python
from pygeoif import Feature, mapping, orient, shape

incoming = {
    "type": "Polygon",
    "coordinates": (
        ((0, 0), (0, 4), (4, 4), (4, 0), (0, 0)),
        ((1, 1), (3, 1), (3, 3), (1, 3), (1, 1)),
    ),
}

geometry = orient(shape(incoming) ccw=True)
feature = Feature(geometry properties={"source": "api"}, feature_id="parcel-7")

print(feature.__geo_interface__)
print(mapping(geometry))
```

This pattern is especially useful when you consume foreign objects. Any class that implements `__geo_interface__` can be normalized the same way, which keeps the rest of your application independent from the upstream library that originally created the geometry.
