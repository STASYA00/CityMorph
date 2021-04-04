import json
import pandas as pd
import sys

sys.path.append('scripts/')
from polygon import Collection, Footprint


class Writer:
	"""
	Class that stores smart label values per instance
	"""
	def __init__(self, filename):
		"""
		Class initialization.
		:param filename: name of the file to store the data, str
		"""
		self.filename = filename
		self.content = {}

	def add(self, instance, result):
		"""
		Function that adds an instance with its smart labels to the collection
		:param instance: name of instance, str
		:param result: smart labels, dict {label_name: label_value}
		:return:
		"""
		self.content[instance] = result

	def get_instances(self) -> list:
		"""
		Function that gets the instances that already exist in the file
		:return: existing instances, list
		"""
		return list(self.content.keys())

	def reset(self):
		"""
		Function that resets the file to an empty state.
		:return:
		"""
		del self.content
		self.content = {}

	def save(self):
		"""
		Function that saves all the smart labels in the class to a local file
		TODO: add saving to AWS based on AWS_SAVE in config
		:return:
		"""
		with open(self.filename, "w") as f:
			json.dump(self.content, f)


class JsonWriter(Writer):
	"""
	Class that saves results in json format.
	"""
	def __init__(self, filename='test'):
		Writer.__init__(self, filename)
		if not self.filename.endswith('.json'):
			self.filename += '.json'
		# with open(self.filename, 'r') as f:
		# 	self.content = json.load(f)
		self.content = {}

	def save(self):
		"""
		Function that saves the writer's content to local system in json format.
		:return:
		"""
		with open(self.filename, 'a') as json_file:
			json.dump(self.content, json_file)


class CsvWriter:
	def __init__(self, features, name='result'):
		assert isinstance(name, str), "Expected name to be str, got {}".format(name)

		self.name = name
		self.features = features
		if self.name + '.csv' in os.listdir():
			self.csv = pd.read_csv(self.name + '.csv', index_col=0)
			self.csv = self.csv.to_dict(orient='list')
		else:
			self.csv = {}
			self.reset()
			df = pd.DataFrame(self.csv)
			df.to_csv(self.name + '.csv', mode='a')
			print('csv saved as {}.csv'.format(self.name))

	def add(self, instance, result):
		if self._check(result):
			for _feature in list(result.keys()):
				if _feature not in list(self.csv.keys()):
					return ValueError
			if isinstance(instance, str):
				if instance not in self.csv['name']:
					self.csv['name'].append(instance)
					for feature in list(self.csv.keys()):
						if feature != 'name':
							if feature in list(result.keys()):
								self.csv[feature].append(result[feature])
							else:
								self.csv[feature].append(0)
			else:
				return ValueError

	def _check(self, result):
		return len(list(result.keys())) == len(self.features)

	def save(self):
		df = pd.DataFrame(self.csv)
		df.to_csv(self.name + '.csv', mode='a', header=False)

	def reset(self):
		self.csv = {}
		self.csv['iter'] = []
		for feature in self.features:
			self.csv[feature] = []


class ShpWriter:
	def __init__(self, name='result'):
		self.name = name

	def save(self, collection):
		if not isinstance(collection, Collection):
			print('Expected Collection, got {}'.format(collection))
			raise TypeError
		if not isinstance(collection.class_type, Footprint.__class__):
			print('Collection should be made of Footprints, got {}'.format(collection.class_type))
			raise AttributeError
		r = []
		for f in collection:
			r.append(f.polygon)
		dict = {'name': [0 for x in r], 'geometry': r}
		df = gpd.GeoDataFrame(dict)
		df.to_file('{}.shp'.format(self.name))