import unittest
from shapely.geometry import Point, Polygon, MultiPolygon, MultiPoint, LineString,\
	GeometryCollection
import sys

sys.path.append('scripts/')
from polygon import Collection, Footprint
from metrics import *


class MetricTest(unittest.TestCase):
	"""
	Tests for footprint class
	"""
	def test_metric_name(self):
		name = 'abc'
		self.assertEqual(Metric(name).name, name)

	def test_metric_name_non_str(self):
		name = 0
		self.assertRaises(TypeError, Metric, name)

	def test_footprint_grow(self):
		p = Polygon([(0, 0), (0, 1), (1, 1), (1, 0), (0, 0)])
		p1 = Footprint(p).grow(1)
		self.assertEqual(round(p1.polygon.area), 8)

	def test_cluster_number_metric(self):
		collection = Collection(int)
		for _ in range(6):
			collection.add(0)
		result = ClusterNumberMetric().calculate(collection)
		self.assertEqual(list(result.values())[0], len(collection))

	def test_cluster_number_metric_wrong_input(self):
		collection = [0] * 6
		result = ClusterNumberMetric()
		self.assertRaises(TypeError, result.calculate, collection)

	def test_min_cluster_distance_metric(self):
		p1 = Polygon([(0, 0), (0, 1), (1, 1), (1, 0), (0, 0)])
		p2 = Polygon([(0, 2), (2, 2), (2, 4), (0, 4), (0, 2)])
		collection = Collection(Footprint)
		collection.add(Footprint(p1))
		collection.add(Footprint(p2))
		result = MinimumClusterDistanceMetric().calculate(collection)
		self.assertEqual(list(result.values())[0], 0.5)

	def test_min_cluster_distance_metric_2(self):
		p1 = Polygon([(0, 0), (0, 1), (1, 1), (1, 0), (0, 0)])
		p2 = Polygon([(0, 2), (2, 2), (2, 4), (0, 4), (0, 2)])
		p3 = Polygon([(10, 2), (12, 2), (12, 4), (10, 4), (10, 2)])
		collection = Collection(Footprint)
		collection.add(Footprint(p1))
		collection.add(Footprint(p2))
		collection.add(Footprint(p3))
		result = MinimumClusterDistanceMetric().calculate(collection)
		self.assertEqual(list(result.values())[0], 4)

	def test_area_metric(self):
		p1 = Polygon([(0, 0), (0, 1), (1, 1), (1, 0), (0, 0)])
		collection = Collection(Footprint)
		collection.add(Footprint(p1))
		result = TotalAreaMetric().calculate(collection)
		self.assertEqual(list(result.values())[0], 1)

	def test_area_metric2(self):
		p1 = Polygon([(0, 0), (0, 1), (1, 1), (1, 0), (0, 0)])
		p2 = Polygon([(0, 2), (2, 2), (2, 4), (0, 4), (0, 2)])
		collection = Collection(Footprint)
		collection.add(Footprint(p1))
		collection.add(Footprint(p2))
		result = TotalAreaMetric().calculate(collection)
		self.assertEqual(list(result.values())[0], 5)

	def test_perimeter_metric(self):
		p1 = Polygon([(0, 0), (0, 1), (1, 1), (1, 0), (0, 0)])
		collection = Collection(Footprint)
		collection.add(Footprint(p1))
		result = TotalPerimeterMetric().calculate(collection)
		self.assertEqual(list(result.values())[0], 4)

	def test_distance_matrix_metric(self):
		p1 = Polygon([(0, 0), (0, 2), (2, 2), (2, 0), (0, 0)])
		p2 = Polygon([(0, 2), (2, 2), (2, 4), (0, 4), (0, 2)])
		collection = Collection(Footprint)
		collection.add(Footprint(p1))
		collection.add(Footprint(p2))
		result = DistanceMatrixMetric().calculate(collection)
		self.assertEqual(list(result.values())[0][0][1], 2)

	def test_distance_matrix_metric2(self):
		p1 = Polygon([(0, 0), (0, 2), (2, 2), (2, 0), (0, 0)])
		p2 = Polygon([(0, 2), (2, 2), (2, 4), (0, 4), (0, 2)])
		collection = Collection(Footprint)
		collection.add(Footprint(p1))
		collection.add(Footprint(p2))
		result = DistanceMatrixMetric().calculate(collection)
		self.assertEqual(list(result.values())[0][0][0], 0)


if __name__ == '__main__':
	unittest.main(verbosity=2)


