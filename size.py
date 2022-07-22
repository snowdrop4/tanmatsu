class SizeResolver():
	def __init__(self):
		pass
	
	def min(self, parent_dimension):
		raise NotImplementedError
	
	def max(self, parent_dimension):
		raise NotImplementedError
	
	def resolve(self, parent_dimension, requested_dimension):
		raise NotImplementedError


class ParentRequested:
	def __init__(self):
		pass
	
	def min(self, parent_dimension):
		return 1
	
	def max(self, parent_dimension):
		return parent_dimension
	
	def resolve(self, parent_dimension, requested_dimension):
		return requested_dimension


class FixedInteger:
	def __init__(self, actual):
		self.actual = actual
	
	def min(self, parent_dimension):
		return self.actual
	
	def max(self, parent_dimension):
		return self.actual
	
	def resolve(self, parent_dimension, requested_dimension):
		return self.actual


class ParentPercent:
	def __init__(self, actual):
		self.actual = actual
	
	def min(self, parent_dimension):
		return int((self.actual * parent_dimension) / 100)
	
	def max(self, parent_dimension):
		return int((self.actual * parent_dimension) / 100)
	
	def resolve(self, parent_dimension, requested_dimension):
		return int((self.actual * parent_dimension) / 100)


class Clamp:
	def __init__(self, minv, actual, maxv):
		self.min    = minv
		self.actual = actual
		self.max    = maxv
	
	def min(self, parent_dimension):
		return self.min
	
	def max(self, parent_dimension):
		return self.max
	
	def resolve(self, parent_dimension, requested_dimension):
		if (requested_dimension >= self.min) and\
		   (requested_dimension <= self.max):
			return requested_dimension
		
		percent_of_parent = int((self.actual * parent_dimension) / 100)
		
		clamped = percent_of_parent
		clamped = max(self.min, clamped)
		clamped = min(self.max, clamped)
		
		return clamped
