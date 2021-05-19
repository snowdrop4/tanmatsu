class SizeResolver():
	"""
	Abstract base class. Used in :class:`widgets.Widget` and descendants
	for calculating widget size.
	"""
	
	def __init__(self):
		pass
	
	def min(self, parent_size: int) -> int:
		"""
		Return the minimum possible size :meth:`resolve` could resolve to,
		given the parent's size.
		"""
		raise NotImplementedError
	
	def max(self, parent_size: int) -> int:
		"""
		Return the maximum possible size :meth:`resolve` could resolve to,
		given the parent's size.
		"""
		raise NotImplementedError
	
	def resolve(self, parent_size: int, requested_size: int) -> int:
		"""
		Resolve the actual size we request to be allocated by the parent widget,
		given the parent's size and the size the parent requests of us.
		
		We can choose to handshake the parent's requested size or not.
		The parent widget has the final say on how much it actually allocates.
		
		:param parent_size: The size of the parent.
		:param requested_size: The size the parent requests of us.
		"""
		raise NotImplementedError


class ParentRequested(SizeResolver):
	"""Always resolve to the parent's requested size."""
	
	def __init__(self):
		pass
	
	def min(self, parent_size: int) -> int:
		return 1
	
	def max(self, parent_size: int) -> int:
		return parent_size
	
	def resolve(self, parent_size: int, requested_size: int) -> int:
		return requested_size


class FixedInteger(SizeResolver):
	"""Always resolve to a fixed sized."""
	
	def __init__(self, actual: int):
		self.actual = actual
	
	def min(self, parent_size: int) -> int:
		return self.actual
	
	def max(self, parent_size: int) -> int:
		return self.actual
	
	def resolve(self, parent_size: int, requested_size: int) -> int:
		return self.actual


class ParentPercent(SizeResolver):
	"""Resolve to a percent of the parent's size."""
	
	def __init__(self, actual: int):
		self.actual = actual
	
	def min(self, parent_size: int) -> int:
		return int((self.actual * parent_size) / 100)
	
	def max(self, parent_size: int) -> int:
		return int((self.actual * parent_size) / 100)
	
	def resolve(self, parent_size: int, requested_size: int) -> int:
		return int((self.actual * parent_size) / 100)


class Clamp(SizeResolver):
	"""
	Resolve to the parent's requested size, as long as it is between a set
	minimum and maximum. Otherwise, resolve to a percentage of the parent's
	size, and clamp it between said minimum and maximum.
	
	:param minv: The minimum size that this function will resolve to.
	:param actual: The percentage of the parent's size that this function
	  will resolve to, assuming the parent's requested size is outside the
	  bounds of the minimum and maximum size.
	:param maxv: The maximum size that this function will resolve to.
	"""
	
	def __init__(self, minv: int, actual: int, maxv: int):
		self.minv   = minv
		self.actual = actual
		self.maxv   = maxv
	
	def min(self, parent_size: int) -> int:
		return self.minv
	
	def max(self, parent_size: int) -> int:
		return self.maxv
	
	def resolve(self, parent_size: int, requested_size: int) -> int:
		if (
			requested_size >= self.minv and\
			requested_size <= self.maxv
		):
			return requested_size
		
		percent_of_parent = int((self.actual * parent_size) / 100)
		
		clamped = percent_of_parent
		clamped = max(self.minv, clamped)
		clamped = min(self.maxv, clamped)
		
		return clamped