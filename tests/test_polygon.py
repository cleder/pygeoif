"""Test Polygon."""

from unittest import mock

from pygeoif import geometry


def test_coords() -> None:
    polygon = geometry.Polygon([(0, 0), (1, 1), (1, 0), (0, 0)])

    assert polygon.coords == (((0.0, 0.0), (1.0, 1.0), (1.0, 0.0), (0.0, 0.0)),)


def test_coords_with_holes() -> None:
    e = [(0, 0), (0, 2), (2, 2), (2, 0), (0, 0)]
    i = [(1, 0), (0.5, 0.5), (1, 1), (1.5, 0.5), (1, 0)]
    polygon = geometry.Polygon(e, [i])
    assert polygon.coords == (
        ((0.0, 0.0), (0.0, 2.0), (2.0, 2.0), (2.0, 0.0), (0.0, 0.0)),
        (((1.0, 0.0), (0.5, 0.5), (1.0, 1.0), (1.5, 0.5), (1.0, 0.0)),),
    )


def test_geo_interface_shell_only() -> None:
    polygon = geometry.Polygon([(0, 0), (1, 1), (1, 0), (0, 0)])

    assert polygon.__geo_interface__, {
        "type": "Polygon",
        "bbox": (0.0, 0.0, 1.0, 1.0),
        "coordinates": (((0.0, 0.0), (1.0, 1.0), (1.0, 0.0), (0.0, 0.0)),),
    }


def test_geo_interface_with_holes() -> None:
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


def test_from_dict_shell_only() -> None:
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


def test_from_dict_with_holes() -> None:
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


def test_from_compatible() -> None:
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


def test_exteriors() -> None:
    polygon = geometry.Polygon([(0, 0), (0, 2), (2, 2), (2, 0), (0, 0)])

    assert polygon.exterior.coords == ((0, 0), (0, 2), (2, 2), (2, 0), (0, 0))


def test_interiors() -> None:
    e = [(0, 0), (0, 2), (2, 2), (2, 0), (0, 0)]
    i = [(1, 0), (0.5, 0.5), (1, 1), (1.5, 0.5), (1, 0)]
    polygon = geometry.Polygon(e, [i])

    assert next(iter(polygon.interiors)).coords == (
        (1, 0),
        (0.5, 0.5),
        (1, 1),
        (1.5, 0.5),
        (1, 0),
    )


def test_bounds() -> None:
    polygon = geometry.Polygon([(0, 0), (1, 1), (1, 0), (0, 0)])

    assert polygon.bounds == (0.0, 0.0, 1.0, 1.0)


def test_wkt_shell_only() -> None:
    polygon = geometry.Polygon([(0, 0), (1, 1), (1, 0), (0, 0)], [])

    assert polygon.wkt == "POLYGON ((0 0, 1 1, 1 0, 0 0))"


def test_wkt_with_holes() -> None:
    e = [(0, 0), (0, 2), (2, 2), (2, 0), (0, 0)]
    i = [(1, 0), (0.5, 0.5), (1, 1), (1.5, 0.5), (1, 0)]
    i2 = [(1, 0), (0.5, 0.5), (1, 1), (1.5, 0.5), (1, 0)]
    polygon = geometry.Polygon(e, [i, i2])

    assert polygon.wkt == (
        "POLYGON ((0 0, 0 2, 2 2, 2 0, 0 0),"
        "(1 0, 0.5 0.5, 1 1, 1.5 0.5, 1 0),"
        "(1 0, 0.5 0.5, 1 1, 1.5 0.5, 1 0))"
    )


def test_wkt_shell_only_3d() -> None:
    polygon = geometry.Polygon([(0, 0, 0), (1, 1, 0), (1, 0, 0), (0, 0, 0)])

    assert polygon.wkt == "POLYGON Z ((0 0 0, 1 1 0, 1 0 0, 0 0 0))"


