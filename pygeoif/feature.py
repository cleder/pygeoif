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
#
# file deepcode ignore inconsistent~equality: Python 3 only
"""Features."""
from typing import Any
from typing import Dict
from typing import Generator
from typing import Iterator
from typing import Optional
from typing import Sequence
from typing import Union
from typing import cast

from pygeoif.functions import compare_coordinates
from pygeoif.geometry import Geometry
from pygeoif.types import Bounds
from pygeoif.types import GeoFeatureCollectionInterface
from pygeoif.types import GeoFeatureInterface


def feature_geo_interface_equals(
    my_interface: GeoFeatureInterface,
    other_interface: GeoFeatureInterface,
) -> bool:
    """Check if my interface is the same as the other interface."""
    return all(
        [
            my_interface.get("id") == other_interface.get("id"),
            my_interface["type"] == other_interface.get("type"),
            my_interface["properties"] == other_interface.get("properties"),
            my_interface["geometry"]["type"] == other_interface["geometry"].get("type"),
            compare_coordinates(
                coords=my_interface["geometry"]["coordinates"],
                other=other_interface["geometry"].get(  # type: ignore [arg-type]
                    "coordinates",
                ),
            ),
        ],
    )


class Feature:
    """
    Aggregates a geometry instance with associated user-defined properties.

    Attributes:
    ----------
    geometry : object
        A geometry instance
    properties : dict
        A dictionary linking field keys with values
        associated with geometry instance

    Example:
    -------
     >>> p = Point(1.0, -1.0)
     >>> props = {'Name': 'Sample Point', 'Other': 'Other Data'}
     >>> a = Feature(p, props)
     >>> a.properties
     {'Name': 'Sample Point', 'Other': 'Other Data'}
      >>> a.properties['Name']
     'Sample Point'

    """

    def __init__(
        self,
        geometry: Geometry,
        properties: Optional[Dict[str, Any]] = None,
        feature_id: Optional[Union[str, int]] = None,
    ) -> None:
        """Initialize the feature."""
        self._geometry = geometry
        self._properties = properties or {}
        self._feature_id = feature_id

    def __eq__(self, other: object) -> bool:
        """Check if the geointerfaces are equal."""
        try:
            if not other.__geo_interface__.get(  # type: ignore [attr-defined]
                "geometry",
            ):
                return False
        except AttributeError:
            return False
        return feature_geo_interface_equals(
            my_interface=self.__geo_interface__,
            other_interface=other.__geo_interface__,  # type: ignore [attr-defined]
        )

    def __repr__(self) -> str:
        """Return the representation."""
        return (
            f"{self.__class__.__name__}({self._geometry!r},"
            f" {self._properties}, {self._feature_id!r})"
        )

    @property
    def id(self) -> Optional[Union[str, int]]:
        """Return the id of the feature."""
        return self._feature_id

    @property
    def geometry(self) -> Geometry:
        """Return the geometry of the feature."""
        return self._geometry

    @property
    def properties(self) -> Dict[str, Any]:
        """Return a dictionary of properties."""
        return self._properties

    @property
    def __geo_interface__(self) -> GeoFeatureInterface:
        """Return the GeoInterface of the geometry with properties."""
        geo_interface: GeoFeatureInterface = {
            "type": "Feature",
            "bbox": cast(Bounds, self._geometry.bounds),
            "geometry": self._geometry.__geo_interface__,
            "properties": self._properties,
        }
        if self._feature_id is not None:
            geo_interface["id"] = self._feature_id

        return geo_interface


class FeatureCollection:
    """
    A heterogenous collection of Features.

    Attributes:
    ----------
    features : sequence
        A sequence of feature instances


    Example:
    -------
    >>> from pygeoif import geometry
    >>> p = geometry.Point(1.0, -1.0)
    >>> props = {'Name': 'Sample Point', 'Other': 'Other Data'}
    >>> a = geometry.Feature(p, props)
    >>> p2 = geometry.Point(1.0, -1.0)
    >>> props2 = {'Name': 'Sample Point2', 'Other': 'Other Data2'}
    >>> b = geometry.Feature(p2, props2)
    >>> features = [a, b]
    >>> c = geometry.FeatureCollection(features)
    >>> c.__geo_interface__
    {'type': 'FeatureCollection',
     'features': [{'geometry': {'type': 'Point', 'coordinates': (1.0, -1.0)},
     'type': 'Feature',
     'properties': {'Other': 'Other Data', 'Name': 'Sample Point'}},
    {'geometry': {'type': 'Point', 'coordinates': (1.0, -1.0)},
     'type': 'Feature',
     'properties': {'Other': 'Other Data2', 'Name': 'Sample Point2'}}]}

    """

    def __init__(self, features: Sequence[Feature]) -> None:
        """Initialize the feature."""
        self._features = tuple(features)

    def __eq__(self, other: object) -> bool:
        """Check if the geointerfaces are equal."""
        return self._check_interface(other) and all(
            (
                feature_geo_interface_equals(my_interface=mine, other_interface=other)
                for mine, other in zip(
                    self.__geo_interface__["features"],
                    other.__geo_interface__["features"],  # type: ignore [attr-defined]
                )
            ),
        )

    def __len__(self) -> int:
        """Return the umber of features in this collection."""
        return len(self._features)

    def __iter__(self) -> Iterator[Feature]:
        """Iterate over the features of the collection."""
        return iter(self._features)

    def __repr__(self) -> str:
        """Return the representation."""
        return f"{self.__class__.__name__}({self._features!r})"

    @property
    def features(self) -> Generator[Feature, None, None]:
        """Iterate over the features of the collection."""
        yield from self._features

    @property
    def bounds(self) -> Bounds:
        """Return the X-Y bounding box."""
        geom_bounds = list(
            zip(*(feature.geometry.bounds for feature in self._features)),
        )
        return (
            min(geom_bounds[0]),
            min(geom_bounds[1]),
            max(geom_bounds[2]),
            max(geom_bounds[3]),
        )

    @property
    def __geo_interface__(self) -> GeoFeatureCollectionInterface:
        """Return the GeoInterface of the feature."""
        return {
            "type": "FeatureCollection",
            "bbox": self.bounds,
            "features": tuple(feature.__geo_interface__ for feature in self._features),
        }

    def _check_interface(self, other: object) -> bool:
        try:
            return self.__geo_interface__[
                "type"
            ] == other.__geo_interface__.get(  # type: ignore [attr-defined]
                "type",
            ) and len(
                self.__geo_interface__["features"],
            ) == len(
                other.__geo_interface__.get(  # type: ignore [attr-defined]
                    "features",
                    [],
                ),
            )
        except AttributeError:
            return False


__all__ = [
    "Feature",
    "FeatureCollection",
]
