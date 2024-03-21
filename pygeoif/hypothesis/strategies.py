"""Data-generating strategies for property-based testing."""

from dataclasses import dataclass
from functools import partial
from typing import Callable
from typing import Optional
from typing import Tuple
from typing import TypeVar
from typing import Union
from typing import cast

import hypothesis.strategies as st

from pygeoif.types import Point2D
from pygeoif.types import Point3D

__all__ = ["Srs", "epsg4326", "point_types", "points_2d", "points_3d"]

T = TypeVar("T")
Draw = TypeVar(
    "Draw",
    bound=Callable[[st.SearchStrategy[T]], T],  # type: ignore [valid-type]
)


@dataclass(frozen=True)
class Srs:
    """
    Represents a spatial reference system (SRS).

    Attributes
    ----------
        name (str): The name of the SRS.
        min_xyz (Tuple[Optional[float], Optional[float], Optional[float]]):
        The minimum x, y, and z values of the SRS.
        max_xyz (Tuple[Optional[float], Optional[float], Optional[float]]):
        The maximum x, y, and z values of the SRS.

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
def points_2d(
    draw: Draw,
    srs: Optional[Srs] = None,
) -> st.SearchStrategy[Point2D]:
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
    return cast(st.SearchStrategy[Point2D], draw(st.tuples(latitudes, longitudes)))


@st.composite
def points_3d(
    draw: Draw,
    srs: Optional[Srs] = None,
) -> st.SearchStrategy[Point3D]:
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
    return cast(
        st.SearchStrategy[Point3D],
        draw(st.tuples(latitudes, longitudes, elevations)),
    )


@st.composite
def point_types(draw: Draw, srs: Optional[Srs] = None) -> Union[
    st.SearchStrategy[Point2D],
    st.SearchStrategy[Point3D],
]:
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
    return draw(st.one_of(points_2d(srs), points_3d(srs)))
