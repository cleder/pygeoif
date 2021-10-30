"""Test Polygon."""
from unittest import mock

from pygeoif import geometry


def test_coords():
    polygon = geometry.Polygon([(0, 0), (1, 1), (1, 0), (0, 0)])

    assert polygon.coords == (((0.0, 0.0), (1.0, 1.0), (1.0, 0.0), (0.0, 0.0)),)


def test_coords_with_holes():
    e = [(0, 0), (0, 2), (2, 2), (2, 0), (0, 0)]
    i = [(1, 0), (0.5, 0.5), (1, 1), (1.5, 0.5), (1, 0)]
    polygon = geometry.Polygon(e, [i])
    assert polygon.coords == (
        ((0.0, 0.0), (0.0, 2.0), (2.0, 2.0), (2.0, 0.0), (0.0, 0.0)),
        (((1.0, 0.0), (0.5, 0.5), (1.0, 1.0), (1.5, 0.5), (1.0, 0.0)),),
    )


def test_geo_interface_shell_only():
    polygon = geometry.Polygon([(0, 0), (1, 1), (1, 0), (0, 0)])

    assert polygon.__geo_interface__, {
        "type": "Polygon",
        "bbox": (0.0, 0.0, 1.0, 1.0),
        "coordinates": (((0.0, 0.0), (1.0, 1.0), (1.0, 0.0), (0.0, 0.0)),),
    }


def test_geo_interface_with_holes():
    e = [(0, 0), (0, 2), (2, 2), (2, 0), (0, 0)]
    i = [(1, 0), (0.5, 0.5), (1, 1), (1.5, 0.5), (1, 0)]
    polygon = geometry.Polygon(e, [i])

    assert polygon.__geo_interface__ == {
        "type": "Polygon",
        "bbox": (0.0, 0.0, 2.0, 2.0),
        "coordinates": (
            ((0.0, 0.0), (0.0, 2.0), (2.0, 2.0), (2.0, 0.0), (0.0, 0.0)),
            ((1.0, 0.0), (0.5, 0.5), (1.0, 1.0), (1.5, 0.5), (1.0, 0.0)),
        ),
    }


def test_from_dict_shell_only():
    polygon = geometry.Polygon._from_dict(
        {
            "type": "Polygon",
            "bbox": (0.0, 0.0, 1.0, 1.0),
            "coordinates": (((0.0, 0.0), (1.0, 1.0), (1.0, 0.0), (0.0, 0.0)),),
        },
    )

    assert polygon.__geo_interface__, {
        "type": "Polygon",
        "bbox": (0.0, 0.0, 1.0, 1.0),
        "coordinates": (((0.0, 0.0), (1.0, 1.0), (1.0, 0.0), (0.0, 0.0)),),
    }


def test_from_dict_with_holes():
    polygon = geometry.Polygon._from_dict(
        {
            "type": "Polygon",
            "bbox": (0.0, 0.0, 2.0, 2.0),
            "coordinates": (
                ((0.0, 0.0), (0.0, 2.0), (2.0, 2.0), (2.0, 0.0), (0.0, 0.0)),
                ((1.0, 0.0), (0.5, 0.5), (1.0, 1.0), (1.5, 0.5), (1.0, 0.0)),
            ),
        },
    )

    assert polygon.__geo_interface__ == {
        "type": "Polygon",
        "bbox": (0.0, 0.0, 2.0, 2.0),
        "coordinates": (
            ((0.0, 0.0), (0.0, 2.0), (2.0, 2.0), (2.0, 0.0), (0.0, 0.0)),
            ((1.0, 0.0), (0.5, 0.5), (1.0, 1.0), (1.5, 0.5), (1.0, 0.0)),
        ),
    }


def test_from_compatible():
    not_a_geometry = mock.Mock(
        __geo_interface__={
            "type": "Polygon",
            "bbox": (0.0, 0.0, 2.0, 2.0),
            "coordinates": (
                ((0.0, 0.0), (0.0, 2.0), (2.0, 2.0), (2.0, 0.0), (0.0, 0.0)),
                ((1.0, 0.0), (0.5, 0.5), (1.0, 1.0), (1.5, 0.5), (1.0, 0.0)),
            ),
        },
    )

    polygon = geometry.Polygon._from_interface(not_a_geometry)

    assert polygon.__geo_interface__ == {
        "type": "Polygon",
        "bbox": (0.0, 0.0, 2.0, 2.0),
        "coordinates": (
            ((0.0, 0.0), (0.0, 2.0), (2.0, 2.0), (2.0, 0.0), (0.0, 0.0)),
            ((1.0, 0.0), (0.5, 0.5), (1.0, 1.0), (1.5, 0.5), (1.0, 0.0)),
        ),
    }


