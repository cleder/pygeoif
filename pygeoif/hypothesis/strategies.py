"""
Data-generating strategies for property-based testing.

Coordinates are limited to 32 bit floats to avoid precision issues.
"""

from dataclasses import dataclass
from functools import partial
from typing import Optional
from typing import Tuple
from typing import cast

import hypothesis.strategies as st

from pygeoif.geometry import GeometryCollection
from pygeoif.geometry import LinearRing
from pygeoif.geometry import LineString
from pygeoif.geometry import MultiLineString
from pygeoif.geometry import MultiPoint
from pygeoif.geometry import MultiPolygon
from pygeoif.geometry import Point
from pygeoif.geometry import Polygon
from pygeoif.types import LineType
from pygeoif.types import Point2D
from pygeoif.types import Point3D
from pygeoif.types import PointType

__all__ = [
    "Srs",
    "geometry_collections",
    "line_coords",
    "line_strings",
    "linear_rings",
    "multi_line_strings",
    "multi_points",
    "multi_polygons",
    "point_coords",
    "points",
    "polygons",
]


coordinate = partial(
    st.floats,
    allow_infinity=False,
    allow_nan=False,
    allow_subnormal=False,
    width=32,
)


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

    def longitudes(self) -> st.SearchStrategy[float]:
        """
        Generate a search strategy for generating longitudes.

        Returns a search strategy that generates floats within the longitude bounds of
        the SRS.
        """
        return coordinate(min_value=self.min_xyz[0], max_value=self.max_xyz[0])

    def latitudes(self) -> st.SearchStrategy[float]:
        """
        Generate a search strategy for generating latitudes.

        Returns a search strategy that generates floats within the latitude bounds of
        the SRS.
        """
        return coordinate(min_value=self.min_xyz[1], max_value=self.max_xyz[1])

    def elevations(self) -> st.SearchStrategy[float]:
        """
        Generate a search strategy for generating elevations.

        Returns a search strategy that generates floats within the elevation bounds of
        the SRS.
        """
        return coordinate(min_value=self.min_xyz[2], max_value=self.max_xyz[2])


epsg4326 = Srs(
    name="EPSG:4326",
    min_xyz=(-180.0, -90.0, -999_999_995_904.0),
    max_xyz=(180.0, 90.0, 999_999_995_904.0),
)


