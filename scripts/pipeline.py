import argparse
import geopandas as gpd
import pandas as pd
from shapely.geometry import MultiPolygon
import sys
import textwrap

sys.path.append('scripts/')
from config import METRICS, CANVAS, PROCESS_METRICS
from grid import Grid, CellCalculator
from metrics import Metric, CMetric, ClusterNumberMetric, MinimumClusterDistanceMetric, \
	MetricFactory, ProcessMetricFactory
from polygon import Reader, Collection, Footprint, Iteration, Uniter, Shifter
from visualizer import Visualizer
from writer import JsonWriter, CsvWriter


class Pipeline:
	def __init__(self):
		self.name = 'generic'

	def run(self, **args):
		return self._run()

	def _run(self, **args):
		return self.name


class CollectionPipeline(Pipeline):
	"""
	Pipeline that produces a collection from a given shapefile name.
	Returns a new collection shifted to (0, 0) as bottom left
	"""
	# Runs well
	def __init__(self, filename):
		Pipeline.__init__(self)
		self.filename = filename
		self.reader = Reader()

	# def _run(self):
	# 	df = self.reader.read(self.filename)
	# 	_collection = Collection(Footprint)
	# 	collection = Collection(Footprint)
	# 	for geometry in df:
	# 		_collection.add(Footprint(geometry))
	# 	del df
	# 	for element in _collection:
	# 		collection = Uniter().make(collection, element)
	# 	del _collection
	# 	return Shifter().make(collection)

	def _run(self):
		df = self.reader.read(self.filename)
		collection = Collection(Footprint)
		for geometry in df:
			collection = Uniter().make(collection, Footprint(geometry))
		del df
		return Shifter().make(collection)


class MetricsPipeline(Pipeline):
	"""
	Pipeline that calculates metrics for a particular collection.
	Returns dictionary of metrics calculated for a given collection.
	"""
	def __init__(self, filename):
		Pipeline.__init__(self)
		self.filename = filename
		self.metric_collection = Collection(Metric)
		for metric in METRICS:
			self.metric_collection.add(MetricFactory().produce(metric))
		print('metrics ready')

	def run(self, collection=None, **args):
		return self._run(collection, **args)

	def _run(self, collection, **args):
		if collection is None:
			collection = CollectionPipeline(self.filename).run()
		result = {}

		for metric in self.metric_collection:
			result[metric.name] = metric.calculate(collection, **args)

		return result


class ProcessMetricsPipeline(Pipeline):
	"""
	Pipeline that calculates metrics for a particular collection.
	Returns dictionary of metrics calculated for a given collection.
	"""
	def __init__(self, filename):
		Pipeline.__init__(self)
		self.filename = filename
		self.metric_collection = Collection(Metric)
		for metric in PROCESS_METRICS:
			self.metric_collection.add(ProcessMetricFactory().produce(metric))
		print('metrics ready')

	def run(self, values: dict, **args):
		return self._run(values, **args)

	def _run(self, values, **args):
		result = {}
		for field in ['cluster_number', 'total_area']:
			for metric in self.metric_collection:
				result['{}_{}'.format(field, metric.name)] = metric.calculate(values, field=field)
		return result


class IterPipeline(Pipeline):
	"""
	Pipeline that makes one iteration of growth on a given value.
	Returns a new Collection.
	"""
	def __init__(self, filename, value=0):
		Pipeline.__init__(self)
		self.filename = filename
		self.value = value

	def run(self, collection=None):
		return self._run(collection)

	def _run(self, collection):
		if collection is None:
			collection = CollectionPipeline(self.filename).run()
		return Iteration(collection, self.value).make()


class GridPipeline(Pipeline):
	"""
	Pipeline that makes one iteration of growth on a given value.
	Returns a new Collection.
	"""
	def __init__(self, filename, value=0):
		Pipeline.__init__(self)
		self.filename = filename
		self.value = value

	def run(self, shapefile=None):
		return self._run(shapefile)

	def _run(self, shapefile):
		_grid = Grid(shapefile)
		_cellcalc = CellCalculator(_grid)
		buildings = Reader().read(self.filename)
		for i in range(len(_grid.grid)):
			_collection, _cell = _cellcalc.get(buildings, i)
			if len(_collection) > 0:
				print('LEN', len(_collection))
				MainPipeline(filename='{}'.format(i)).run(collection =_collection, sample=_cell)
				print('Iteration {} finished executing'.format(i))


