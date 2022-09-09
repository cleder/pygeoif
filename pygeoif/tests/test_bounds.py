"""Optimize bounds for multigeometries."""

minx = (1, 2, 3, 4)
miny = (8, 7, 6, 5)
maxx = (5, 6, 7, 8)
maxy = (9, 8, 7, 6)


def get_bounds():
    return zip(minx, miny, maxx, maxy)


def test_bounds() -> None:
    assert list(get_bounds()) == [
        (1, 8, 5, 9),
        (2, 7, 6, 8),
        (3, 6, 7, 7),
        (4, 5, 8, 6),
    ]


def test_brute() -> None:
    new_bounds = (
        min(b[0] for b in get_bounds()),
        min(b[1] for b in get_bounds()),
        max(b[2] for b in get_bounds()),
        max(b[3] for b in get_bounds()),
    )

    assert new_bounds == (1, 5, 8, 9)


def test_unzip() -> None:
    assert list(zip(*get_bounds())) == [minx, miny, maxx, maxy]


def test_bounds_unzipped() -> None:
    tb = list(zip(*get_bounds()))
    new_bounds = (
        min(tb[0]),
        min(tb[1]),
        max(tb[2]),
        max(tb[3]),
    )

    assert new_bounds == (1, 5, 8, 9)


def get_line():
    return zip(minx, miny)


def test_line() -> None:
    assert list(get_line()) == [
        (1, 8),
        (2, 7),
        (3, 6),
        (4, 5),
    ]


def test_unzip_line() -> None:
    assert list(zip(*get_line())) == [(1, 2, 3, 4), (8, 7, 6, 5)]


def test_line_bounds() -> None:
    xy = list(zip(*get_line()))

    bounds = (
        min(xy[0]),
        min(xy[1]),
        max(xy[0]),
        max(xy[1]),
    )

    assert bounds == (1, 5, 4, 8)
