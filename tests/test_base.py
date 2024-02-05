"""Test Baseclass."""

from unittest import mock

import pytest

from pygeoif import geometry


def test_geometry_interface() -> None:
    """The geo interface must be implemented in subclasses."""
    base_geo = geometry._Geometry()

    with pytest.raises(NotImplementedError, match="^Must be implemented by subclass$"):
        assert base_geo.__geo_interface__


def test_bounds() -> None:
    """Subclasses must implement bounds."""
    base_geo = geometry._Geometry()
    with pytest.raises(NotImplementedError, match="^Must be implemented by subclass$"):
        assert base_geo.bounds


def test_wkt() -> None:
    """Implement wkt in subclasses."""
    base_geo = geometry._Geometry()
    with pytest.raises(NotImplementedError, match="^Must be implemented by subclass$"):
        assert base_geo.wkt


def test_empty() -> None:
    base_geo = geometry._Geometry()
    with pytest.raises(NotImplementedError, match="^Must be implemented by subclass$"):
        assert base_geo.is_empty


def test_wkt_inset() -> None:
    base_geo = geometry._Geometry()

    with pytest.raises(NotImplementedError, match="^Must be implemented by subclass$"):
        assert base_geo._wkt_inset == ""


def test_wkt_coordinates() -> None:
    base_geo = geometry._Geometry()
    with pytest.raises(NotImplementedError, match="^Must be implemented by subclass$"):
        assert base_geo._wkt_coords


def test_from_dict() -> None:
    base_geo = geometry._Geometry()
    with pytest.raises(NotImplementedError, match="^Must be implemented by subclass$"):
        assert base_geo._from_dict({"type": "_Geometry"})  # type: ignore


def test_has_z() -> None:
    base_geo = geometry._Geometry()
    with pytest.raises(NotImplementedError, match="^Must be implemented by subclass$"):
        assert base_geo.has_z


def test_convex_hull() -> None:
    with mock.patch("pygeoif.geometry._Geometry.has_z"):
        base_geo = geometry._Geometry()
        with pytest.raises(
            NotImplementedError,
            match="^Must be implemented by subclass$",
        ):
            assert base_geo.convex_hull


def test_get_bounds() -> None:
    base_geo = geometry._Geometry()
    with pytest.raises(NotImplementedError, match="^Must be implemented by subclass$"):
        assert base_geo._get_bounds()


@pytest.mark.parametrize(
    ("attr_val", "expected_error", "expected_error_message"),
    [
        # Happy path tests
        (
            ("attribute", "value"),
            AttributeError,
            "Attributes of _Geometry cannot be changed",
        ),
        (
            ("another_attribute", 123),
            AttributeError,
            "Attributes of _Geometry cannot be changed",
        ),
        (
            ("yet_another_attribute", [1, 2, 3]),
            AttributeError,
            "Attributes of _Geometry cannot be changed",
        ),
        # Edge cases
        (("", "value"), AttributeError, "Attributes of _Geometry cannot be changed"),
        ((None, "value"), TypeError, ".*attribute name must be string.*"),
        # Error cases
        ((123, "value"), TypeError, ".*attribute name must be string.*"),
        (([1, 2, 3], "value"), TypeError, ".*attribute name must be string.*"),
    ],
)
def test_setattr(attr_val, expected_error, expected_error_message) -> None:
    base_geo = geometry._Geometry()

    with pytest.raises(expected_error, match=f"^{expected_error_message}$"):
        setattr(base_geo, *attr_val)


@pytest.mark.parametrize(
    ("attr", "expected_error", "expected_error_message"),
    [
        (
            "attr1",
            AttributeError,
            "Attributes of _Geometry cannot be deleted",
        ),  # realistic test value
        (
            "",
            AttributeError,
            "Attributes of _Geometry cannot be deleted",
        ),  # edge case: empty string
        (
            None,
            TypeError,
            ".*attribute name must be string.*",
        ),  # edge case: None
        (
            123,
            TypeError,
            ".*attribute name must be string.*",
        ),  # error case: non-string attribute
    ],
    ids=[
        "realistic_test_value",
        "edge_case_empty_string",
        "edge_case_None",
        "error_case_non_string_attribute",
    ],
)
def test_delattr(attr, expected_error, expected_error_message) -> None:
    # Arrange
    base_geo = geometry._Geometry()

    # Act
    with pytest.raises(expected_error, match=f"^{expected_error_message}$"):
        delattr(base_geo, attr)
