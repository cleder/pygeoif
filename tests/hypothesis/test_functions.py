"""Hypothesis test cases for the `pygeoif.functions` module."""

# This test code was written by the `hypothesis.extra.ghostwriter` module
# and is provided under the Creative Commons Zero public domain dedication.

import math

import more_itertools
from hypothesis import given
from hypothesis import strategies as st

import pygeoif.functions
import pygeoif.types


@given(
    coords=st.one_of(
        st.lists(
            st.tuples(
                st.floats(
                    allow_subnormal=False,
                ),
                st.floats(allow_subnormal=False),
            ),
        ),
        st.lists(
            st.tuples(
                st.floats(allow_subnormal=False),
                st.floats(allow_subnormal=False),
                st.floats(allow_subnormal=False),
            ),
        ),
    ),
)
def test_fuzz_centroid(
    coords: pygeoif.types.LineType,
) -> None:
    center, area = pygeoif.functions.centroid(coords=coords)
    if area == 0 or math.isnan(area):
        assert math.isnan(center[0])
        assert math.isnan(center[1])
    else:  # pragma: no cover
        assert isinstance(center[0], float)
        assert isinstance(center[1], float)
        assert len(center) == 2


@given(
    vertices=st.integers(min_value=3, max_value=24),
    radius=st.floats(min_value=1.0, max_value=1_000.0),
    center=st.tuples(
        st.floats(min_value=-100.0, max_value=100.0),
        st.floats(min_value=-100.0, max_value=100.0),
    ),
    offset=st.sampled_from([0.0, 1e3, 1e5, 1e7, 1e9, 1e10]),
)
def test_centroid_of_a_regular_polygon_is_its_center(
    vertices: int,
    radius: float,
    center: tuple[float, float],
    offset: float,
) -> None:
    """
    The centroid of a regular polygon is its center by symmetry.

    A closed form expectation that does not share any arithmetic with the
    implementation, so unlike a shape-only assertion it detects a centroid
    that has silently lost its significant digits.
    """
    expected_x, expected_y = center[0] + offset, center[1] + offset
    coords = [
        (
            expected_x + radius * math.cos(2 * math.pi * step / vertices),
            expected_y + radius * math.sin(2 * math.pi * step / vertices),
        )
        for step in range(vertices)
    ]
    coords.append(coords[0])

    computed, _ = pygeoif.functions.centroid(coords=coords)

    tolerance = 32 * math.ulp(max(abs(value) for point in coords for value in point))
    assert abs(computed[0] - expected_x) <= tolerance
    assert abs(computed[1] - expected_y) <= tolerance


@given(
    coords=st.one_of(
        st.floats(),
        st.lists(st.tuples(st.floats(), st.floats())),
        st.lists(st.tuples(st.floats(), st.floats(), st.floats())),
        st.lists(
            st.one_of(
                st.lists(st.tuples(st.floats(), st.floats())),
                st.lists(st.tuples(st.floats(), st.floats(), st.floats())),
            ),
        ),
        st.lists(
            st.one_of(
                st.lists(st.tuples(st.floats(), st.floats())),
                st.lists(st.tuples(st.floats(), st.floats(), st.floats())),
                st.lists(
                    st.one_of(
                        st.lists(st.tuples(st.floats(), st.floats())),
                        st.lists(st.tuples(st.floats(), st.floats(), st.floats())),
                    ),
                ),
                st.tuples(st.floats(), st.floats()),
                st.tuples(st.floats(), st.floats(), st.floats()),
            ),
        ),
        st.tuples(st.floats(), st.floats()),
        st.tuples(st.floats(), st.floats(), st.floats()),
    ),
    other=st.one_of(
        st.floats(),
        st.lists(st.tuples(st.floats(), st.floats())),
        st.lists(st.tuples(st.floats(), st.floats(), st.floats())),
        st.lists(
            st.one_of(
                st.lists(st.tuples(st.floats(), st.floats())),
                st.lists(st.tuples(st.floats(), st.floats(), st.floats())),
            ),
        ),
        st.lists(
            st.one_of(
                st.lists(st.tuples(st.floats(), st.floats())),
                st.lists(st.tuples(st.floats(), st.floats(), st.floats())),
                st.lists(
                    st.one_of(
                        st.lists(st.tuples(st.floats(), st.floats())),
                        st.lists(st.tuples(st.floats(), st.floats(), st.floats())),
                    ),
                ),
                st.tuples(st.floats(), st.floats()),
                st.tuples(st.floats(), st.floats(), st.floats()),
            ),
        ),
        st.tuples(st.floats(), st.floats()),
        st.tuples(st.floats(), st.floats(), st.floats()),
    ),
)
def test_fuzz_compare_coordinates(
    coords: float | pygeoif.types.CoordinatesType | pygeoif.types.MultiCoordinatesType,
    other: float | pygeoif.types.CoordinatesType | pygeoif.types.MultiCoordinatesType,
) -> None:
    assert isinstance(
        pygeoif.functions.compare_coordinates(coords=coords, other=other),
        bool,
    )

    flat_coords = (
        [coords] if isinstance(coords, float) else more_itertools.collapse(coords)
    )
    flat_other = [other] if isinstance(other, float) else more_itertools.collapse(other)

    if any(math.isnan(c) for c in flat_coords):  # pragma: no cover
        assert not pygeoif.functions.compare_coordinates(coords=coords, other=coords)
    else:  # pragma: no cover
        assert pygeoif.functions.compare_coordinates(coords=coords, other=coords)
    if any(math.isnan(c) for c in flat_other):  # pragma: no cover
        assert not pygeoif.functions.compare_coordinates(coords=other, other=other)
    else:  # pragma: no cover
        assert pygeoif.functions.compare_coordinates(coords=other, other=other)


