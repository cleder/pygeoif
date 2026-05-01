---
title: "Exceptions"
description: "Reference for the custom exception types exported by pygeoif.exceptions."
---

`pygeoif.exceptions` defines the small set of custom exception classes raised across the package.

Import path: `from pygeoif.exceptions import DimensionError, InvalidGeometryError, WKTParserError`

## Exception Classes

### `DimensionError`

```python
class DimensionError(ValueError)
```

Raised when geometry dimensionality is inconsistent or unsupported. Common cases include accessing `.z` on a 2D point or mixing 2D and 3D coordinates in one `LineString`.

### `WKTParserError`

```python
class WKTParserError(AttributeError)
```

Raised by `from_wkt()` when the input WKT is unsupported or cannot be parsed successfully.

### `InvalidGeometryError`

```python
class InvalidGeometryError(ValueError)
```

Declared as part of the public API for invalid geometry cases. In the current source it is exported but not heavily used by the core constructors.

## Examples

Handling dimensional errors:

```python
from pygeoif import Point
from pygeoif.exceptions import DimensionError

try:
    print(Point(1, 2).z)
except DimensionError as exc:
    print(exc)
```

Handling parse failures:

```python
from pygeoif import from_wkt
from pygeoif.exceptions import WKTParserError

try:
    from_wkt("POINT broken")
except WKTParserError as exc:
    print(exc)
```

## Notes

- `WKTParserError` subclasses `AttributeError`, which may matter if you already catch parsing-related `ValueError` elsewhere.
- `InvalidGeometryError` is part of the public contract even though topology validation is intentionally lightweight.
- Many invalid semantic geometries are still constructible because the library favors interoperability and lightweight value objects over heavy validation.

## Source Behavior

All three exception classes are declared in `pygeoif/exceptions.py` as tiny marker types with explanatory docstrings and no extra instance state. That simplicity is deliberate. The rest of the package can raise domain-specific errors without introducing a larger exception hierarchy or carrying hidden metadata. In practice, that means you should treat these exceptions as semantic signals about what failed rather than as rich structured error payloads.

That also keeps the exceptions easy to catch selectively in boundary code such as parsers, import pipelines, and validation wrappers.

## Related API

- [Factories](/docs/api-reference/factories)
- [Point](/docs/api-reference/point)
- [LinearRing](/docs/api-reference/linearring)
