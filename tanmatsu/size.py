import fractions


class FixedInteger():
	"""
	Resolve to a fixed size.
	
	:param size: A size, in rows/columns.
	:paramtype size: int
	"""
	
	def __init__(self, size: int):
		self.size = size


class Fraction():
	"""
	Resolve to a fraction of the parent's available space, after subtracting
	space taken up by any :class:`FixedInteger` sizes.
	
	:param numerator: Numerator of the fraction.
	:paramtype numerator: int
	
	:param denominator: Denominator of the fraction.
	:paramtype denominator: int
	"""
	
	def __init__(self, numerator, denominator):
		self.fraction = fractions.Fraction(numerator, denominator)


class Auto():
	"""
	Resolve to a proportion of the parent's available space, divided
	up equally amongst all :class:`Auto`s.
	"""
	def __init__(self):
		pass


# class Clamp():
# 	"""
# 	Resolve to the parent's requested size, as long as it is between a set
# 	minimum and maximum. Otherwise, resolve to a percentage of the parent's
# 	size, and clamp it between said minimum and maximum.
	
# 	:param minv: The minimum size that this function will resolve to.
# 	:paramtype minv: int
	
# 	:param actual: The percentage of the parent's size that this function
# 	               will resolve to, assuming the parent's requested size
# 	               is outside the bounds of the minimum and maximum size.
# 	:paramtype actual: int
	
# 	:param maxv: The maximum size that this function will resolve to.
# 	:paramtype maxv: int
# 	"""
# 	def __init__(self, minv: int, percent: Fraction, maxv: int):
# 		self.minv = minv
# 		self.percent = percent
# 		self.maxv = maxv
	
# 	def resolve(self, parent_size: int, requested_size) -> int:
# 		if (
# 			requested_size >= self.minv and\
# 			requested_size <= self.maxv
# 		):
# 			return requested_size
		
# 		clamped = floor(self.percent * parent_size)
# 		clamped = max(self.minv, clamped)
# 		clamped = min(self.maxv, clamped)
		
# 		return clamped
