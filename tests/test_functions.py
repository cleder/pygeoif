"""Test geometric functions."""

import itertools
import math
import random
from typing import Tuple

import pytest

from pygeoif.functions import centroid
from pygeoif.functions import compare_coordinates
from pygeoif.functions import compare_geo_interface
from pygeoif.functions import convex_hull
from pygeoif.functions import dedupe
from pygeoif.functions import signed_area


def circle_ish(x, y, r, steps):
    pts = []
    steps = max(steps, 3)
    for step in range(steps):
        phi = 2 * math.pi * step / steps
        pts.append((r * math.cos(phi) + x, r * math.sin(phi) + y))
    pts.append((x + r, y))
    return pts


def star_ish(x, y, r, steps):
    pts = []
    steps = max(steps, 3)
    for step in range(steps):
        phi = 2 * math.pi * step / steps
        pts.append(
            (random.randrange(1, r + 1) * math.cos(phi) + x, r * math.sin(phi) + y),
        )
    pts.append((x + r, y))
    return pts


def spiral_ish(x, y, r, steps):
    pts = []
    for step in range(1, steps):
        phi = math.pi * step / steps
        pts.append((step * r * math.cos(phi) + x, step * r * math.sin(phi) + y))
    pts.append((x + r, y))
    return pts


def crescent_ish(x, y, r, steps):
    pts = []
    for step in range(1, steps):
        phi = math.pi * step / steps
        pts.append((step * r * 2 * math.cos(phi) + x, step * r * math.sin(phi) + y))
    for step in range(steps, 0, -1):
        phi = math.pi * step / steps
        pts.append((step * r * math.cos(phi) + x, step * r * math.sin(phi) + y))
    pts.append(pts[0])
    return pts


def test_signed_area() -> None:
    a0 = [(0, 0), (0, 2), (2, 2), (2, 0), (0, 0)]
    a1 = [(0, 0, 1), (0, 2, 2), (2, 2, 3), (2, 0, 4), (0, 0, 1)]
    assert signed_area(a0) == signed_area(a1) == -4
    assert centroid(a0)[1] == centroid(a1)[1] == -4


def test_signed_area2() -> None:
    a0 = [(0, 0), (0, 1), (1, 1), (0, 0)]
    assert centroid(a0)[1] == signed_area(a0)


def test_centroid_line() -> None:
    a0 = [(0, 0), (1, 1), (0, 0)]
    with pytest.raises(ZeroDivisionError):
        assert centroid(a0)


def test_signed_area_0_3d() -> None:
    assert signed_area(((0.0, 0.0, 0.0), (0.0, 0.0, 0.0))) == 0.0


def test_signed_area_0_2d() -> None:
    assert signed_area(((0.0, 0.0), (0.0, 0.0), (0.0, 0.0))) == 0.0


def test_signed_area_circle_ish() -> None:
    for i in range(100):
        x = random.randrange(20)
        y = random.randrange(20)
        r = random.randrange(1, 20 + i)
        pts = []
        steps = random.randrange(3, 30 + i)
        pts = circle_ish(x, y, r, steps)

        center1, area1 = centroid(pts)
        center2, area2 = centroid(list(reversed(pts)))

        # both area computations should be approximately equal
        assert math.isclose(area1, signed_area(pts))
        assert math.isclose(area2, signed_area(list(reversed(pts))))
        assert center1, area1 == (center2, area2)
        assert math.isclose(center1[0], x, abs_tol=0.000_000_1)
        assert math.isclose(center1[1], y, abs_tol=0.000_000_1)
        # we are computing an approximation of math.pi
        if steps > 12:
            assert 3.0 * r**2 < area1 < 3.2 * r**2
        if steps > 30:
            assert 3.1 * r**2 < area1 < 3.2 * r**2


def test_signed_area_crescent_ish() -> None:
    for i in range(100):
        x = random.randrange(20) - i
        y = random.randrange(20 + i)
        r = random.randrange(1, 20)
        pts = []
        steps = random.randrange(4, 20)
        pts = crescent_ish(x, y, r, steps)

        center1, area1 = centroid(pts)
        center2, area2 = centroid(list(reversed(pts)))

        assert math.isclose(area1, signed_area(pts))
        assert math.isclose(area2, signed_area(list(reversed(pts))))
        assert center1, area1 == (center2, area2)


def test_empty_hull() -> None:
    assert convex_hull([]) == []


def test_point() -> None:
    pts = [(0, 0)]

    hull = convex_hull(pts)

    assert hull == [(0, 0)]


def test_line() -> None:
    pts = [(0, 0), (1, 1)]

    hull = convex_hull(pts)

    assert hull == [(0, 0), (1, 1)]


