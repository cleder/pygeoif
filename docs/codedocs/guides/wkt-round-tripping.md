---
title: "WKT Round Tripping"
description: "Parse WKT into geometry objects, normalize it, and serialize it back out safely."
---

WKT often shows up at system boundaries: databases, SQL dumps, queue payloads, or CLI tools. This guide shows how to parse WKT with `from_wkt()`, inspect and normalize the result, and emit WKT again through `.wkt`.

<Steps>
<Step>
### Parse the incoming WKT

```python
from pygeoif import from_wkt

geometry = from_wkt(
    "MULTIPOLYGON (((0 0, 3 0, 3 3, 0 3, 0 0)), ((10 10, 12 10, 12 12, 10 12, 10 10)))"
)

print(type(geometry).__name__)
print(len(tuple(geometry.geoms)))
```

</Step>
<Step>
### Inspect the normalized geometry object

```python
for polygon in geometry.geoms:
    print(polygon.bounds)
    print(polygon.convex_hull.wkt)
```

</Step>
<Step>
### Apply dimensional or orientation normalization

```python
from pygeoif import Polygon, force_3d, orient

single = from_wkt("POLYGON ((0 0, 4 0, 4 3, 0 3, 0 0))")
single = orient(single ccw=True)
single_3d = force_3d(single z=100)

print(single.exterior.is_ccw)
print(single_3d.wkt)
```

</Step>
<Step>
### Handle bad input explicitly

```python
from pygeoif import from_wkt
from pygeoif.exceptions import WKTParserError

try:
    from_wkt("POLYGON ((0 0, broken))")
except WKTParserError as exc:
    print(f"Could not parse payload: {exc}")
```

</Step>
</Steps>

Complete example:

```python
from pygeoif import Feature, from_wkt, orient

parcel = orient(
    from_wkt("POLYGON ((0 0, 0 5, 5 5, 5 0, 0 0), (1 1, 2 1, 2 2, 1 2, 1 1))"),
    ccw=True,
)

record = Feature(parcel, {"kind": "parcel"}, feature_id="p-100")

print(parcel.wkt)
print(record.__geo_interface__)
```

The important detail is that the round trip happens through a structured geometry model, not by regex-editing WKT strings in place. That means you can validate shape type, inspect bounds, adjust orientation, and only then serialize back to text.

This approach also keeps the rest of your code format-agnostic. Once the WKT is parsed, your application deals with geometry objects and shared helpers instead of raw strings. That makes it much easier to add GeoJSON export, dimensional normalization, or feature wrapping later without rewriting the ingestion path.
