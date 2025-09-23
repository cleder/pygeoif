"""Test LineStrings with Hypothesis."""

import pytest
from hypothesis import given

from pygeoif import geometry
from pygeoif.factories import force_2d
from pygeoif.factories import force_3d
from pygeoif.factories import from_wkt
from pygeoif.factories import shape
from pygeoif.hypothesis.strategies import epsg4326
from pygeoif.hypothesis.strategies import line_strings


def test_max_points_lt_2() -> None:
    with pytest.raises(ValueError, match=r"^max_points must be greater than 1"):
        line_strings(max_points=1).example()


@given(line_strings(srs=epsg4326))
def test_from_wkt_epsg_4326(line: geometry.LineString) -> None:
    assert line == from_wkt(str(line))


@given(line_strings())
def test_repr_eval(line: geometry.LineString) -> None:
    assert eval(repr(line), {}, {"LineString": geometry.LineString}) == line


@given(line_strings())
def test_shape(line: geometry.LineString) -> None:
    assert line == shape(line)


@given(line_strings())
def test_bounds(line: geometry.LineString) -> None:
    assert line.bounds == force_2d(line).bounds


@given(line_strings())
def test_convex_hull(line: geometry.LineString) -> None:
    assert line.convex_hull == force_2d(line.convex_hull)
    assert line.convex_hull == force_2d(line).convex_hull
    assert line.convex_hull == force_3d(line).convex_hull


@given(line_strings())
def test_convex_hull_bounds(line: geometry.LineString) -> None:
    """
    Test that the convex hull calculation preserves the original bounds.

    The bounds of the convex hull of a LineString must be equal to the bounds of
    the LineString itself.
    """
    assert line.convex_hull
    assert line.convex_hull.bounds == line.bounds
