from shapely.geometry import Polygon
import geopandas as gpd
import sys

sys.path.append('scripts/')
from polygon import Reader, Collection, Footprint, Uniter


class Grid:
	def __init__(self, filename):
		self.filename = filename
		self.grid = self._load()
		self.width = self.grid[0].bounds[2] - self.grid[0].bounds[0]
		self.height = self.grid[0].bounds[3] - self.grid[0].bounds[1]

	def _load(self):
		return Reader().read(self.filename)

class CellCalculator:
	def __init__(self, grid):
		self.grid = grid
		self.margin = 10000

	def get(self, collection, cell):
		return self._get(collection, cell)

	def _get(self, dataframe, cell):
		_collection = Collection(Footprint)
		# _p1 = None
		for polygon in dataframe:
			if polygon.centroid.distance(self.grid.grid[cell]) < self.margin: #self.grid.width:
				if polygon.centroid.distance(self.grid.grid[cell]) < self.margin: #self.grid.height:
					if polygon.intersects(self.grid.grid[cell]) or polygon.within(self.grid.grid[cell]):
						# _collection.add(Footprint(polygon))
						# if _p1:
						# _p1 = polygon
						_collection = Uniter().make(_collection, Footprint(polygon))
		return _collection, self.grid.grid[cell]


