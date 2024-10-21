#
#   Copyright (C) 2012 - 2023 Christian Ledermann
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
"""PyGeoIf provides a GeoJSON-like protocol for geo-spatial (GIS) vector data."""

from pygeoif.about import __version__  # noqa: F401
from pygeoif.factories import force_2d
from pygeoif.factories import force_3d
from pygeoif.factories import from_wkt
from pygeoif.factories import mapping
from pygeoif.factories import orient
from pygeoif.factories import shape
from pygeoif.feature import Feature
from pygeoif.feature import FeatureCollection
from pygeoif.geometry import GeometryCollection
from pygeoif.geometry import LinearRing
from pygeoif.geometry import LineString
from pygeoif.geometry import MultiLineString
from pygeoif.geometry import MultiPoint
from pygeoif.geometry import MultiPolygon
from pygeoif.geometry import Point
from pygeoif.geometry import Polygon

__all__ = [
    "Feature",
    "FeatureCollection",
    "GeometryCollection",
    "LineString",
    "LinearRing",
    "MultiLineString",
    "MultiPoint",
    "MultiPolygon",
    "Point",
    "Polygon",
    "force_2d",
    "force_3d",
    "from_wkt",
    "mapping",
    "orient",
    "shape",
]