def test_repr() -> None:
    e = [(0, 0), (0, 2), (2, 2), (2, 0), (0, 0)]
    i = [(1, 0), (0.5, 0.5), (1, 1), (1.5, 0.5), (1, 0)]
    polygon = geometry.Polygon(e, [i])

    assert repr(polygon) == (
        "Polygon(((0, 0), (0, 2), (2, 2), (2, 0), (0, 0)), "
        "(((1, 0), (0.5, 0.5), (1, 1), (1.5, 0.5), (1, 0)),))"
    )


def test_repr_shell_only() -> None:
    polygon = geometry.Polygon([(0, 0, 0), (1, 1, 0), (1, 0, 0), (0, 0, 0)])

    assert repr(polygon) == "Polygon(((0, 0, 0), (1, 1, 0), (1, 0, 0), (0, 0, 0)),)"


def test_repr_eval() -> None:
    e = [(0, 0), (0, 2), (2, 2), (2, 0), (0, 0)]
    i = [(1, 0), (0.5, 0.5), (1, 1), (1.5, 0.5), (1, 0)]
    polygon = geometry.Polygon(e, [i])

    assert (
        eval(repr(polygon), {}, {"Polygon": geometry.Polygon}).__geo_interface__
        == polygon.__geo_interface__
    )


def test_repr_eval_shell_only() -> None:
    polygon = geometry.Polygon([(0, 0, 0), (1, 1, 0), (1, 0, 0), (0, 0, 0)])

    assert (
        eval(repr(polygon), {}, {"Polygon": geometry.Polygon}).__geo_interface__
        == polygon.__geo_interface__
    )


def test_hasz() -> None:
    polygon = geometry.Polygon([(0, 0, 0), (1, 1, 0), (1, 0, 0), (0, 0, 0)])

    assert polygon.has_z


def test_convex_hull() -> None:
    polygon = geometry.Polygon([(0, 0), (1, 1), (2, 2)])

    assert polygon.convex_hull == geometry.LineString([(0, 0), (2, 2)])


def test_convex_hull_3d() -> None:
    polygon = geometry.Polygon([(0, 0, 0), (1, 1, 1), (2, 2, 2)])

    assert polygon.convex_hull == geometry.LineString([(0, 0), (2, 2)])


def test_convex_hull_3d_collapsed_to_point() -> None:
    polygon = geometry.Polygon([(0, 0, 0), (0, 0, 1), (0, 0, 2)])

    assert polygon.convex_hull == geometry.Point(0, 0)


def test_convex_hull_linear_ring() -> None:
    polygon = geometry.Polygon([(0, 0), (1, 0), (2, 2)])

    assert polygon.convex_hull == geometry.Polygon([(0, 0), (1, 0), (2, 2), (0, 0)])


def test_from_linear_rings() -> None:
    ring1 = geometry.LinearRing([(0, 0), (1, 1), (2, 2)])
    ring2 = geometry.LinearRing(((0, 0), (1, 1), (1, 0), (0, 0)))

    assert geometry.Polygon.from_linear_rings(ring1, ring2) == geometry.Polygon(
        ((0, 0), (1, 1), (2, 2), (0, 0)),
        (((0, 0), (1, 1), (1, 0), (0, 0)),),
    )


def test_from_coordinates() -> None:
    polygon = geometry.Polygon([(0, 0, 0), (1, 1, 0), (1, 0, 0), (0, 0, 0)])

    assert geometry.Polygon.from_coordinates(polygon.coords) == polygon


def test_from_coordinates_with_holes() -> None:
    e = [(0, 0), (0, 2), (2, 2), (2, 0), (0, 0)]
    i = [(1, 0), (0.5, 0.5), (1, 1), (1.5, 0.5), (1, 0)]
    polygon = geometry.Polygon(e, [i])

    assert geometry.Polygon.from_coordinates(polygon.coords) == polygon


def test_empty() -> None:
    polygon = geometry.Polygon([])

    assert polygon.is_empty


def test_empty_wkt() -> None:
    polygon = geometry.Polygon([])

    assert polygon.wkt == "POLYGON EMPTY"


def test_repr_empty() -> None:
    polygon = geometry.Polygon([])

    assert repr(polygon) == "Polygon((),)"


def test_empty_bounds() -> None:
    polygon = geometry.Polygon([])

    assert polygon.bounds == ()
