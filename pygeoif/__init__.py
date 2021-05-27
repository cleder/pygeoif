# -*- coding: utf-8 -*-
#
#   Copyright (C) 2012 - 2021 Christian Ledermann
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
from .factories import from_wkt
from .factories import mapping
from .factories import orient
from .factories import shape
from .feature import Feature
from .feature import FeatureCollection
from .geometry import GeometryCollection
from .geometry import LinearRing
from .geometry import LineString
from .geometry import MultiLineString
from .geometry import MultiPoint
from .geometry import MultiPolygon
from .geometry import Point
from .geometry import Polygon

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
    "from_wkt",
    "geometry",
    "mapping",
    "orient",
    "shape",
]
