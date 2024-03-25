"""Test LineStrings with Hypothesis."""

from hypothesis import given

from pygeoif import geometry
from pygeoif.factories import force_2d
from pygeoif.factories import force_3d
from pygeoif.factories import from_wkt
from pygeoif.factories import shape
from pygeoif.hypothesis.strategies import epsg4326
from pygeoif.hypothesis.strategies import multi_line_strings


@given(multi_line_strings(srs=epsg4326))
def test_from_wkt_epsg_4326(line: geometry.MultiLineString) -> None:
    assert line == from_wkt(str(line))


@given(multi_line_strings())
def test_repr_eval(line: geometry.MultiLineString) -> None:
    assert eval(repr(line), {}, {"MultiLineString": geometry.MultiLineString}) == line


@given(multi_line_strings())
def test_shape(line: geometry.MultiLineString) -> None:
    assert line == shape(line)


@given(multi_line_strings())
def test_bounds(line: geometry.MultiLineString) -> None:
    assert line.bounds == force_2d(line).bounds


@given(multi_line_strings())
def test_convex_hull(line: geometry.MultiLineString) -> None:
    assert line.convex_hull == force_2d(line.convex_hull)
    assert line.convex_hull == force_2d(line).convex_hull
    assert line.convex_hull == force_3d(line).convex_hull


@given(multi_line_strings())
def test_convex_hull_bounds(line: geometry.MultiLineString) -> None:
    """
    Test that the convex hull calculation preserves the original bounds.

    The bounds of the convex hull of a MultiLineString must be equal to the bounds of
    the MultiLineString itself.
    """
    assert line.convex_hull
    assert line.convex_hull.bounds == line.bounds
