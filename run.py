import argparse
import sys
import textwrap

sys.path.append('scripts/')
from pipeline import *


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
	parser.add_argument('grid', type=str,
	                    help='path to the grid shapefile to inspect', default=None)
	parser.add_argument("--vis", action="store_true", help='visualize images')

	############################################################################

	args = parser.parse_args()

	FILE = args.filename

	GRID = args.grid

	VIS = args.vis

	# pipe = MainPipeline(FILE)
	pipe = GridPipeline(FILE)
	pipe.run(GRID)