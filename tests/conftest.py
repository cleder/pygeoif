"""Data-generating strategies for property-based testing."""
import hypothesis.strategies as st

# Incomplete list of allowed spatial reference systems to generate data
# - EPSG 4326
# - EPSG 3857
# ...?


# EPSG:4326 primitives
latitudes = st.floats(
    min_value=-90.0,
    max_value=90.0,
    allow_nan=False,
    allow_infinity=False,
)
longitudes = st.floats(
    min_value=-180.0,
    max_value=180.0,
    allow_nan=False,
    allow_infinity=False,
)
elevations = st.floats(allow_nan=False, allow_infinity=False)


# Point2D
@st.composite
def points_2d(draw, srs="EPSG:4326"):
    if srs == "EPSG:4326":
        return draw(st.tuples(latitudes, longitudes))
    raise NotImplementedError


# Point3D
@st.composite
def points_3d(draw, srs="EPSG:4326"):
    if srs == "EPSG:4326":
        return draw(st.tuples(latitudes, longitudes, elevations))
    raise NotImplementedError


# PointType
@st.composite
def points(draw, srs="EPSG:4326"):
    if srs == "EPSG:4326":
        return draw(st.one_of(points_2d(), points_3d()))
    raise NotImplementedError


# LineType

# Geometries
