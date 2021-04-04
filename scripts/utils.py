import numpy as np
import pandas as pd

from shapely.geometry import Point, Polygon, MultiPolygon
from shapely.validation import explain_validity
from shapely.ops import unary_union


def geom_check(df, dtype):
	_geom_check = [1 if x.geom_type != dtype else 0 for x in df['geometry']]
	if len(np.unique(_geom_check)) > 1:
		df = df.loc[df['geometry'].geom_type == dtype]
	return df


def polygon_to_contour(polygon):
	polygon = validate_polygon(polygon)
	coords = [x for x in polygon.exterior.coords]
	return [[[int(x[0]), int(x[1])]] for x in coords]

def polygon_to_internal_contour(polygon):
	polygon = validate_polygon(polygon)
	holes = []
	for interior in polygon.interiors:
		holes.append([[[int(x[0]), int(x[1])]] for x in interior.coords])

	return holes

def validate_polygon(polygon):
	if polygon.geom_type == 'Polygon':
		n=0
		while not polygon.is_valid:
			n+=0.5
			polygon = polygon.simplify(n)
			if n >= 10:
				break
	elif polygon.geom_type == 'MultiPolygon':
		p1 = polygon.geoms[0]
		for p in polygon.geoms[1:]:
			if p.geom_type == 'Polygon':
				dist = p1.distance(p) + 0.001
				p1 = unary_union([p1.buffer(dist), p.buffer(dist)])
		polygon = p1
	if not polygon.is_valid:
		print(explain_validity(polygon))
	return polygon