@st.composite
def _point_coords_2d(
    draw: st.DrawFn,
    *,
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
        longitudes = srs.longitudes()
        latitudes = srs.latitudes()
    return draw(st.tuples(latitudes, longitudes))


@st.composite
def _point_coords_3d(
    draw: st.DrawFn,
    *,
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
        longitudes = srs.longitudes()
        latitudes = srs.latitudes()
        elevations = srs.elevations()
    return draw(st.tuples(latitudes, longitudes, elevations))


@st.composite
def point_coords(
    draw: st.DrawFn,
    *,
    srs: Optional[Srs] = None,
    has_z: Optional[bool] = None,
) -> PointType:
    """
    Generate a random point in either 2D or 3D space.

    Args:
    ----
        draw: The draw function from the hypothesis library.
        srs: An optional parameter specifying the spatial reference system.
        has_z: An optional parameter specifying whether to generate 2D or 3D points.

    Returns:
    -------
        A tuple representing the point in either 2D or 3D space.

    """
    if has_z is True:
        return draw(_point_coords_3d(srs=srs))
    if has_z is False:
        return draw(_point_coords_2d(srs=srs))
    return draw(st.one_of(_point_coords_2d(srs=srs), _point_coords_3d(srs=srs)))


@st.composite
def points(
    draw: st.DrawFn,
    *,
    srs: Optional[Srs] = None,
    has_z: Optional[bool] = None,
) -> Point:
    """
    Generate a random point in either 2D or 3D space.

    Args:
    ----
        draw: The draw function from the hypothesis library.
        srs: An optional parameter specifying the spatial reference system.
        has_z: An optional parameter specifying whether to generate 2D or 3D points.

    Returns:
    -------
        A randomly generated point in either 2D or 3D space.

    """
    return Point(*draw(point_coords(srs=srs, has_z=has_z)))


@st.composite
def line_coords(  # noqa: PLR0913
    draw: st.DrawFn,
    *,
    min_points: int,
    max_points: Optional[int] = None,
    srs: Optional[Srs] = None,
    has_z: Optional[bool] = None,
    unique: bool = False,
) -> LineType:
    """
    Generate a random line in either 2D or 3D space.

    Args:
    ----
        draw: The draw function from the hypothesis library.
        min_points: Minimum number of points in the line
        max_points: Maximum number of points in the line
        srs: An optional parameter specifying the spatial reference system.
        has_z: An optional parameter specifying whether to generate 2D or 3D points.
        unique: Optional flag to generate unique points (default False).

    Returns:
    -------
        A list of point coordinates representing the line in either 2D or 3D space.

    """
    if has_z is None:
        has_z = draw(st.booleans())
    return cast(
        LineType,
        draw(
            st.lists(
                point_coords(srs=srs, has_z=has_z),
                min_size=min_points,
                max_size=max_points,
                unique=unique,
            ),
        ),
    )


@st.composite
def line_strings(
    draw: st.DrawFn,
    *,
    max_points: Optional[int] = None,
    srs: Optional[Srs] = None,
    has_z: Optional[bool] = None,
) -> LineString:
    """
    Generate a random linestring in either 2D or 3D space.

    Args:
    ----
        draw: The draw function from the hypothesis library.
        max_points: Maximum number of points in the line (must be greater than 1)
        srs: An optional parameter specifying the spatial reference system.
        has_z: An optional parameter specifying whether to generate 2D or 3D lines.

    Returns:
    -------
        A LineString representing the randomly generated linestring in either 2D or 3D
        space.

    """
    if max_points is not None and max_points < 2:  # noqa: PLR2004
        raise ValueError("max_points must be greater than 1")  # noqa: TRY003,EM101
    return LineString(
        draw(
            line_coords(
                min_points=2,
                max_points=max_points,
                srs=srs,
                has_z=has_z,
                unique=True,
            ),
        ),
    )


@st.composite
def linear_rings(
    draw: st.DrawFn,
    *,
    max_points: Optional[int] = None,
    srs: Optional[Srs] = None,
    has_z: Optional[bool] = None,
) -> LinearRing:
    """
    Generate a linear ring using the provided draw function.

    Args:
    ----
        draw (st.DrawFn): The draw function used to generate the coordinates.
        max_points (Optional[int]): The maximum number of points in the linear ring.
        If not specified, there is no limit.
        srs (Optional[Srs]): The spatial reference system of the linear ring.
        If not specified, the default SRS is used.
        has_z (Optional[bool]): Whether the linear ring has z-coordinates.
        If not specified, 2D or 3D coordinates are generated.

    Returns:
    -------
        LinearRing: The generated linear ring.

    Raises:
    ------
        ValueError: If max_points is less than 4.

    """
    if max_points is not None and max_points < 4:  # noqa: PLR2004
        raise ValueError("max_points must be greater than 3")  # noqa: TRY003,EM101
    return LinearRing(
        draw(
            line_coords(
                min_points=3,
                max_points=max_points,
                srs=srs,
                has_z=has_z,
                unique=True,
            ),
        ),
    )


@st.composite
def polygons(  # noqa: PLR0913
    draw: st.DrawFn,
    *,
    max_points: Optional[int] = None,
    min_interiors: int = 0,
    max_interiors: int = 5,
    srs: Optional[Srs] = None,
    has_z: Optional[bool] = None,
) -> Polygon:
    """
    Generate a random polygon using the given strategies.

    Args:
    ----
        draw (st.DrawFn): The draw function used to generate random values.
        max_points (Optional[int]): The maximum number of points in the polygon.
        If not specified, there is no limit.
        min_interiors (Optional[int]): The minimum number of interior rings (holes)
        in the polygon. Defaults to 0.
        max_interiors (Optional[int]): The maximum number of interior rings (holes)
        in the polygon. If not specified, there is no limit.
        srs (Optional[Srs]): The spatial reference system of the polygon.
        Defaults to None.
        has_z (Optional[bool]): Whether the polygon has z-coordinates.
        If not specified, a random boolean value will be used.

    Returns:
    -------
        Polygon: The generated polygon.

    Raises:
    ------
        ValueError: If max_points is specified and is less than 4.

    """
    if has_z is None:
        has_z = draw(st.booleans())
    if max_points is not None and max_points < 4:  # noqa: PLR2004
        raise ValueError("max_points must be greater than 3")  # noqa: TRY003,EM101
    return Polygon(
        draw(
            line_coords(
                min_points=3,
                max_points=max_points,
                srs=srs,
                has_z=has_z,
                unique=True,
            ),
        ),
        holes=draw(
            st.lists(
                line_coords(
                    min_points=3,
                    max_points=max_points,
                    srs=srs,
                    has_z=has_z,
                    unique=True,
                ),
                min_size=min_interiors,
                max_size=max_interiors,
            ),
        ),
    )


@st.composite
def multi_points(
    draw: st.DrawFn,
    *,
    min_points: int = 1,
    max_points: Optional[int] = None,
    srs: Optional[Srs] = None,
    has_z: Optional[bool] = None,
) -> MultiPoint:
    """
    Generate a MultiPoint geometry object with random coordinates.

    Args:
    ----
        draw (st.DrawFn): The draw function from the hypothesis library.
        min_points (int): The minimum number of points in the MultiPoint. Default is 1.
        max_points (Optional[int]): The maximum number of points in the MultiPoint.
        srs (Optional[Srs]): The spatial reference system of the coordinates.
        has_z (Optional[bool]): Whether the coordinates have a Z component.
        if not specified, 2D and 3D coordinates will be generated randomly.

    Returns:
    -------
     MultiPoint: The generated MultiPoint geometry object.

    """
    if has_z is None:
        has_z = draw(st.booleans())
    return MultiPoint(
        draw(
            st.lists(
                point_coords(srs=srs, has_z=has_z),
                min_size=min_points,
                max_size=max_points,
                unique=True,
            ),
        ),
    )


@st.composite
def multi_line_strings(  # noqa: PLR0913
    draw: st.DrawFn,
    *,
    min_lines: int = 1,
    max_lines: int = 5,
    max_points: int = 10,
    srs: Optional[Srs] = None,
    has_z: Optional[bool] = None,
) -> MultiLineString:
    """
    Generate a random MultiLineString object.

    Args:
    ----
        draw (st.DrawFn): The Hypothesis draw function.
        min_lines (int, optional): The minimum number of lines in the MultiLineString.
        max_lines (int, optional): The maximum number of lines in the MultiLineString.
        max_points (int, optional): The maximum number of points in each line.
        srs (Srs, optional): The spatial reference system of the MultiLineString.
        has_z (bool, optional): Whether the MultiLineString has z-coordinates.

    Returns:
    -------
        MultiLineString: The generated MultiLineString object.

    """
    if has_z is None:
        has_z = draw(st.booleans())
    return MultiLineString(
        draw(
            st.lists(
                line_coords(
                    min_points=2,
                    max_points=max_points,
                    srs=srs,
                    has_z=has_z,
                    unique=True,
                ),
                min_size=min_lines,
                max_size=max_lines,
            ),
        ),
    )


@st.composite
def multi_polygons(  # noqa: PLR0913
    draw: st.DrawFn,
    *,
    min_polygons: int = 1,
    max_polygons: int = 3,
    max_points: int = 10,
    min_interiors: int = 0,
    max_interiors: int = 2,
    srs: Optional[Srs] = None,
    has_z: Optional[bool] = None,
) -> MultiPolygon:
    """
    Generate a random MultiPolygon object.

    Args:
    ----
        draw (st.DrawFn): The Hypothesis draw function.
        min_polygons (int, optional): The min number of polygons in the MultiPolygon.
        max_polygons (int, optional): The max number of polygons in the MultiPolygon.
        max_points (int, optional): The maximum number of points in each polygon.
        min_interiors (int, optional): The minimum number of interiors in each polygon.
        max_interiors (int, optional): The maximum number of interiors in each polygon.
        srs (Optional[Srs], optional): The spatial reference system of the MultiPolygon.
        has_z (Optional[bool], optional): Whether the MultiPolygon has z-coordinates.

    Returns:
    -------
        MultiPolygon: The generated MultiPolygon object.

    """
    if has_z is None:
        has_z = draw(st.booleans())
    return MultiPolygon.from_polygons(
        *draw(
            st.lists(
                polygons(
                    max_points=max_points,
                    min_interiors=min_interiors,
                    max_interiors=max_interiors,
                    srs=srs,
                    has_z=has_z,
                ),
                min_size=min_polygons,
                max_size=max_polygons,
            ),
        ),
    )


@st.composite
def geometry_collections(  # noqa: PLR0913
    draw: st.DrawFn,
    *,
    min_geoms: int = 1,
    max_geoms: int = 5,
    max_points: int = 20,
    min_interiors: int = 0,
    max_interiors: int = 5,
    srs: Optional[Srs] = None,
    has_z: Optional[bool] = None,
) -> GeometryCollection:
    """
    Generate a random GeometryCollection object.

    Args:
    ----
        draw (st.DrawFn): The Hypothesis draw function.
        min_geoms (int, optional): The minimum number of geometries in the collection.
        max_geoms (int, optional): The maximum number of geometries in the collection.
        max_points (int, optional): The maximum number of points in each geometry.
        min_interiors (int, optional): The minimum number of interiors in each polygon.
        max_interiors (int, optional): The maximum number of interiors in each polygon.
        srs (Optional[Srs], optional): The spatial reference system of the geometries.
        has_z (Optional[bool], optional): Whether the geometries have Z coordinates.

    Returns:
    -------
        GeometryCollection: A randomly generated GeometryCollection object.

    """
    if has_z is None:
        has_z = draw(st.booleans())
    return GeometryCollection(
        draw(
            st.lists(
                st.one_of(
                    points(srs=srs, has_z=has_z),
                    line_strings(max_points=max_points, srs=srs, has_z=has_z),
                    linear_rings(max_points=max_points, srs=srs, has_z=has_z),
                    polygons(
                        max_points=max_points,
                        min_interiors=min_interiors,
                        max_interiors=max_interiors,
                        srs=srs,
                        has_z=has_z,
                    ),
                    multi_points(max_points=max_points, srs=srs, has_z=has_z),
                    multi_line_strings(
                        max_points=max_points,
                        max_lines=max_geoms,
                        srs=srs,
                        has_z=has_z,
                    ),
                    multi_polygons(
                        max_points=max_points,
                        min_interiors=min_interiors,
                        max_interiors=max_interiors,
                        max_polygons=max_geoms,
                        srs=srs,
                        has_z=has_z,
                    ),
                ),
                min_size=min_geoms,
                max_size=max_geoms,
            ),
        ),
    )
