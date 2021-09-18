"""Test geometric functions."""
import math
import random

import pytest

from pygeoif.functions import convex_hull
from pygeoif.functions import signed_area


def test_signed_area():
    a0 = [(0, 0), (0, 2), (2, 2), (2, 0), (0, 0)]
    a1 = [(0, 0, 1), (0, 2, 2), (2, 2, 3), (2, 0, 4), (0, 0, 1)]
    assert signed_area(a0) == signed_area(a1) == -4


def test_signed_area_0_3d():
    assert signed_area(((0.0, 0.0, 0.0), (0.0, 0.0, 0.0))) == 0.0


def test_signed_area_0_2d():
    assert signed_area(((0.0, 0.0), (0.0, 0.0), (0.0, 0.0))) == 0.0


def test_signed_area_unequal_len():  # sourcery skip: move-assign
    a2 = [(0, 0, 1, 3), (0, 2, 2)]

    with pytest.raises(
        UnboundLocalError,
        match="^local variable 'xs' referenced before assignment$",
    ):
        signed_area(a2)


def test_point():
    pts = [(0, 0)]

    hull = convex_hull(pts)

    assert hull == [(0, 0)]


def test_line():
    pts = [(0, 0), (1, 1)]

    hull = convex_hull(pts)

    assert hull == [(0, 0), (1, 1)]


def test_line2():
    pts = ((x, x) for x in range(5))

    hull = convex_hull(pts)

    assert hull == [(0, 0), (4, 4)]


def test_line3():
    pts = ((x, x) for x in range(3))

    hull = convex_hull(pts)

    assert hull == [(0, 0), (2, 2)]


def test_square():
    pts = []
    for x in range(100):
        for y in range(100):
            pts.append((x, y))

    hull = convex_hull(pts)

    assert hull == [(0, 0), (99, 0), (99, 99), (0, 99), (0, 0)]


def test_triangle():
    pts = []
    for x in range(100):
        for y in range(x + 1):
            pts.append((x, y))

    hull = convex_hull(pts)

    assert hull == [(0, 0), (99, 0), (99, 99), (0, 0)]


def test_trapezoid():
    pts = []
    for x in range(100):
        for y in range(-x - 1, x + 1):
            pts.append((x, y))

    hull = convex_hull(pts)

    assert hull == [(0, -1), (99, -100), (99, 99), (0, 0), (0, -1)]


def test_circles():
    for _ in range(10):
        x = random.randrange(20)
        y = random.randrange(20)
        r = random.randrange(1, 20)
        pts = []
        steps = random.randrange(4, 20)
        for step in range(1, steps):
            phi = 2 * math.pi * step / steps
            pts.append((r * math.cos(phi) + x, r * math.sin(phi) + y))

        hull = convex_hull(pts)

        assert set(hull) == set(pts)
        assert len(hull) == len(pts) + 1


def test_spiral():
    for _ in range(10):
        x = random.randrange(20)
        y = random.randrange(20)
        pts = []
        steps = random.randrange(4, 20)
        for step in range(1, steps):
            phi = math.pi * step / steps
            pts.append((step * math.cos(phi) + x, step * math.sin(phi) + y))

        hull = convex_hull(pts)

        assert set(hull) == set(pts)
        assert len(hull) == len(pts) + 1
