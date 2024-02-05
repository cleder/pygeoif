"""Test MultiPoint."""

import pytest

from pygeoif import geometry


def test_geoms() -> None:
    multipoint = geometry.MultiPoint([(0, 0), (1, 1), (1, 2), (2, 2)])

    for point in multipoint.geoms:
        assert type(point) is geometry.Point


def test_len() -> None:
    multipoint = geometry.MultiPoint(
        [(0, 0), (1, 1), (1, 2), (2, 2), (0, 0), (1, 1), (1, 2), (2, 2)],
    )

    assert len(multipoint) == 8


def test_bounds() -> None:
    multipoint = geometry.MultiPoint(
        [(0, 1), (1, 1), (3, 2)],
    )

    assert multipoint.bounds == (0, 1, 3, 2)


def test_has_z_empty() -> None:
    multipoint = geometry.MultiPoint(())

    assert multipoint.has_z is None


def test_geo_interface() -> None:
    multipoint = geometry.MultiPoint([(0, 0), (1, 1), (1, 2), (2, 2)])

    assert multipoint.__geo_interface__ == {
        "type": "MultiPoint",
        "bbox": (0, 0, 2, 2),
        "coordinates": ((0, 0), (1, 1), (1, 2), (2, 2)),
    }


def test_from_dict() -> None:
    multipoint = geometry.MultiPoint._from_dict(
        {
            "type": "MultiPoint",
            "bbox": (0.0, 0.0, 1.0, 1.0),  # pragma: no mutate
            "coordinates": ((0.0, 0.0), (1.0, 1.0)),
        },
    )

    assert multipoint.__geo_interface__ == {
        "type": "MultiPoint",
        "bbox": (0.0, 0.0, 1.0, 1.0),  # pragma: no mutate
        "coordinates": ((0.0, 0.0), (1.0, 1.0)),
    }


def test_coords() -> None:
    multipoint = geometry.MultiPoint([(0, 0), (1, 1), (1, 2), (2, 2)])

    with pytest.raises(
        NotImplementedError,
        match="^Multi-part geometries do not provide a coordinate sequence$",
    ):
        assert multipoint.coords


def test_unique() -> None:
    multipoint = geometry.MultiPoint(
        [(0, 0), (1, 1), (1, 2), (2.0, 2.0), (0, 0), (1.0, 1.0), (1, 2), (2, 2)],
        unique=True,
    )

    assert len(multipoint) == 4


def test_wkt() -> None:
    multipoint = geometry.MultiPoint([(0, 0), (1, 1), (1, 2), (2, 2)])

    assert multipoint.wkt == "MULTIPOINT (0 0, 1 1, 1 2, 2 2)"


def test_repr() -> None:
    multipoint = geometry.MultiPoint([(0, 0), (1, 1), (1, 2), (2, 2)])

    assert repr(multipoint) == "MultiPoint(((0, 0), (1, 1), (1, 2), (2, 2)))"


def test_repr_eval() -> None:
    multipoint = geometry.MultiPoint([(0, 0), (1, 1), (1, 2), (2, 2)])

    assert (
        eval(
            repr(multipoint),
            {},
            {"MultiPoint": geometry.MultiPoint},
        ).__geo_interface__
        == multipoint.__geo_interface__
    )


def test_convex_hull() -> None:
    multipoint = geometry.MultiPoint([(0, 0), (1, 1), (2, 2)])

    assert multipoint.convex_hull == geometry.LineString([(0, 0), (2, 2)])


def test_convex_hull_3d() -> None:
    multipoint = geometry.MultiPoint([(0, 0, 0), (1, 1, 1), (2, 2, 2)])

    assert multipoint.convex_hull == geometry.LineString([(0, 0), (2, 2)])


def test_convex_hull_3d_collapsed_to_point() -> None:
    multipoint = geometry.MultiPoint([(0, 0, 0), (0, 0, 1), (0, 0, 2)])

    assert multipoint.convex_hull == geometry.Point(0, 0)


def test_convex_hull_linear_ring() -> None:
    multipoint = geometry.MultiPoint([(0, 0), (1, 0), (2, 2)])

    assert multipoint.convex_hull == geometry.Polygon([(0, 0), (1, 0), (2, 2), (0, 0)])


def test_from_points() -> None:
    multipoint = geometry.MultiPoint([(0, 0), (1, 0), (2, 2)])
    p1 = geometry.Point(0, 0)
    p2 = geometry.Point(1, 0)
    p3 = geometry.Point(2.0, 2.0)

    assert geometry.MultiPoint.from_points(p1, p2, p3) == multipoint


def test_from_points_unique() -> None:
    multipoint = geometry.MultiPoint([(0, 0), (1, 0), (2, 2)], unique=True)
    p1 = geometry.Point(0, 0)
    p2 = geometry.Point(1, 0)
    p3 = geometry.Point(2.0, 2.0)

    assert (
        geometry.MultiPoint.from_points(p1, p2, p3, p1, p2, p3, p1, unique=True)
        == multipoint
    )


def test_empty() -> None:
    multipoint = geometry.MultiPoint([(1, None)])

    assert multipoint.is_empty


def test_repr_empty() -> None:
    multipoint = geometry.MultiPoint([(None, None)])

    assert repr(multipoint) == "MultiPoint(((),))"


def test_empty_bounds() -> None:
    multipoint = geometry.MultiPoint([(None, None)])

    assert multipoint.bounds == ()
