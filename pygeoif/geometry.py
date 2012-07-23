# -*- coding: utf-8 -*-

class _Feature(object):
    """ Base class """
    _type = None
    _coordinates = None

    @property
    def __geo_interface__(self):
        if self._type and self._coordinates:
            return {
                    'type': self._type,
                    'coordinates': tuple(self._coordinates)
                    }

    def __str__(self):
        return self.to_wkt()

    def to_wkt(self):
        return self._type.upper() + ' ' + str(tuple(self._coordinates)).replace(',','')


class Point(_Feature):
    """
    A zero dimensional feature

    A point has zero length and zero area.

    Attributes
    ----------
    x, y, z : float
        Coordinate values

    Example
    -------

      >>> p = Point(1.0, -1.0)
      >>> print p
      POINT (1.0000000000000000 -1.0000000000000000)
      >>> p.y
      -1.0
      >>> p.x
      1.0
    """

    _type = 'Point'

    def __init__(self, *args):
        """
        Parameters
        ----------
        There are 2 cases:

        1) 1 parameter: this must satisfy the __geo_interface__ protocol
            or be a tuple or list of x, y, [z]
        2) 2 or more parameters: x, y, [z] : float
            Easting, northing, and elevation.
        """
        if len(args) == 1:
            if hasattr(args[0], '__geo_interface__'):
                if args[0].__geo_interface__['type'] == 'Point':
                    self._coordinates = list(args[0].__geo_interface__['coordinates'])
                else:
                    raise TypeError
            else:
                if isinstance(args[0], (list, tuple)):
                    if 2 <= len(args[0]) <= 3:
                        coords = [float(x) for x in args[0]]
                        self._coordinates = coords
                    else:
                        raise TypeError
                else:
                    raise TypeError
        elif 2 <= len(args) <= 3:
            coords = [float(x) for x in args]
            self._coordinates = coords
        else:
            raise ValueError


    @property
    def x(self):
        """Return x coordinate."""
        return self._coordinates[0]

    @property
    def y(self):
        """Return y coordinate."""
        return self._coordinates[1]

    @property
    def z(self):
        """Return z coordinate."""
        if len(self._coordinates) != 3:
            #("This point has no z coordinate.")
            raise ValueError
        return self._coordinates[2]

    @property
    def coords(self):
        return tuple(self._coordinates)

    @coords.setter
    def coords(self, coordinates):
        if isinstance(coordinates, (list, tuple)):
            if 2 <= len(coordinates) <= 3:
                coords = [float(x) for x in coordinates]
                self._coordinates = coords
            else:
                raise TypeError
        else:
            raise TypeError



class LineString(_Feature):
    """A one-dimensional figure comprising one or more line segments """
    _type = 'LineString'

    def __init__(self, coordinates=None):
        """
        Parameters
        ----------
        coordinates : sequence
            A sequence of (x, y [,z]) numeric coordinate pairs or triples
            or a sequence of Points or
            an object that provides the __geo_interface__, including another
            instance of LineString.

        Example
        -------
        Create a line with two segments

          >>> a = LineString([[0, 0], [1, 0], [1, 1]])
        """

        if hasattr(coordinates, '__geo_interface__'):
            gi = coordinates.__geo_interface__
            if gi['type'] == 'LineString' or gi['type'] == 'LinearRing':
                self._coordinates = gi['coordinates']
            #XXX from polygon
            else:
                raise NotImplementedError
        elif isinstance(coordinates, (list, tuple)):
            coords = []
            for coord in coordinates:
                p = Point(coord)
                l = len(p.coords)
                if coords:
                    if l != l2:
                        raise ValueError
                l2 = l
                coords.append(tuple(p.coords))
            self._coordinates = coords
        else:
            raise ValueError


    @property
    def coords(self):
        return tuple(self._coordinates)

    @coords.setter
    def coords(self, coordinates):
        if isinstance(coordinates, (list, tuple)):
            coords = []
            for coord in coordinates:
                p = Point(coord)
                l = len(p.coords)
                if coords:
                    if l != l2:
                        raise ValueError
                l2 = l
                coords.append(tuple(p.coords))
            self._coordinates = coords
        else:
            raise ValueError

    def to_wkt(self):
        wc = [ ' '.join([str(x) for x in c]) for c in self.coords]
        return self._type.upper() + ' (' + ', '.join(wc) + ')'