def test_line_minimal() -> None:
    pts = [(0, 0), (1, 1), (1, 0)]

    hull = convex_hull(pts)

    assert hull == [(0, 0), (1, 0), (1, 1), (0, 0)]


def test_line2() -> None:
    pts = ((x, x) for x in range(5))

    hull = convex_hull(pts)

    assert hull == [(0, 0), (4, 4)]


def test_line3() -> None:
    pts = ((x, x) for x in range(3))

    hull = convex_hull(pts)

    assert hull == [(0, 0), (2, 2)]


def test_square() -> None:
    pts = list(itertools.product(range(100), range(100)))
    hull = convex_hull(pts)
    assert hull == [(0, 0), (99, 0), (99, 99), (0, 99), (0, 0)]


def test_triangle() -> None:
    pts = []
    for x in range(100):
        pts.extend((x, y) for y in range(x + 1))
    hull = convex_hull(pts)
    assert hull == [(0, 0), (99, 0), (99, 99), (0, 0)]


def test_trapezoid() -> None:
    pts = []
    for x in range(100):
        pts.extend((x, y) for y in range(-x - 1, x + 1))
    hull = convex_hull(pts)
    assert hull == [(0, -1), (99, -100), (99, 99), (0, 0), (0, -1)]


def test_circles() -> None:
    for _ in range(10):
        x = random.randrange(20)
        y = random.randrange(20)
        r = random.randrange(1, 20)
        steps = random.randrange(4, 20)
        pts = circle_ish(x, y, r, steps)

        hull = convex_hull(pts)

        assert set(hull) == set(pts)
        assert len(hull) == len(pts)


def test_spiral() -> None:
    for _ in range(10):
        x = random.randrange(20)
        y = random.randrange(20)
        pts = []
        steps = random.randrange(4, 20)
        spiral_ish(x, y, 1, steps)

        hull = convex_hull(pts)

        assert set(hull) == set(pts)
        assert len(hull) == len(pts)


def test_crescent() -> None:
    for _ in range(10):
        x = random.randrange(20)
        y = random.randrange(20)
        pts = []
        steps = random.randrange(4, 20)
        crescent_ish(x, y, 1, steps)

        hull = convex_hull(pts)
        assert len(hull) == len(pts) / 2


def test_star() -> None:
    for _ in range(10):
        x = random.randrange(20)
        y = random.randrange(20)
        pts = []
        steps = random.randrange(4, 20)
        star_ish(x, y, 1, steps)

        hull = convex_hull(pts)

        assert set(hull).issubset(set(pts))
        assert len(hull) <= len(pts)


def test_random() -> None:
    """The convex hull of an exiting hull must be the same as the hull itself."""
    for i in range(100):
        pts = (
            (random.randrange(-x, x + 1), random.randrange(-x, x + 1))
            for x in range(i + 1)
        )
        hull = convex_hull(pts)

        assert convex_hull(hull) == hull
        if len(hull) > 3:
            _, area = centroid(tuple(hull))
            assert math.isclose(area, signed_area(hull))


def test_dedupe_point() -> None:
    assert dedupe(((1, 2, 3),) * 10) == ((1, 2, 3),)


def test_dedupe_line() -> None:
    assert dedupe(((1, 2, 3), (4, 5, 6)) * 3) == (
        (1, 2, 3),
        (4, 5, 6),
        (1, 2, 3),
        (4, 5, 6),
        (1, 2, 3),
        (4, 5, 6),
    )


def test_dedupe_line2() -> None:
    assert dedupe(((1, 2, 3),) * 2 + ((4, 5, 6),) * 3) == ((1, 2, 3), (4, 5, 6))


@pytest.mark.parametrize(
    ("numbers", "expected"),
    [
        ((0, 0), True),
        ((0, 1), False),
        ((1, 0), False),
        ((1, 1), True),
        ((0.3, 0.2 + 0.1), True),
        ((1, "1"), False),
        (("10", 10), False),
        ((None, 1), False),
        ((1, None), False),
        ((None, None), False),
        ((1, 1.0), True),
        ((1.0, 1), True),
        ((math.inf, math.inf), True),
        ((-math.inf, -math.inf), True),
        ((math.inf, -math.inf), False),
        ((math.nan, math.nan), False),
    ],
)
def test_compare_numbers(numbers: Tuple[float, float], expected: bool) -> None:
    """Compare numbers for equality."""
    assert compare_coordinates(*numbers) is expected


