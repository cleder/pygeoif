"""Exceptions for pygeoif."""


class DimensionError(IndexError):
    """Geometries must have 2 or 3 dimensions."""


class WKTParserError(AttributeError):
    """WKT not supported or cannot be parsed."""


__all__ = [
    "DimensionError",
    "WKTParserError",
]