def test_exteriors():
    polygon = geometry.Polygon([(0, 0), (0, 2), (2, 2), (2, 0), (0, 0)])

    assert polygon.exterior.coords == ((0, 0), (0, 2), (2, 2), (2, 0), (0, 0))


def test_interiors():
    e = [(0, 0), (0, 2), (2, 2), (2, 0), (0, 0)]
    i = [(1, 0), (0.5, 0.5), (1, 1), (1.5, 0.5), (1, 0)]
    polygon = geometry.Polygon(e, [i])

    assert list(polygon.interiors)[0].coords == (
        (1, 0),
        (0.5, 0.5),
        (1, 1),
        (1.5, 0.5),
        (1, 0),
    )


def test_bounds():
    polygon = geometry.Polygon([(0, 0), (1, 1), (1, 0), (0, 0)])

    assert polygon.bounds == (0.0, 0.0, 1.0, 1.0)


def test_wkt_shell_only():
    polygon = geometry.Polygon([(0, 0), (1, 1), (1, 0), (0, 0)], [])

    assert polygon.wkt == "POLYGON ((0 0, 1 1, 1 0, 0 0))"


def test_wkt_with_holes():
    e = [(0, 0), (0, 2), (2, 2), (2, 0), (0, 0)]
    i = [(1, 0), (0.5, 0.5), (1, 1), (1.5, 0.5), (1, 0)]
    i2 = [(1, 0), (0.5, 0.5), (1, 1), (1.5, 0.5), (1, 0)]
    polygon = geometry.Polygon(e, [i, i2])

    assert polygon.wkt == (
        "POLYGON ((0 0, 0 2, 2 2, 2 0, 0 0),"
        "(1 0, 0.5 0.5, 1 1, 1.5 0.5, 1 0),"
        "(1 0, 0.5 0.5, 1 1, 1.5 0.5, 1 0))"
    )


def test_wkt_shell_only_3d():
    polygon = geometry.Polygon([(0, 0, 0), (1, 1, 0), (1, 0, 0), (0, 0, 0)])

    assert polygon.wkt == "POLYGON Z ((0 0 0, 1 1 0, 1 0 0, 0 0 0))"


def test_repr():
    e = [(0, 0), (0, 2), (2, 2), (2, 0), (0, 0)]
    i = [(1, 0), (0.5, 0.5), (1, 1), (1.5, 0.5), (1, 0)]
    polygon = geometry.Polygon(e, [i])

    assert repr(polygon) == (
        "Polygon(((0, 0), (0, 2), (2, 2), (2, 0), (0, 0)), "
        "(((1, 0), (0.5, 0.5), (1, 1), (1.5, 0.5), (1, 0)),))"
    )


def test_repr_shell_only():
    polygon = geometry.Polygon([(0, 0, 0), (1, 1, 0), (1, 0, 0), (0, 0, 0)])

    assert repr(polygon) == "Polygon(((0, 0, 0), (1, 1, 0), (1, 0, 0), (0, 0, 0)),)"


def test_repr_eval():
    e = [(0, 0), (0, 2), (2, 2), (2, 0), (0, 0)]
    i = [(1, 0), (0.5, 0.5), (1, 1), (1.5, 0.5), (1, 0)]
    polygon = geometry.Polygon(e, [i])

    assert (
        eval(repr(polygon), {}, {"Polygon": geometry.Polygon}).__geo_interface__
        == polygon.__geo_interface__
    )


def test_repr_eval_shell_only():
    polygon = geometry.Polygon([(0, 0, 0), (1, 1, 0), (1, 0, 0), (0, 0, 0)])

    assert (
        eval(repr(polygon), {}, {"Polygon": geometry.Polygon}).__geo_interface__
        == polygon.__geo_interface__
    )