@pytest.mark.parametrize(
    ("points", "expected"),
    [
        (((1, 2), [1, 2]), True),
        (((1, 2), [1, 3]), False),
        (((1, 2), [2, 2]), False),
        (((1, 2, 0), (1, 2)), False),
        (((1, 2), (1, 2, 0)), False),
        (((1, 2, 0), [1, 2, 0]), True),
        (((1, 2, 0), [1, 2, 1]), False),
        (((1, 2, 0), [1, 3, 0]), False),
        (((1, 2, 0), [2, 2, 0]), False),
        (((0.3, 0.3), (0.1 + 0.2, 0.1 + 0.2)), True),
        (((0.3, 0.3), ("0.3", "0.3")), False),
    ],
)
def test_compare_points(points, expected: bool) -> None:
    """Compare a single set of coordinates."""
    assert compare_coordinates(*points) is expected


@pytest.mark.parametrize(
    ("lines", "expected"),
    [
        ((((1, 2), (3, 4)), ((1, 2), (3, 4))), True),
        ((((1, 2), (3, 4)), [[1, 2], [3, 4]]), True),
        ((((1, 2), (3, 4)), ((1, 2), (3, 5))), False),
        ((((1, 2), (3, (3, 5))), ((1, 2), (3, (3, 5)))), True),
        ((((1, 2), (3, 4)), ((1, 2), (3, 4), (3, 4))), False),
    ],
)
def test_compare_lines(lines, expected: bool) -> None:
    """Compare a sequence of coordinates."""
    assert compare_coordinates(*lines) is expected


@pytest.mark.parametrize(
    ("polygons", "expected"),
    [
        (
            (
                (((1, 2), (3, 4)), ((5, 6), (7, 8))),
                (((1, 2), (3, 4)), ((5, 6), (7, 8))),
            ),
            True,
        ),
        (
            (
                (((1, 2), (3, 4)), ((5, 6), (7, 8))),
                (((1, 2), (3, 4)), ((5, 6), (7, 8)), ((5, 6), (7, 8))),
            ),
            False,
        ),
        (
            (
                (((1, 2), (3, 4)), ((5, 6), (7, 8))),
                (((1, 2), (3, 4)), (((5, 6), (7, 8)), ((5, 6), (7, 8)))),
            ),
            False,
        ),
        (
            (
                [[[1, 2], [3, 4]], ([[5, 6], (7, 8)], ([5, 6], [7, 8]))],
                (((1, 2), (3, 4)), (((5, 6), (7, 8)), ((5, 6), (7, 8)))),
            ),
            True,
        ),
    ],
)
def test_compare_polygons(polygons, expected: bool) -> None:
    """Compare nested sequences of coordinates."""
    assert compare_coordinates(*polygons) is expected


def test_compare_eq_geo_interface() -> None:
    geo_if = {
        "geometries": (
            {
                "geometries": (
                    {
                        "geometries": (
                            {
                                "bbox": (0, 0, 0, 0),
                                "coordinates": (0, 0),
                                "type": "Point",
                            },
                            {
                                "bbox": (0, 0, 2, 2),
                                "coordinates": ((0, 0), (1, 1), (1, 2), (2, 2)),
                                "type": "MultiPoint",
                            },
                        ),
                        "type": "GeometryCollection",
                    },
                    {
                        "bbox": (0, 0, 3, 1),
                        "coordinates": ((0, 0), (3, 1)),
                        "type": "LineString",
                    },
                ),
                "type": "GeometryCollection",
            },
            {"coordinates": (((0, 0), (1, 1), (1, 0), (0, 0)),), "type": "Polygon"},
            {
                "bbox": (0, 0, 2, 2),
                "coordinates": (
                    ((0, 0), (0, 2), (2, 2), (2, 0), (0, 0)),
                    ((1, 0), (0.5, 0.5), (1, 1), (1.5, 0.5), (1, 0)),
                ),
                "type": "Polygon",
            },
            {"coordinates": (0, 0), "type": "Point"},
            {"bbox": (-1, -1, -1, -1), "coordinates": (-1, -1), "type": "Point"},
            {"coordinates": ((0, 0), (1, 1), (1, 0), (0, 0)), "type": "LinearRing"},
            {
                "bbox": (0, 0, 1, 1),
                "coordinates": ((0, 0), (1, 1)),
                "type": "LineString",
            },
        ),
        "type": "GeometryCollection",
    }

    assert compare_geo_interface(geo_if, geo_if) is True


def test_compare_neq_geo_interface() -> None:
    geo_if1 = {
        "type": "Point",
        "bbox": (0, 1, 0, 1),
        "coordinates": (0.0, 1.0, 2.0),
    }
    geo_if2 = {
        "coordinates": (0.0, 1.0, 3.0),
    }

    assert compare_geo_interface(geo_if1, geo_if2) is False


def test_compare_neq_empty_geo_interface() -> None:
    geo_if = {
        "type": "Point",
        "bbox": (0, 1, 0, 1),
        "coordinates": (0.0, 1.0, 2.0),
    }

    assert compare_geo_interface(geo_if, {}) is False
