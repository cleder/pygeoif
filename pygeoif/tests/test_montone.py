"""Test monotone."""
import math
import random

from pygeoif.monotone import convex_hull


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
