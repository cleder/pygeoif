#
#   Copyright (C) 2012 - 2024 Christian Ledermann
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

import math
from collections.abc import Iterable
from itertools import groupby
from itertools import zip_longest
from typing import cast

from pygeoif.types import CoordinatesType
from pygeoif.types import GeoCollectionInterface
from pygeoif.types import GeoInterface
from pygeoif.types import LineType
from pygeoif.types import MultiCoordinatesType
from pygeoif.types import Point2D
from pygeoif.types import PointType


def _relative_coordinates(
    coords: LineType,
) -> tuple[list[float], list[float], Point2D]:
    """
    Return the x and y coordinates as offsets from the first vertex.

    Shoelace sums are translation invariant in exact arithmetic but not in
    floating point: the individual terms grow with the square of the coordinate
    magnitude while their sum only grows with the area, so for a ring that sits
    far from the origin the significant digits are cancelled away. Accumulating
    relative to a vertex of the ring keeps the terms the size of the ring
    itself. The origin is returned so a result can be shifted back.
    """
    origin_x, origin_y = coords[0][0], coords[0][1]
    return (
        [coord[0] - origin_x for coord in coords],
        [coord[1] - origin_y for coord in coords],
        (origin_x, origin_y),
    )


def signed_area(coords: LineType) -> float:
    """
    Return the signed area enclosed by a ring.

    Linear time algorithm: http://www.cgafaq.info/wiki/Polygon_Area.
    A value >= 0 indicates a counter-clockwise oriented ring.
    """
    if len(coords) < 3:  # noqa: PLR2004
        return 0.0
    xs, ys, _ = _relative_coordinates(coords)
    xs.append(xs[1])  # pragma: no mutate
    ys.append(ys[1])  # pragma: no mutate
    return sum(xs[i] * (ys[i + 1] - ys[i - 1]) for i in range(1, len(coords))) / 2.0


def centroid(coords: LineType) -> tuple[Point2D, float]:
    """Calculate the coordinates of the centroid and the area of a LineString."""
    if not coords:
        return ((math.nan, math.nan), 0.0)

    xs, ys, (origin_x, origin_y) = _relative_coordinates(coords)
    ans: list[float] = [0, 0]
    n = len(coords)
    signed_area = 0.0

    # For all vertices
    for i in range(n):
        j = (i + 1) % n
        # Calculate area using shoelace formula
        area = (xs[i] * ys[j]) - (xs[j] * ys[i])
        signed_area += area

        # Calculate coordinates of centroid of polygon
        ans[0] += (xs[i] + xs[j]) * area
        ans[1] += (ys[i] + ys[j]) * area

    if signed_area == 0 or math.isnan(signed_area):
        return ((math.nan, math.nan), signed_area)

    # Shift the result back out of the local coordinate system.
    ans[0] = ans[0] / (3 * signed_area) + origin_x
    ans[1] = ans[1] / (3 * signed_area) + origin_y

    return cast("Point2D", tuple(ans)), signed_area / 2.0


def dedupe(coords: LineType) -> LineType:
    """Remove duplicate Points from a LineString."""
    return cast("LineType", tuple(coord for coord, _count in groupby(coords)))


def _orientation(p: Point2D, q: Point2D, r: Point2D) -> float:
    """
    Calculate orientation of three points (p, q, r).

    Returns
    -------
    negative if counterclockwise
    0 if colinear
    positive if clockwise

    """
    return (q[1] - p[1]) * (r[0] - q[0]) - (q[0] - p[0]) * (r[1] - q[1])


def _hull(points: Iterable[Point2D]) -> list[Point2D]:
    """Construct the upper/lower hull of a set of points."""
    stack: list[Point2D] = []
    for p in points:
        while (
            len(stack) >= 2  # noqa: PLR2004
            and _orientation(stack[-2], stack[-1], p) >= 0
        ):
            stack.pop()
        stack.append(p)
    return stack


def convex_hull(points: Iterable[Point2D]) -> LineType:
    """
    Return the convex hull of a set of points using Andrew's monotone chain algorithm.

    Args:
    ----
        points (Iterable[Point2D]): A collection of 2D points.

    Returns:
    -------
        LineType: The convex hull, represented as a list of points.

    """
    points = sorted(set(points))
    # No points, a single point or a line between two points
    if len(points) <= 2:  # noqa: PLR2004
        return points

    # Construct the upper and lower hulls
    upper = _hull(points)
    lower = _hull(reversed(points))
    if len(lower) == len(upper) == 2 and set(lower) == set(upper):  # noqa: PLR2004
        # all points are in a straight line
        return upper
    # Remove duplicate points (at the end of upper and beginning of lower)
    return dedupe(upper + lower)


