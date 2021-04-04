import argparse
import sys
import textwrap

sys.path.append('scripts/')
from config import METRICS, CANVAS, PROCESS_METRICS
from metrics import Metric, CMetric, ClusterNumberMetric, MinimumClusterDistanceMetric, \
	MetricFactory, ProcessMetricFactory
from pipeline import *
from polygon import Reader, Collection, Footprint, Iteration, Uniter, Shifter
from visualizer import Visualizer
from writer import JsonWriter


if __name__ == '__main__':
	parser = argparse.ArgumentParser(
		formatter_class=argparse.RawDescriptionHelpFormatter,
		description=textwrap.dedent('''\
				USAGE: python run.py area.shp

				------------------------------------------------------------------------

				This is an algorithm that runs the metrics calculation for a 
				chosen area.

				------------------------------------------------------------------------

				'''), epilog=textwrap.dedent('''\
				The algorithm will be updated with the changes made in the strategy.
				'''))

	parser.add_argument('filename', type=str,
	                    help='path to the shapefile to inspect', default=None)
	parser.add_argument("--vis", action="store_true", help='visualize images')

	############################################################################

	args = parser.parse_args()

	FILE = args.filename

	VIS = args.vis

	collection = CollectionPipeline(FILE).run()
	m_pipe = MetricsPipeline(FILE)
	result = m_pipe.run(collection, initial_collection=collection)

	writer = JsonWriter(filename=FILE.split('.')[0])
	writer.add("{}".format(0), result)

	# v = Visualizer(collection, name='{}_iter'.format(n)).visualize()
	n_clusters = 100
	i = 1
	while n_clusters != 1:
		_collection = IterPipeline(FILE, i).run(collection)
		result = m_pipe.run(_collection, initial_collection=collection)
		n_clusters = result['cluster_number']
		print('Number of clusters:    {}'.format(n_clusters))
		writer.add(i, result)
		if VIS:
			v = Visualizer(_collection, name='{}_iter'.format(i)).visualize()
			del v
		del _collection
		del result
		i += 1
	process_pipe = ProcessMetricsPipeline(FILE).run(writer.content)
	writer.add('whole', process_pipe)
	writer.save()