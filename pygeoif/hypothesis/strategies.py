"""Data-generating strategies for property-based testing."""

from dataclasses import dataclass
from functools import partial
from typing import Optional
from typing import Tuple

import hypothesis.strategies as st

from pygeoif.geometry import Point
from pygeoif.types import Point2D
from pygeoif.types import Point3D
from pygeoif.types import PointType

__all__ = [
    "Srs",
    "epsg4326",
    "point_coords",
    "point_coords_2d",
    "point_coords_3d",
    "points",
]


@dataclass(frozen=True)
class Srs:
    """
    Represents a spatial reference system (SRS).

    Attributes
    ----------
        name (str): The name of the SRS.
        min_xyz (Tuple[Optional[float], Optional[float], Optional[float]]):
        - The minimum x, y, and z values of the SRS.
        max_xyz (Tuple[Optional[float], Optional[float], Optional[float]]):
        - The maximum x, y, and z values of the SRS.

    """

    name: str
    min_xyz: Tuple[Optional[float], Optional[float], Optional[float]]
    max_xyz: Tuple[Optional[float], Optional[float], Optional[float]]


epsg4326 = Srs(
    name="EPSG:4326",
    min_xyz=(-180.0, -90.0, -1_000_000_000_000.0),
    max_xyz=(180.0, 90.0, 1_000_000_000_000.0),
)

coordinate = partial(st.floats, allow_infinity=False, allow_nan=False)


@st.composite
def point_coords_2d(
    draw: st.DrawFn,
    srs: Optional[Srs] = None,
) -> Point2D:
    """
    Generate 2D points using the given draw function.

    Args:
    ----
        draw: The draw function used to generate the points.
        srs: Optional spatial reference system (Srs) object.

    Returns:
    -------
        A tuple of latitude and longitude values generated using the draw function.

    """
    longitudes = coordinate()
    latitudes = coordinate()
    if srs:
        longitudes = coordinate(min_value=srs.min_xyz[0], max_value=srs.max_xyz[0])
        latitudes = coordinate(min_value=srs.min_xyz[1], max_value=srs.max_xyz[1])
    return draw(st.tuples(latitudes, longitudes))


@st.composite
def point_coords_3d(
    draw: st.DrawFn,
    srs: Optional[Srs] = None,
) -> Point3D:
    """
    Generate 3D points using the given draw function.

    Args:
    ----
        draw: The draw function used to generate the points.
        srs: Optional spatial reference system (Srs) object.

    Returns:
    -------
        A tuple representing the generated 3D points.

    """
    longitudes = coordinate()
    latitudes = coordinate()
    elevations = coordinate()
    if srs:
        longitudes = coordinate(min_value=srs.min_xyz[0], max_value=srs.max_xyz[0])
        latitudes = coordinate(min_value=srs.min_xyz[1], max_value=srs.max_xyz[1])
        elevations = coordinate(min_value=srs.min_xyz[2], max_value=srs.max_xyz[2])
    return draw(st.tuples(latitudes, longitudes, elevations))


@st.composite
def point_coords(draw: st.DrawFn, srs: Optional[Srs] = None) -> PointType:
    """
    Generate a random point in either 2D or 3D space.

    Args:
    ----
        draw: The draw function from the hypothesis library.
        srs: An optional parameter specifying the spatial reference system.

    Returns:
    -------
        A randomly generated point in either 2D or 3D space.

    """
    return draw(st.one_of(point_coords_2d(srs), point_coords_3d(srs)))


@st.composite
def points(draw: st.DrawFn, srs: Optional[Srs] = None) -> Point:
    """
    Generate a random point in either 2D or 3D space.

    Args:
    ----
        draw: The draw function from the hypothesis library.
        srs: An optional parameter specifying the spatial reference system.

    Returns:
    -------
        A randomly generated point in either 2D or 3D space.

    """
    return Point(*draw(point_coords(srs)))