def compare_coordinates(
    coords: float | CoordinatesType | MultiCoordinatesType,
    other: float | CoordinatesType | MultiCoordinatesType,
) -> bool:
    """Compare two coordinate sequences."""
    try:
        return all(
            compare_coordinates(coords=c, other=o)
            for c, o in zip_longest(
                coords,  # type: ignore [arg-type]
                other,  # type: ignore [arg-type]
                fillvalue=math.nan,
            )
        )
    except TypeError:
        try:
            return math.isclose(a=cast("float", coords), b=cast("float", other))
        except TypeError:
            return False


def compare_geo_interface(
    first: GeoInterface | GeoCollectionInterface,
    second: GeoInterface | GeoCollectionInterface,
) -> bool:
    """Compare two geo interfaces."""
    try:
        if first["type"] != second["type"]:
            return False
        if first["type"] == "GeometryCollection":
            return all(
                compare_geo_interface(first=g1, second=g2)  # type: ignore [arg-type]
                for g1, g2 in zip_longest(
                    first["geometries"],
                    second["geometries"],  # type: ignore [typeddict-item]
                    fillvalue={"type": None, "coordinates": ()},
                )
            )
        return compare_coordinates(
            coords=first["coordinates"],
            other=second["coordinates"],  # type: ignore [typeddict-item]
        )
    except KeyError:
        return False


def move_coordinate(
    coordinate: PointType,
    move_by: PointType,
) -> PointType:
    """
    Move the coordinate by the given vector.

    This forcefully changes the dimensions of the coordinate to match the latter.
    >>> move_coordinate((0, 0), (-1, 1))
    (-1, 1)
    >>> move_coordinate((0, 0, 0), (-1, 1))
    (-1, 1)
    >>> move_coordinate((0, 0), (-1, 1, 0))
    (-1, 1, 0)
    """
    if len(coordinate) < len(move_by):
        return cast(
            "PointType",
            tuple(c + m for c, m in zip_longest(coordinate, move_by, fillvalue=0)),
        )

    return cast(
        "PointType",
        tuple(c + m for c, m in zip(coordinate, move_by, strict=False)),
    )


def move_coordinates(
    coordinates: CoordinatesType,
    move_by: PointType,
) -> CoordinatesType:
    """
    Move the coordinates recursively by the given vector.

    This forcefully changes the dimension of each of the coordinate to match
    the dimensionality of the vector.
    >>> move_coordinates(((0, 0), (-1, 1)), (-1, 1))
    ((-1, 1), (-2, 2))
    >>> move_coordinates(((0, 0, 0), (-1, 1, 0)), (-1, 1))
    ((-1, 1), (-2, 2))
    >>> move_coordinates(((0, 0), (-1, 1)), (-1, 1, 0))
    ((-1, 1, 0), (-2, 2, 0))
    """
    if not coordinates:
        return coordinates
    if isinstance(coordinates[0], (int, float)):
        return move_coordinate(cast("PointType", coordinates), move_by)
    return cast(
        "CoordinatesType",
        tuple(
            move_coordinates(cast("CoordinatesType", c), move_by) for c in coordinates
        ),
    )


def move_geo_interface(
    interface: GeoInterface | GeoCollectionInterface,
    move_by: PointType,
) -> GeoInterface | GeoCollectionInterface:
    """Move the coordinates of the geo interface by the given vector."""
    if interface["type"] == "GeometryCollection":
        return {
            "type": "GeometryCollection",
            "geometries": tuple(
                move_geo_interface(g, move_by) for g in interface["geometries"]
            ),
        }
    return {
        "type": interface["type"],
        "coordinates": move_coordinates(
            interface["coordinates"],  # type: ignore [arg-type]
            move_by,
        ),
    }


__all__ = [
    "centroid",
    "compare_coordinates",
    "compare_geo_interface",
    "convex_hull",
    "dedupe",
    "move_coordinate",
    "move_coordinates",
    "signed_area",
]
