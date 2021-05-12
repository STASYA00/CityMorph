import numpy as np
from shapely.geometry import MultiPolygon
import sys
from time import time

sys.path.append('scripts/')
from polygon import Collection, Footprint


class MetricFactory:
	def __init__(self):
		self.dict = {'cluster_number': ClusterNumberMetric,
		             'Dlimit': DlimitMetric,
		             'total_area': TotalAreaMetric,
		             'total_perimeter': TotalPerimeterMetric,
		             'distance_matrix': DistanceMatrixMetric,
		             'hindex': HindexMetric,
		             'area_ratio': AreaRatioMetric,
		             'area_ratio_cell': AreaRatioCellMetric,
		             'minimum_cluster_distance': MinimumClusterDistanceMetric,
		             'clusters_at_distance': ClustersAtDistanceMetric,
		             'clusters_at_percent_distance': ClustersAtPercentDistanceMetric,
		             'distance_matrix_mean': DistanceMatrixMediaMetric,
		             'distance_matrix_sum': DistanceMatrixSumMetric,
		             }

	def produce(self, metric: str):
		assert metric in list(self.dict.keys()), "Unknown metric {}".format(metric)
		return self.dict[metric]()


class ProcessMetricFactory:
	"""
	A factory that generates metrics that are calculated over all the iterations.
	"""
	def __init__(self):
		self.dict = {'xy': XYMetric,
		             'total_sum': TotalClusterSumMetric,
		             'total_nr_sum': TotalNRClusterSumMetric,
		             'max_variation': MaxClusterVariationMetric,
		             'iter_max_variation': IterMaxClusterVariationMetric,
		             'clusters_reduction_distance': ClustersReductionMetric
		             }

	def produce(self, metric: str):
		assert metric in list(self.dict.keys()), "Unknown metric {}".format(metric)
		return self.dict[metric]()


class Metric:
	def __init__(self, name: str='generic'):
		if not isinstance(name, str):
			raise TypeError
		self.name = name

	def calculate(self, collection: Collection, **args):
		return self._calculate(collection, **args)  # **args

	def _calculate(self, collection, **args):
		return 0


class ClusterNumberMetric(Metric):
	def __init__(self, name: str='cluster_number'):
		Metric.__init__(self, name)

	def _calculate(self, collection: Collection, **args):
		if not isinstance(collection, Collection):
			raise TypeError
		return len(collection)


class DlimitMetric(Metric):
	def __init__(self, name: str='Dlimit'):
		Metric.__init__(self, name)

	def _calculate(self, collection: Collection, **args):
		# Works well
		if not isinstance(collection, Collection):
			raise TypeError
		if not isinstance(collection.class_type, Footprint.__class__):
			raise AttributeError
		min_dist = 0
		for i, element in enumerate(collection.collection):
			max_dist = 10000000  # distance between the closest footprints
			for j, element1 in enumerate(collection.collection):
				if j != i:
					max_dist = min(max_dist, element.polygon.distance(element1.polygon))
			if len(collection) > 1:
				min_dist = max(min_dist, max_dist)
		return min_dist / 2


class MinimumClusterDistanceMetric(Metric):
	def __init__(self, name: str='minimum_cluster_distance'):
		Metric.__init__(self, name)

	def _calculate(self, collection: Collection, **args):

		if not isinstance(collection, Collection):
			raise TypeError
		if not isinstance(collection.class_type, Footprint.__class__):
			raise AttributeError

		min_dist = 10000000
		for i, element in enumerate(collection.collection):
			for j, element1 in enumerate(collection.collection):
				if j > i:
					min_dist = min(min_dist, element.polygon.distance(
						element1.polygon))
		if min_dist == 10000000:
			min_dist = 0
		return min_dist


class TotalAreaMetric(Metric):
	def __init__(self, name: str='total_area'):
		Metric.__init__(self, name)

	def _calculate(self, collection: Collection, **args):
		if not isinstance(collection.class_type, Footprint.__class__):
			raise AttributeError
		hull = args['hull']
		area = 0
		for footprint in collection:
			area += footprint.polygon.intersection(hull).area
		return area


class TotalPerimeterMetric(Metric):
	def __init__(self, name: str='total_perimeter'):
		Metric.__init__(self, name)

	def _calculate(self, collection: Collection, **args):
		if not isinstance(collection.class_type, Footprint.__class__):
			raise AttributeError
		perimeter = 0
		for footprint in collection:
			perimeter += footprint.polygon.length
		return perimeter