class LinearRing(LineString):
    """
    A closed one-dimensional feature comprising one or more line segments

    A LinearRing that crosses itself or touches itself at a single point is
    invalid and operations on it may fail.
    """
    _type = 'LinearRing'

    @property
    def coords(self):
        if self._coordinates[0] == self._coordinates[-1]:
            return tuple(self._coordinates)
        else:
            raise ValueError

    #XXX the coords.setter and __init__ should either complain about
    # a non closed ring or close it automatically


class Polygon(_Feature):
    """
    A two-dimensional figure bounded by a linear ring

    A polygon has a non-zero area. It may have one or more negative-space
    "holes" which are also bounded by linear rings. If any rings cross each
    other, the feature is invalid and operations on it may fail.

    Attributes
    ----------
    exterior : LinearRing
        The ring which bounds the positive space of the polygon.
    interiors : sequence
        A sequence of rings which bound all existing holes.
    """
    _type = 'Polygon'
    _exterior = None
    _interiors = None

    @property
    def __geo_interface__(self):
        if self._interiors:
            return {
                'type': self._type,
                'coordinates': (self._exterior.coords,
                        tuple([i.coords for i in self.interiors])
                    )
                }
        elif self._exterior:
            return {
                'type': self._type,
                'coordinates': (self._exterior.coords,)

                }



    def __init__(self, shell=None, holes=None):
        """
        Parameters
        ----------
        shell : sequence
            A sequence of (x, y [,z]) numeric coordinate pairs or triples
            or a LinearRing.
            If a Polygon is passed as shell the holes parameter will be
            ignored
        holes : sequence
            A sequence of objects which satisfy the same requirements as the
            shell parameters above

        Example
        -------
        Create a square polygon with no holes

          >>> coords = ((0., 0.), (0., 1.), (1., 1.), (1., 0.), (0., 0.))
          >>> polygon = Polygon(coords)
          >>> polygon.area
          1.0
        """

        if hasattr(shell, '__geo_interface__'):
            gi = shell.__geo_interface__
            if gi['type'] == 'LinearRing':
                self._exterior = LinearRing(shell)
            #XXX Polygon
            else:
                raise NotImplementedError
        elif isinstance(shell, (list, tuple)):
            self._exterior = LinearRing(shell)
        #else:
        #    raise ValueError
        if holes:
            self._interiors = []
            for hole in holes:
                if hasattr(hole, '__geo_interface__'):
                    gi = hole.__geo_interface__
                    if gi['type'] == 'LinearRing':
                        self._interiors.append(LinearRing(hole))
                    else:
                        raise NotImplementedError
                elif isinstance(hole, (list, tuple)):
                    self._interiors.append(LinearRing(hole))
        else:
            self._interiors = []

    @property
    def exterior(self):
        if self._exterior is not None:
            return self._exterior

    @property
    def interiors(self):
        if self._exterior is not None:
            if self._interiors:
                for interior in self._interiors:
                    yield interior
        else:
            yield []


class MultiPoint(_Feature):
    pass

class MultiLineString(_Feature):
    pass

class MultiPolygon(_Feature):
    pass

class GeometryCollection(_Feature):
    pass

def from_wkt(wkt):
    if wkt.startswith('POINT'):
        coords = wkt[wkt.find('(') + 1 : wkt.find(')')].split()
        return Point(coords)
    if wkt.startswith('LINESTRING'):
        coords = wkt[wkt.find('(') + 1 : wkt.find(')')].split(',')
        return LineString([c.split() for c in coords])



