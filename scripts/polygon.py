import geopandas as gpd
import numpy as np
from shapely.affinity import translate, scale
from shapely.geometry import Point, Polygon, MultiPolygon, MultiPoint, LineString,\
	GeometryCollection
import sys

sys.path.append('scripts/')
from config import GEOMETRY_TYPE
from utils import geom_check, validate_polygon

# from metrics import *


# IDEA: put number of initial elements inside each cluster into the collection
# and update this value as the cluster grows

class Collection:
	# TESTED: collection_test.py
	def __init__(self, class_type):
		self.collection = []
		self.class_type = class_type

	def __iter__(self):
		return Iterator(self.collection, self.class_type)

	def __len__(self):
		return len(self.collection)

	def add(self, obj):
		if obj.__class__ == type:
			if issubclass(obj, self.class_type):
				self.collection.append(obj)
		else:
			if isinstance(obj, self.class_type):
				self.collection.append(obj)
			elif issubclass(obj.__class__, self.class_type):
				self.collection.append(obj)
			elif isinstance(obj, list):
				for _object in obj:
					assert isinstance(_object, self.class_type), "Expected a list of {}," \
													" got {}".format(self.class_type, type(_object))
					self.collection.append(_object)
			else:
				print(type(obj))
				raise TypeError


class Iterator:
	def __init__(self, collection, class_type):
		self.collection = collection
		self.index = 0
		self.class_type = class_type
		assert isinstance(self.collection, list), "Wrong iteration input."

	def __next__(self):
		try:
			_object = self.collection[self.index]
		except IndexError:
			raise StopIteration()
		self.index += 1
		assert isinstance(_object, self.class_type)
		return _object

	def __iter__(self):
		return self

	def has_next(self):
		return self.index < len(self.collection)


class Reader:
	def __init__(self):
		self.n = 0

	def read(self, shapefile):
		assert isinstance(shapefile, str)
		df = gpd.read_file(shapefile)
		df = geom_check(df, GEOMETRY_TYPE)
		return [x for x in df['geometry']]


class Footprint:
	"""
	Class that represents a building footprint.
	TESTED: footprint_test.py
	"""
	def __init__(self, polygon):
		"""
		:param polygon: building footprint, Polygon
		"""
		if not (isinstance(polygon, Polygon) or isinstance(polygon, MultiPolygon)):
			print('Expected Polygon type, got {}'.format(type(polygon)))
			raise TypeError
		self.polygon = validate_polygon(polygon)

	def grow(self, value):
		"""
		Function that increases the footprint in size by given offset
		:param value: offset value, int or float
		:return: new footprint with offset polygon, Footprint
		"""
		return Footprint(self.polygon.buffer(value))


class Uniter:
	def __init__(self):
		self.name = 'uniter'

	def make(self, collection, footprint):
		new = Collection(Footprint)
		for element1 in collection:
			if element1.polygon.intersects(footprint.polygon):
				footprint = Footprint(element1.polygon.union(footprint.polygon))
			else:
				new.add(element1)
		new.add(footprint)
		return new


class Shifter:
	def __init__(self):
		self.name = 'shifter'

	def make(self, collection):
		new = Collection(Footprint)
		if len(collection) > 0:
			min_x, min_y = self.get_min(collection)
			for footprint in collection:
				new.add(Footprint(translate(footprint.polygon, xoff=-min_x, yoff=-min_y)))
		return new

	def get_min(self, collection):
		min_x, min_y = 10 ** 10, 10 ** 10
		for footprint in collection:
			coords = np.array([[x[0], x[1]] for x in footprint.polygon.exterior.coords])
			min_x = np.min((np.min(coords[:, 0]), min_x))
			min_y = np.min((np.min(coords[:, 1]), min_y))
		return min_x, min_y

	def get_max(self, collection):
		max_x, max_y = -10 ** 10, -10 ** 10
		for footprint in collection:
			coords = np.array([[x[0], x[1]] for x in footprint.polygon.exterior.coords])
			max_x = np.max((np.max(coords[:, 0]), max_x))
			max_y = np.max((np.max(coords[:, 1]), max_y))
		return max_x, max_y


class Scaler:
	def __init__(self):
		self.name = 'scaler'

	def make(self, collection, canvas):
		# Works
		init = Shifter().get_min(collection)
		if not np.sum(init) == 0:
			collection = Shifter().make(collection)
		limits = Shifter().get_max(collection)
		pol_scale = np.max((limits[0] / canvas[1], limits[1] / canvas[0]))
		new = Collection(Footprint)
		for footprint in collection:
			new.add(Footprint(scale(footprint.polygon, xfact=1 / pol_scale,
			                        yfact=1 / pol_scale, origin=(0, 0))))
		return new


class Iteration:
	"""
	Class that represents one algorithm iteration.
	"""
	def __init__(self, collection, value):
		"""
		:param collection: collection of Footprints, Collection class
		:param value: value of buffer, int or float
		"""
		if not (isinstance(value, int) or isinstance(value, float)):
			print("expected value to be numeric, got {}".format(type(value)))
			raise TypeError
		if not isinstance(collection, Collection):
			print("Expected collection to be Collection, got {}".format(type(collection)))
			raise TypeError
		if not isinstance(collection.class_type, Footprint.__class__):
			print('Collection should be made of Footprints, got {}'.format(collection.class_type))
			raise AttributeError

		self.value = value
		# self.calculator = Calculator()
		self.collection = collection
		self.new_collection = Collection(Footprint)

	def make(self):
		return self._make()

	def _calculate_metrics(self, polygon1, polygon2):
		# See what exactly metric needs to calculate something, maybe all the polygons
		return self.calculator.calculate(polygon1, polygon2)

	def _make(self):
		for element in self.collection:
			self.new_collection = Uniter().make(self.new_collection,
			                                    element.grow(self.value))
		# return self._calculate_metrics(polygon1, polygon2)
		del self.collection
		return self.new_collection