class DistanceMatrixMetric(Metric):
	def __init__(self, name: str='distance_matrix'):
		Metric.__init__(self, name)

	def _calculate(self, collection: Collection, **args):
		if not isinstance(collection.class_type, Footprint.__class__):
			raise AttributeError
		distance_matrix = np.zeros((len(collection), len(collection)))
		for i, footprint in enumerate(collection.collection):
			for j, footprint1 in enumerate(collection.collection):
				if j > i:
					distance_matrix[i][j] = footprint.polygon.centroid.distance(footprint1.polygon.centroid)

		return distance_matrix.tolist()


class DistanceMatrixSumMetric(Metric):
	def __init__(self, name: str='distance_matrix_sum'):
		Metric.__init__(self, name)

	def _calculate(self, collection: Collection, **args):
		if not isinstance(collection.class_type, Footprint.__class__):
			raise AttributeError
		distance_matrix = np.zeros((len(collection), len(collection)))
		for i, footprint in enumerate(collection.collection):
			for j, footprint1 in enumerate(collection.collection):
				if j > i:
					distance_matrix[i][j] = footprint.polygon.centroid.distance(footprint1.polygon.centroid)

		return np.sum(distance_matrix)


class DistanceMatrixMediaMetric(Metric):
	def __init__(self, name: str='distance_matrix_mean'):
		Metric.__init__(self, name)

	def _calculate(self, collection: Collection, **args):
		if not isinstance(collection.class_type, Footprint.__class__):
			raise AttributeError
		distance_matrix = np.zeros((len(collection), len(collection)))
		for i, footprint in enumerate(collection.collection):
			for j, footprint1 in enumerate(collection.collection):
				if j > i:
					distance_matrix[i][j] = footprint.polygon.centroid.distance(footprint1.polygon.centroid)

		return np.mean(distance_matrix)


class HindexMetric(Metric):
	def __init__(self, name: str='hindex'):
		Metric.__init__(self, name)

	def _calculate(self, collection: Collection, **args):
		if not isinstance(collection.class_type, Footprint.__class__):
			raise AttributeError
		initial_collection = args['initial_collection']
		result = {}
		for i, footprint in enumerate(collection.collection):
			result[i] = 0
			for footprint1 in initial_collection:
				if footprint.polygon.intersects(footprint1.polygon) or \
						footprint1.polygon.within(footprint.polygon):
					result[i] += 1

		# result = {cluster1: n elements, cluster2: n elements}
		values = np.array(list(result.values()))
		values = np.array(np.unique(values, return_counts=True))[:, ::-1]
		for v in values[0]:
			if v <= np.sum(values[1][:list(values[0]).index(v)]):
				return v
		return 1


class AreaRatioMetric(Metric):
	def __init__(self, name: str='area_ratio'):
		Metric.__init__(self, name)

	def _calculate(self, collection: Collection, **args):
		if not isinstance(collection.class_type, Footprint.__class__):
			raise AttributeError
		result = {}
		# _hull = MultiPolygon([x.polygon for x in collection]).convex_hull
		hull = args['hull']

		for i, footprint in enumerate(collection.collection):
			result[i] = footprint.polygon.intersection(hull).area / hull.area
		return np.sum(list(result.values()))


class AreaRatioCellMetric(Metric):
	def __init__(self, name: str='area_ratio_cell'):
		Metric.__init__(self, name)

	def _calculate(self, collection: Collection, **args):
		if not isinstance(collection.class_type, Footprint.__class__):
			raise AttributeError
		result = {}
		# _hull = MultiPolygon([x.polygon for x in collection]).convex_hull
		if 'sample' in list(args.keys()):
			hull = args['sample']
		else:
			hull = args['hull']

		for i, footprint in enumerate(collection.collection):
			result[i] = footprint.polygon.intersection(hull).area / hull.area
		return np.sum(list(result.values()))


class ClustersAtDistanceMetric(Metric):
	def __init__(self, name: str='clusters_at_distance'):
		Metric.__init__(self, name)
		self.distance = 5

	def _calculate(self, collection: Collection, **args):
		if not isinstance(collection.class_type, Footprint.__class__):
			raise AttributeError
		result = 0
		for i, footprint in enumerate(collection.collection):
			for j, footprint1 in enumerate(collection.collection):
				if j > i:
					if round(footprint.polygon.distance(footprint1.polygon)) == self.distance:
						result += 1
		return result