class MainPipeline(Pipeline):
	def __init__(self, filename, value=0):
		Pipeline.__init__(self)
		self.filename = filename
		self.value = value

	def run(self, collection=None,**args):
		return self._run(collection, **args)

	def _run(self, collection, **args):
		# print(collection)
		# if len(collection) < 1:
		# 	collection = CollectionPipeline(self.filename).run()
		sample = None
		if 'sample' in list(args.keys()):
			sample = args['sample']
		hull = MultiPolygon(
			[x.polygon for x in collection.collection]).convex_hull
		m_pipe = MetricsPipeline(self.filename)
		result = m_pipe.run(collection, initial_collection=collection,
		                    hull=hull, sample=sample)

		writer = CsvWriter(filename='result/' + self.filename.split('.')[0], features=METRICS)
		writer.add("{}".format(0), result)

		# v = Visualizer(collection, name='{}_iter'.format(n)).visualize()
		n_clusters = 100
		i = 1
		while n_clusters != 1:
			_collection = IterPipeline(self.filename, i).run(collection)
			result = m_pipe.run(_collection, initial_collection=collection,
			                    hull=hull)
			n_clusters = result['cluster_number']
			print('Number of clusters:    {}'.format(n_clusters))
			writer.add(i, result)
			if self.value:
				v = Visualizer(_collection,
				               name='{}_iter'.format(i)).visualize()
				del v
			del _collection
			del result
			i += 1
		writer.save()
		process_writer = CsvWriter(filename='result/{}_process'.format(self.filename.split('.')[0]),
		                           features=['{}_{}'.format(y, x) for x in
		                                     PROCESS_METRICS for y in
		                                     ['cluster_number', 'total_area']])
		process_pipe = ProcessMetricsPipeline(self.filename).run(writer.content)
		process_writer.add('whole', process_pipe)
		process_writer.save()


class TestPipeline(Pipeline):
	"""
	Pipeline to test different ideas.
	"""
	def __init__(self, filename):
		Pipeline.__init__(self)
		self.filename = filename

	def _run(self):
		collection = CollectionPipeline(self.filename).run()
		print(ClusterNumberMetric().calculate(collection))
		print(MinimumClusterDistanceMetric().calculate(collection))
		new_collection = Iteration(collection, 8).make()
		print(ClusterNumberMetric().calculate(new_collection))
		print(MinimumClusterDistanceMetric().calculate(new_collection))
		return 0


if __name__ == '__main__':
	parser = argparse.ArgumentParser(
		formatter_class=argparse.RawDescriptionHelpFormatter,
		description=textwrap.dedent('''\
				USAGE: python pipeline.py area.shp

				------------------------------------------------------------------------

				This is an algorithm that runs the metrics calculation for a 
				chosen area.

				------------------------------------------------------------------------

				'''), epilog=textwrap.dedent('''\
				The algorithm will be updated with the changes made in the strategy.
				'''))

	parser.add_argument('filename', type=str,
	                    help='path to the shapefile to inspect', default=None)

	############################################################################

	args = parser.parse_args()

	FILE = args.filename

	collection = CollectionPipeline(FILE).run()
	m_pipe = MetricsPipeline(FILE)
	result = m_pipe.run(collection, initial_collection=collection)

	writer = CsvWriter(filename=FILE.split('.')[0])
	writer.add("{}".format(0), result)

	# v = Visualizer(collection, name='{}_iter'.format(n)).visualize()
	for i in range(1, 14):
		_collection = IterPipeline(FILE, i).run(collection)
		result = m_pipe.run(_collection, initial_collection=collection)
		writer.add(i, result)
		# v = Visualizer(_collection, name='{}_iter'.format(i)).visualize()
		# del v
		del _collection
		del result
	process_pipe = ProcessMetricsPipeline(FILE).run(writer.content)
	writer.add('whole', process_pipe)
	writer.save()


