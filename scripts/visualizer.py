import cv2
import geopandas as gpd
import math
import numpy as np
import os
from shapely.affinity import translate, scale
from shapely.geometry import Point, Polygon, MultiPolygon, MultiPoint, LineString,\
	GeometryCollection
from shapely.validation import explain_validity
from shapely.ops import unary_union
import sys

sys.path.append('scripts/')
from config import CANVAS
from polygon import Scaler, Shifter
from utils import polygon_to_contour, polygon_to_internal_contour


class Visualizer:
	def __init__(self, collection, name='result'):
		self.collection = collection
		self.canvas = CANVAS
		assert isinstance(name, str), "Expected name to be str, got {}".format(type(name))
		self.name = name

	def visualize(self):
		return self._visualize()

	def _visualize(self):
		self.collection = Scaler().make(self.collection, self.canvas)
		# limits = Shifter().get_max(self.collection)
		# base = np.zeros((math.ceil(limits[1]), math.ceil(limits[0])))
		base = np.zeros(self.canvas)
		contours, holes = [], []
		for footprint in self.collection:
			contours.append(polygon_to_contour(footprint.polygon))
			holes.append(polygon_to_internal_contour(footprint.polygon))
		for c in contours:
			base = cv2.drawContours(base, np.array([c]),
			                        -1, (255, 255, 255), -1)
		for hole_group in holes:
			for hole in hole_group:
				base = cv2.drawContours(base, np.array([hole]), -1, (0, 0, 0), -1)
		if not 'vis' in os.listdir():
			os.mkdir('vis')
		cv2.imwrite('vis/{}.png'.format(self.name), base)
		return base

