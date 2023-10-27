#
#   Copyright (C) 2012 -2022  Christian Ledermann
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
"""Exceptions for pygeoif."""


class DimensionError(ValueError):
    """Geometries must have 2 or 3 dimensions."""


class WKTParserError(AttributeError):
    """WKT not supported or cannot be parsed."""


class InvalidGeometryError(ValueError):
    """Geometry is not valid."""


__all__ = [
    "DimensionError",
    "InvalidGeometryError",
    "WKTParserError",
]
