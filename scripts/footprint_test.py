import unittest
from shapely.geometry import Point, Polygon, MultiPolygon, MultiPoint, LineString,\
	GeometryCollection
import sys
sys.path.append('scripts/')
from polygon import Footprint


class FootprintTest(unittest.TestCase):
	"""
	Tests for footprint class
	"""
	def test_footprint(self):
		p = Polygon([(0, 0), (0, 2), (2, 2), (2, 0), (0, 0)])
		self.assertEqual(Footprint(p).polygon.geom_type, 'Polygon')

	def test_wrong_type_footprint(self):
		p = Point((0,0))
		self.assertRaises(TypeError, Footprint, p)

	def test_footprint_grow(self):
		p = Polygon([(0, 0), (0, 1), (1, 1), (1, 0), (0, 0)])
		p1 = Footprint(p).grow(1)
		self.assertEqual(round(p1.polygon.area), 8)

	def test_invalid_polygon(self):
		p = Polygon([(0, 0), (0, 2), (1, 1), (2, 2), (2, 0), (1, 1), (0, 0)])
		print(p.is_valid)
		self.assertEqual(Footprint(p).polygon.is_valid, True)

	def test_multipolygon(self):
		p1 = Polygon([(0, 0), (0, 2), (2, 2), (2, 0), (0, 0)])
		p2 = Polygon([(1, 1), (1, 3), (3, 3), (3, 1), (1, 1)])
		p = MultiPolygon([p1, p2])
		self.assertEqual(Footprint(p).polygon.is_valid, True)


if __name__ == '__main__':
	unittest.main(verbosity=2)