class ClustersAtPercentDistanceMetric(Metric):
	def __init__(self, name: str='clusters_at_percent_distance'):
		Metric.__init__(self, name)
		self.percent = 0.25

	def _calculate(self, collection: Collection, **args):
		if not isinstance(collection.class_type, Footprint.__class__):
			raise AttributeError
		result = 0
		distance = DlimitMetric().calculate(args['initial_collection'])
		for i, footprint in enumerate(collection.collection):
			for j, footprint1 in enumerate(collection.collection):
				if j > i:
					if round(footprint.polygon.distance(footprint1.polygon)) == self.percent * distance:
						result += 1
		return result


class CMetric(Metric):
	def __init__(self, name:str = 'generic_c_metric'):
		Metric.__init__(self, name)

	def calculate(self, result: dict, **args):
		return self._calculate(result, **args)

	def _calculate(self, result: dict, **args):
		_result = 0
		for iter, values in result.items():
			_result += self._get(iter, values, args['field'])
		return _result

	def _get(self, iter, values, field):
		return 0


class XYMetric(CMetric):
	def __init__(self, name: str='xy'):
		CMetric.__init__(self, name)

	def _calculate(self, result: dict, **args):
		_result = 0
		for iter, values in result.items():
			_result += self._get(iter, values, args['field'])
			if _result > 0:
				return _result
		return _result

	def _get(self, iter, values, field):
		"""
		:param iter:
		:param values:
		:param field: json field to take the values from
		:return:
		"""
		if int(iter) == int(values[field]):
			return iter
		elif int(iter) < int(values[field]):
			return 0
		else:
			return int(iter) - 1


class TotalClusterSumMetric(CMetric):
	def __init__(self, name: str='total_sum'):
		CMetric.__init__(self, name)

	def _get(self, iter, values, field):
		return int(values[field])


class TotalNRClusterSumMetric(CMetric):
	def __init__(self, name: str='total_nr_sum'):
		CMetric.__init__(self, name)

	def _calculate(self, result: dict, **args):
		_result = 0
		_prev_values = 0
		for iter, values in result.items():
			if self._get(iter, values, args['field']) != _prev_values:
				_result += self._get(iter, values, args['field'])
			_prev_values = values
		return _result

	def _get(self, iter, values, field):
		return int(values[field])


class MaxClusterVariationMetric(CMetric):
	def __init__(self, name: str='max_variation'):
		CMetric.__init__(self, name)

	def _calculate(self, result: dict, **args):
		_result = 0
		_prev_values = 0
		for iter, values in result.items():
			if int(iter) > 0:
				_result = max(_result, self._get(_prev_values, values, args['field']))
			_prev_values = values
		return _result

	def _get(self, prev_values, values, field):
		return int(prev_values[field]) - int(values[field])


class IterMaxClusterVariationMetric(CMetric):
	def __init__(self, name: str='iter_max_variation'):
		CMetric.__init__(self, name)

	def _calculate(self, result: dict, **args):
		_result = []
		_prev_values = 0
		iter = 0

		for iter, values in result.items():
			if int(iter) > 0:
				_result.append(self._get(_prev_values, values, args['field']))
			_prev_values = values
		return list(range(int(iter) + 1))[_result.index(max(_result))]

	def _get(self, prev_values, values, field):
		return int(prev_values[field]) - int(values[field])


class ClustersReductionMetric(CMetric):
	def __init__(self, name: str='clusters_reduction_distance'):
		CMetric.__init__(self, name)
		self.percent = 0.5

	def _calculate(self, result: dict, **args):
		_result =[]
		_prev_values = 0
		for iter, values in result.items():
			if int(iter) > 0:
				if self._get(_prev_values, values, args['field']):
					_result.append(iter)
			_prev_values = values
		return _result

	def _get(self, prev_values, values, field):
		diff = int(prev_values[field]) - int(values[field])
		return diff >= prev_values[field] * self.percent


class Calculator:
	def __init__(self, metrics=[]):
		self.metrics = metrics
		self.result = {}

	def calculate(self, polygon1, polygon2):
		for metric in self.metrics:
			self.result[metric.name] = metric.calculate(polygon1, polygon2)
		return self.result




