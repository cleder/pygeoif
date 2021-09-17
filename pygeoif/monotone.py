"""
Andrew's monotone chain convex hull algorithm.

https://en.wikibooks.org/wiki/Algorithm_Implementation/Geometry/Convex_hull/Monotone_chain#Python

Construct the convex hull of a set of 2-dimensional points.
"""
from typing import Iterable
from typing import List
from typing import Union

from pygeoif.types import LineType
from pygeoif.types import Point2D


def _cross(o: Point2D, a: Point2D, b: Point2D) -> float:
    """2D cross product of OA and OB vectors, i.e. z-component of their 3D cross product.

    Returns a positive value, if OAB makes a counter-clockwise turn,
    negative for clockwise turn, and zero if the points are collinear.
    """
    return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])


def _build_hull(points: Iterable[Point2D]) -> List[Point2D]:
    hull: List[Point2D] = []
    for p in points:
        while len(hull) >= 2 and _cross(hull[-2], hull[-1], p) <= 0:
            hull.pop()
        hull.append(p)
    return hull


def convex_hull(points: Iterable[Point2D]) -> Union[Point2D, LineType]:
    """
    Compute the convex hull of a set of 2D points.

    Input: an iterable sequence of (x, y) pairs representing the points.
    Output: a list of vertices of the convex hull in counter-clockwise order,
    starting from the vertex with the lexicographically smallest coordinates.

    Implements Andrew's monotone chain algorithm. O(n log n) complexity.
    """
    # Sort the points lexicographically (tuples are compared lexicographically).
    # Remove duplicates to detect the case we have just one unique point.
    points = sorted(set(points))

    # Boring case: no points, a single point or a line between two points,
    # possibly repeated multiple times.
    if len(points) <= 2:
        return points

    lower = _build_hull(points)
    upper = _build_hull(reversed(points))

    if len(lower) == len(upper) == 2 and set(lower) == set(upper):
        # all points are in a straight line
        return lower
    # Concatenation of the lower and upper hulls gives the convex hull.
    # Last point of lower list is omitted
    # because it is repeated at the beginning of the upper list.
    return lower[:-1] + upper


__all__ = [
    "convex_hull",
]
