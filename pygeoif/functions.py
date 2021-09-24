# -*- coding: utf-8 -*-
#
#   Copyright (C) 2012 -2021  Christian Ledermann
#
#   This library is free software; you can redistribute it and/or
#   modify it under the terms of the GNU Lesser General Public
#   License as published by the Free Software Foundation; either
#   version 2.1 of the License, or (at your option) any later version.

#   This library is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#   Lesser General Public License for more details.

#   You should have received a copy of the GNU Lesser General Public License
#   along with this library; if not, write to the Free Software Foundation,
#   Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA
#
"""Functions for geometries."""
from itertools import groupby
from typing import Iterable
from typing import List
from typing import Tuple
from typing import cast

from pygeoif.types import LineType
from pygeoif.types import Point2D


def signed_area(coords: LineType) -> float:
    """Return the signed area enclosed by a ring.

    Linear time algorithm: http://www.cgafaq.info/wiki/Polygon_Area.
    A value >= 0 indicates a counter-clockwise oriented ring.
    """
    xs, ys = map(list, zip(*(coord[:2] for coord in coords)))
    xs.append(xs[1])  # pragma: no mutate
    ys.append(ys[1])  # pragma: no mutate
    return (
        sum(
            xs[i] * (ys[i + 1] - ys[i - 1])  # type: ignore [operator]
            for i in range(1, len(coords))
        )
        / 2.0
    )


def centroid(coords: LineType) -> Tuple[Point2D, float]:
    """Calculate the coordinates of the centroid and the area of a LineString."""
    ans: List[float] = [0, 0]

    n = len(coords)
    signed_area = 0.0

    # For all vertices
    for i, coord in enumerate(coords):

        next_coord = coords[(i + 1) % n]
        # Calculate area using shoelace formula
        area = (coord[0] * next_coord[1]) - (next_coord[0] * coord[1])
        signed_area += area

        # Calculate coordinates of centroid of polygon
        ans[0] += (coord[0] + next_coord[0]) * area
        ans[1] += (coord[1] + next_coord[1]) * area

    ans[0] = (ans[0]) / (3 * signed_area)
    ans[1] = (ans[1]) / (3 * signed_area)

    return cast(Point2D, tuple(ans)), signed_area / 2.0


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


def convex_hull(points: Iterable[Point2D]) -> LineType:
    """
    Compute the convex hull of a set of 2D points.

    Input: an iterable sequence of (x, y) pairs representing the points.
    Output: a list of vertices of the convex hull in counter-clockwise order,
    starting from the vertex with the lexicographically smallest coordinates.

    Andrew's monotone chain convex hull algorithm constructs the convex hull
    of a set of 2-dimensional points in O(n log n) time.

    It does so by first sorting the points lexicographically
    (first by x-coordinate, and in case of a tie, by y-coordinate),
    and then constructing upper and lower hulls of the points.

    An upper hull is the part of the convex hull, which is visible from the above.
    It runs from its rightmost point to the leftmost point in counterclockwise order.
    Lower hull is the remaining part of the convex hull.
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


def dedupe(coords: LineType) -> LineType:
    """Remove duplicate Points from a LineString."""
    return tuple(coord for coord, _count in groupby(coords))


__all__ = ["centroid", "convex_hull", "dedupe", "signed_area"]
