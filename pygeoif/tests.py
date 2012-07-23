# -*- coding: utf-8 -*-
import unittest
import geometry

class BasicTestCase(unittest.TestCase):

    def testPoint(self):
        self.assertRaises(ValueError, geometry.Point)
        p = geometry.Point(0, 1)
        self.assertEqual(p.x, 0.0)
        self.assertEqual(p.y, 1.0)
        self.assertEqual(p.__geo_interface__,
            {'type': 'Point', 'coordinates': (0.0, 1.0)})
        self.assertEqual(p.to_wkt(), 'POINT (0.0 1.0)')
        #self.assertRaises(ValueError, p.z)
        self.assertEqual(p.coords, (0.0, 1.0))
        p1 = geometry.Point(0, 1, 2)
        self.assertEqual(p1.x, 0.0)
        self.assertEqual(p1.y, 1.0)
        self.assertEqual(p1.z, 2.0)
        self.assertEqual(p1.coords, (0.0, 1.0, 2.0))
        self.assertEqual(p1.__geo_interface__,
            {'type': 'Point', 'coordinates': (0.0, 1.0, 2.0)})
        p2 = geometry.Point([0, 1])
        self.assertEqual(p2.x, 0.0)
        self.assertEqual(p2.y, 1.0)
        #self.assertRaises(ValueError, p2.z)
        p3 = geometry.Point([0, 1, 2])
        self.assertEqual(p3.x, 0.0)
        self.assertEqual(p3.y, 1.0)
        self.assertEqual(p3.z, 2.0)
        p4 = geometry.Point(p)
        self.assertEqual(p4.x, 0.0)
        self.assertEqual(p4.y, 1.0)
        #self.assertRaises(ValueError, p4.z)
        p5 = geometry.Point(p1)
        self.assertEqual(p5.x, 0.0)
        self.assertEqual(p5.y, 1.0)
        self.assertEqual(p5.z, 2.0)
        self.assertRaises(TypeError, geometry.Point, '1.0, 2.0')
        self.assertRaises(ValueError, geometry.Point, '1.0', 'a')
        self.assertRaises(TypeError, geometry.Point, (0,1,2,3,4))
        #you may also pass string values as internally they get converted
        #into floats, but this is not recommended
        p6 = geometry.Point('0', '1')
        self.assertEqual(p.__geo_interface__,p6.__geo_interface__)
        p6.coords = [0,1,2]
        self.assertEqual(p3.coords, p6.coords)

    def testLineString(self):
        l = geometry.LineString([(0, 0), (1, 1)])
        self.assertEqual(l.coords, ((0.0, 0.0), (1.0, 1.0)))
        self.assertEqual(l.coords[:1], ((0.0, 0.0),))
        self.assertEqual(l.__geo_interface__, {'type': 'LineString',
                            'coordinates': ((0.0, 0.0), (1.0, 1.0))})
        self.assertEqual(l.to_wkt(), 'LINESTRING (0.0 0.0, 1.0 1.0)')
        p = geometry.Point(0, 0)
        p1 = geometry.Point(1, 1)
        p2 = geometry.Point(2, 2)
        l1 = geometry.LineString([p, p1, p2])
        self.assertEqual(l1.coords, ((0.0, 0.0), (1.0, 1.0), (2.0, 2.0)))
        l2 = geometry.LineString(l1)
        self.assertEqual(l2.coords, ((0.0, 0.0), (1.0, 1.0), (2.0, 2.0)))
        l.coords = l2.coords
        self.assertEqual(l.__geo_interface__, l2.__geo_interface__)
        #self.assertRaises(ValueError, geometry.LineString([(0, 0, 0), (1, 1)]))


    def testLinearRing(self):
        r = geometry.LinearRing([(0, 0), (1, 1), (1, 0), (0, 0)])
        self.assertEqual(r.coords,((0, 0), (1, 1), (1, 0), (0, 0)))
        l = geometry.LineString(r)
        self.assertEqual(l.coords,((0, 0), (1, 1), (1, 0), (0, 0)))
        self.assertEqual(r.__geo_interface__, {'type': 'LinearRing',
                            'coordinates': ((0.0, 0.0), (1.0, 1.0),
                                            (1.0, 0.0), (0.0, 0.0))})
        #r1 = geometry.LinearRing([(0, 0), (1, 1), (1, 0)])
        #self.assertRaises(ValueError, r1.coords)

    def testPolygon(self):
        p = geometry.Polygon([(0, 0), (1, 1), (1, 0), (0, 0)])
        self.assertEqual(p.exterior.coords, ((0.0, 0.0), (1.0, 1.0),
                                            (1.0, 0.0), (0.0, 0.0)))
        self.assertEqual(list(p.interiors), [])
        self.assertEqual(p.__geo_interface__, {'type': 'Polygon',
                            'coordinates': (((0.0, 0.0), (1.0, 1.0),
                            (1.0, 0.0), (0.0, 0.0)),)})
        r = geometry.LinearRing([(0, 0), (1, 1), (1, 0), (0, 0)])
        p1 = geometry.Polygon(r)
        self.assertEqual(p1.exterior.coords, r.coords)
        e = [(0, 0), (0, 2), (2, 2), (2, 0), (0, 0)]
        i = [(1, 0), (0.5, 0.5), (1, 1), (1.5, 0.5), (1, 0)]
        ph1 = geometry.Polygon(e, [i])
        self.assertEqual(ph1.exterior.coords, tuple(e))
        self.assertEqual(list(ph1.interiors)[0].coords, tuple(i))
        self.assertEqual(ph1.__geo_interface__, {'type': 'Polygon',
                'coordinates': (((0.0, 0.0), (0.0, 2.0), (2.0, 2.0),
                                (2.0, 0.0), (0.0, 0.0)),
                                ((1.0, 0.0), (0.5, 0.5),
                                (1.0, 1.0), (1.5, 0.5), (1.0, 0.0)))})
        ext = [(0, 0), (0, 2), (2, 2), (2, 0), (0, 0)]
        int_1 = [(0.5, 0.25), (1.5, 0.25), (1.5, 1.25), (0.5, 1.25), (0.5, 0.25)]
        int_2 = [(0.5, 1.25), (1, 1.25), (1, 1.75), (0.5, 1.75), (0.5, 1.25)]
        ph2 = geometry.Polygon(ext, [int_1, int_2])
        self.assertEqual(ph2.exterior.coords, tuple(ext))
        self.assertEqual(list(ph2.interiors)[0].coords, tuple(int_1))
        self.assertEqual(list(ph2.interiors)[1].coords, tuple(int_2))
        import pdb; pdb.set_trace()
        self.assertEqual(ph2.__geo_interface__, {'type': 'Polygon',
                'coordinates': (((0.0, 0.0), (0.0, 2.0), (2.0, 2.0),
                        (2.0, 0.0), (0.0, 0.0)),
                        ((0.5, 0.25), (1.5, 0.25),
                        (1.5, 1.25), (0.5, 1.25), (0.5, 0.25)),
                        ((0.5, 1.25), (1.0, 1.25), (1.0, 1.75),
                        (0.5, 1.75), (0.5, 1.25)))})



    def test_from_wkt(self):
        p = geometry.from_wkt('POINT (0.0 1.0)')
        self.assertEqual(isinstance(p, geometry.Point), True)
        self.assertEqual(p.x, 0.0)
        self.assertEqual(p.y, 1.0)
        l = geometry.from_wkt('LINESTRING(-72.991 46.177,-73.079 46.16,-73.146 46.124,-73.177 46.071,-73.164 46.044)')
        self.assertEqual(l.to_wkt(), 'LINESTRING (-72.991 46.177, -73.079 46.16, -73.146 46.124, -73.177 46.071, -73.164 46.044)')




def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(BasicTestCase))
    return suite

if __name__ == '__main__':
    unittest.main()
