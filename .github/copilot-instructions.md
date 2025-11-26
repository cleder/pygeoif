# PyGeoIf Copilot Instructions

## 1. Overview
This file enables AI coding assistants to generate features aligned with the `pygeoif` project’s architecture and style. It is based only on actual, observed patterns from the codebase — not invented practices. `pygeoif` is a pure Python implementation of the `__geo_interface__` protocol (GeoJSON-like) for geospatial vector data.

## 2. File Category Reference

### Geometry Implementation
- **Description**: Core geometry classes (Point, Polygon, etc.).
- **Examples**: `pygeoif/geometry.py`, `pygeoif/feature.py`
- **Conventions**:
    - Inherit from `_Geometry` or `_MultiGeometry`.
    - Define `__slots__`.
    - Implement `__geo_interface__`, `bounds`, `wkt`, `is_empty`, `has_z`.
    - Implement `from_coordinates` class method.

### Utility Functions
- **Description**: Standalone pure functions for geometric calculations.
- **Examples**: `pygeoif/functions.py`
- **Conventions**:
    - Must be pure functions.
    - Operate on coordinate tuples/sequences when possible.
    - Explicit type hints.

### Types
- **Description**: Static type definitions.
- **Examples**: `pygeoif/types.py`, `pygeoif/py.typed`
- **Conventions**:
    - Use `typing_extensions` for compatibility.
    - Use `TypedDict` for interfaces.
    - Use `Protocol` for structural types.

### Testing Strategies
- **Description**: Hypothesis strategies for property-based testing.
- **Examples**: `pygeoif/hypothesis/strategies.py`
- **Conventions**:
    - Use `@st.composite`.
    - Use `st.floats(width=32)` for precision control.
    - Support `Srs` (Spatial Reference Systems).

### Tests
- **Description**: Unit and property-based tests.
- **Examples**: `tests/test_point.py`, `tests/test_polygon.py`
- **Conventions**:
    - Use `pytest`.
    - Use `@given` with custom strategies.
    - Aim for 100% branch coverage.

### Exceptions
- **Description**: Custom exception classes.
- **Examples**: `pygeoif/exceptions.py`
- **Conventions**:
    - Inherit from `Exception` or built-ins.
    - Name ends in `Error`.

### Metadata
- **Description**: Project metadata and public API exposure.
- **Examples**: `pygeoif/about.py`, `pygeoif/__init__.py`
- **Conventions**:
    - Version in `about.py`.
    - Public API in `__init__.py`.

### Configuration
- **Description**: Tool configuration.
- **Examples**: `pyproject.toml`, `tox.ini`
- **Conventions**:
    - Centralize in `pyproject.toml` where possible.

### Documentation
- **Description**: Project documentation.
- **Examples**: `README.rst`
- **Conventions**:
    - Use ReStructuredText (`.rst`).
    - Include `pycon` doctests.

## 3. Feature Scaffold Guide

To implement a new feature (e.g., a new Geometry type):

1.  **Implementation**: Add the class to `pygeoif/geometry.py` (or a new file if it's a major addition, but `geometry.py` is preferred for core types).
    - Inherit from `_Geometry`.
    - Implement required properties (`__geo_interface__`, `bounds`, `wkt`, etc.).
2.  **Types**: Add any new type aliases or interfaces to `pygeoif/types.py`.
3.  **Strategies**: Add a hypothesis strategy to `pygeoif/hypothesis/strategies.py` to generate instances of the new type.
4.  **Tests**: Create a new test file `tests/test_<typename>.py`.
    - Add property-based tests using the new strategy.
    - Add unit tests for specific edge cases.
5.  **Exposure**: Export the new class in `pygeoif/__init__.py`.

## 4. Integration Rules

- **Geometry Inheritance**: All geometries **must** inherit from `_Geometry` (or `_MultiGeometry`) to ensure consistent behavior and immutability.
- **Geo Interface**: All geometries and features **must** implement the `__geo_interface__` property returning a GeoJSON-compatible dictionary.
- **Pure Python**: Do **not** introduce C extensions or heavy dependencies. The library must remain "Shapely ultralight".
- **Testing**: All new logic **must** be tested with `hypothesis`.
- **Typing**: All code **must** pass `mypy` strict checks. Use `cast` where necessary for dynamic dictionary returns.

## 5. Example Prompt Usage

**User Prompt:**
> "Add a Circle geometry type that is defined by a center point and a radius."

**Copilot Response:**
- `pygeoif/geometry.py`: Add `Circle` class inheriting from `_Geometry`. Implement `__geo_interface__` (approximated as Polygon or Point with properties?), `bounds`, `wkt`.
- `pygeoif/types.py`: Add `CircleType` alias.
- `pygeoif/hypothesis/strategies.py`: Add `circles()` strategy generating random center and radius.
- `tests/test_circle.py`: Add tests verifying `bounds`, `wkt`, and `__geo_interface__` properties.
- `pygeoif/__init__.py`: Export `Circle`.