@given(
    first=st.from_type(pygeoif.types.GeoInterface),
    second=st.from_type(pygeoif.types.GeoInterface),
)
def test_fuzz_compare_geo_interface(
    first: pygeoif.types.GeoInterface,
    second: pygeoif.types.GeoInterface,
) -> None:
    assert isinstance(
        pygeoif.functions.compare_geo_interface(first=first, second=second),
        bool,
    )


@given(
    points=st.lists(
        st.tuples(
            st.floats(
                allow_nan=False,
                allow_infinity=False,
                allow_subnormal=False,
                width=32,
            ),
            st.floats(
                allow_nan=False,
                allow_infinity=False,
                allow_subnormal=False,
                width=32,
            ),
        ),
    ),
)
def test_fuzz_convex_hull(points: list[tuple[float, float]]) -> None:
    hull = pygeoif.functions.convex_hull(points=points)

    for coord in hull:
        assert coord in points
    assert len(hull) <= len(points) + 1
    assert pygeoif.functions.signed_area(hull) >= 0


@given(
    coords=st.one_of(
        st.lists(st.tuples(st.floats(), st.floats())),
        st.lists(st.tuples(st.floats(), st.floats(), st.floats())),
    ),
)
def test_fuzz_dedupe(
    coords: pygeoif.types.LineType,
) -> None:
    deduped = pygeoif.functions.dedupe(coords=coords)

    assert len(deduped) <= len(coords)
    for coord in deduped:
        assert coord in coords


@given(
    coordinate=st.one_of(
        st.tuples(st.floats(), st.floats()),
        st.tuples(st.floats(), st.floats(), st.floats()),
    ),
    move_by=st.one_of(
        st.tuples(st.floats(), st.floats()),
        st.tuples(st.floats(), st.floats(), st.floats()),
    ),
)
def test_fuzz_move_coordinate(
    coordinate: pygeoif.types.PointType,
    move_by: pygeoif.types.PointType,
) -> None:
    moved = pygeoif.functions.move_coordinate(coordinate=coordinate, move_by=move_by)

    assert len(moved) == len(move_by)


@given(
    coordinates=st.one_of(
        st.lists(st.tuples(st.floats(), st.floats())),
        st.lists(st.tuples(st.floats(), st.floats(), st.floats())),
        st.lists(
            st.one_of(
                st.lists(st.tuples(st.floats(), st.floats())),
                st.lists(st.tuples(st.floats(), st.floats(), st.floats())),
            ),
        ),
        st.tuples(st.floats(), st.floats()),
        st.tuples(st.floats(), st.floats(), st.floats()),
    ),
    move_by=st.one_of(
        st.tuples(st.floats(), st.floats()),
        st.tuples(st.floats(), st.floats(), st.floats()),
    ),
)
def test_fuzz_move_coordinates(
    coordinates: pygeoif.types.CoordinatesType,
    move_by: pygeoif.types.PointType,
) -> None:
    moved = pygeoif.functions.move_coordinates(coordinates=coordinates, move_by=move_by)

    assert moved if coordinates else not moved


@given(
    coords=st.one_of(
        st.lists(st.tuples(st.floats(), st.floats())),
        st.lists(st.tuples(st.floats(), st.floats(), st.floats())),
    ),
)
def test_fuzz_signed_area(
    coords: pygeoif.types.LineType,
) -> None:
    assert isinstance(pygeoif.functions.signed_area(coords=coords), float)