def test_hasz():
    polygon = geometry.Polygon([(0, 0, 0), (1, 1, 0), (1, 0, 0), (0, 0, 0)])

    assert polygon.has_z


def test_convex_hull():
    polygon = geometry.Polygon([(0, 0), (1, 1), (2, 2)])

    assert polygon.convex_hull == geometry.LineString([(0, 0), (2, 2)])


def test_convex_hull_3d():
    polygon = geometry.Polygon([(0, 0, 0), (1, 1, 1), (2, 2, 2)])

    assert polygon.convex_hull == geometry.LineString([(0, 0), (2, 2)])


def test_convex_hull_3d_collapsed_to_point():
    polygon = geometry.Polygon([(0, 0, 0), (0, 0, 1), (0, 0, 2)])

    assert polygon.convex_hull == geometry.Point(0, 0)


def test_convex_hull_linear_ring():
    polygon = geometry.Polygon([(0, 0), (1, 0), (2, 2)])

    assert polygon.convex_hull == geometry.Polygon([(0, 0), (1, 0), (2, 2), (0, 0)])


def test_from_linear_rings():
    ring1 = geometry.LinearRing([(0, 0), (1, 1), (2, 2)])
    ring2 = geometry.LinearRing(((0, 0), (1, 1), (1, 0), (0, 0)))

    assert geometry.Polygon.from_linear_rings(ring1, ring2) == geometry.Polygon(
        ((0, 0), (1, 1), (2, 2), (0, 0)),
        (((0, 0), (1, 1), (1, 0), (0, 0)),),
    )


def test_from_coordinates():
    polygon = geometry.Polygon([(0, 0, 0), (1, 1, 0), (1, 0, 0), (0, 0, 0)])

    assert geometry.Polygon.from_coordinates(polygon.coords) == polygon


def test_from_coordinates_with_holes():
    e = [(0, 0), (0, 2), (2, 2), (2, 0), (0, 0)]
    i = [(1, 0), (0.5, 0.5), (1, 1), (1.5, 0.5), (1, 0)]
    polygon = geometry.Polygon(e, [i])

    assert geometry.Polygon.from_coordinates(polygon.coords) == polygon


def test_maybe_valid():
    e = [(0, 0), (0, 2), (2, 2), (2, 0), (0, 0)]
    i = [(0.5, 0.5), (1, 1), (0.5, 1)]
    polygon = geometry.Polygon(e, [i])

    assert polygon.maybe_valid


def test_is_invalid_hole_too_big_y():
    e = [(0, 0), (0, 2), (2, 2), (2, 0), (0, 0)]
    i = [(0.5, 0.5), (1, 3), (0.5, 1)]
    polygon = geometry.Polygon(e, [i])

    assert not polygon.maybe_valid


def test_is_invalid_hole_too_big_x():
    e = [(0, 0), (0, 2), (2, 2), (2, 0), (0, 0)]
    i = [(0.5, 0.5), (3, 1), (0.5, 1)]
    polygon = geometry.Polygon(e, [i])

    assert not polygon.maybe_valid


def test_is_invalid_hole_too_big_min():
    e = [(0, 0), (0, 2), (2, 2), (2, 0), (0, 0)]
    i = [(-0.5, -0.5), (3, 1), (0.5, 1)]
    polygon = geometry.Polygon(e, [i])

    assert not polygon.maybe_valid


def test_is_invalid_exterior():
    e = [(0, 0), (1, 0), (1, 1), (0, -1), (0, 0)]
    polygon = geometry.Polygon(e)

    assert not polygon.maybe_valid


def test_is_invalid_interior():
    e = [(-2, -2), (-2, 2), (2, 2), (2, -2), (-2, -2)]
    i = [(0, 0), (1, 0), (1, 1), (0, -1), (0, 0)]
    polygon = geometry.Polygon(e, [i])

    assert not polygon.maybe_valid


def test_empty():
    polygon = geometry.Polygon([])

    assert polygon.is_empty


def test_empty_wkt():
    polygon = geometry.Polygon([])

    assert polygon.wkt == "POLYGON EMPTY"


def test_repr_empty():
    polygon = geometry.Polygon([])

    assert repr(polygon) == "Polygon((),)"
