class Point():
	"""
	Coordinates on a 2D plane.
	
	:ivar x: `x` coordinate.
	:ivar y: `y` coordinate.
	"""
	
	def __init__(self, x: int, y: int):
		self.x = x
		self.y = y
	
	def set(self, x: int, y: int):
		"""Set the coordinates to `x`, `y`."""
		self.x = x
		self.y = y
	
	def duplicate(self) -> Point:
		"""Return a copy of the coordinates."""
		return Point(self.x, self.y)
	
	def __eq__(self, other: Point) -> bool:
		return self.x == other.x and self.y == other.y
	
	def __str__(self) -> str:
		return f"Point: {self.x}x, {self.y}y"


class Dimensions():
	"""
	Dimensions on a 2D plane.
	
	:ivar w: `w` dimension.
	:ivar h: `h` dimension.
	"""
	
	def __init__(self, w: int, h: int):
		self.w = w
		self.h = h
	
	def set(self, w: int, h: int):
		"""Set the dimensions to `w`, `h`."""
		self.w = w
		self.h = h
	
	def duplicate(self) -> Dimensions:
		"""Return a copy of the dimensions."""
		return Dimensions(self.w, self.h)
	
	def __eq__(self, other: Dimensions) -> bool:
		return self.w == other.w and self.h == other.h
	
	def __str__(self) -> str:
		return f"Dimensions: {self.w}w by {self.h}h"


class Rectangle():
	"""
	Coordinates and dimensions on a 2D plane.
	
	:ivar x: `x` coordinate.
	:ivar y: `y` coordinate.
	:ivar w: `w` dimension.
	:ivar h: `h` dimension.
	"""
	
	def __init__(self, x: int, y: int, w: int, h: int):
		self.x = x
		self.y = y
		self.w = w
		self.h = h
	
	@property
	def x1(self):
		"""Alias of `x`."""
		return self.x
	
	@property
	def y1(self):
		"""Alias of `y`."""
		return self.y
	
	@property
	def x2(self) -> int:
		"""The coordinate at `x + w - 1`. I.e., the far `x` coordinate."""
		return self.x + (self.w - 1)
	
	@property
	def y2(self) -> int:
		"""The coordinate at `y + h - 1`. I.e., the far `y` coordinate."""
		return self.y + (self.h - 1)
	
	def intersects(self, other: Rectangle) -> bool:
		"""Whether this rectangle intersects with rectangle `other`."""
		
		a = self.x1 <= other.x2
		b = self.x2 >= other.x1
		c = self.y1 <= other.y2
		d = self.y2 >= other.y1
		
		return a and b and c and d
	
	def contains(self, other: Point) -> bool:
		"""Whether this rectangle contains point `other`."""
		
		a = self.x <= other.x <= self.x2
		b = self.y <= other.y <= self.y2
		
		return a and b
	
	def overlap_rectangle(self, other: Rectangle) -> Rectangle:
		"""Returns the rectangle that overlaps with this rectangle and rectangle `other`."""
		
		x1 = max(self.x1, other.x1)
		y1 = max(self.y1, other.y1)
		
		x2 = min(self.x2, other.x2)
		y2 = min(self.y2, other.y2)
		
		w = x2 - x1 + 1
		h = y2 - y1 + 1
		
		return Rectangle(x1, y1, w, h)
	
	def duplicate(self) -> Rectangle:
		"""Returns a copy of this rectangle."""
		
		return Rectangle(self.x, self.y, self.w, self.h)
	
	def origin_point(self) -> Point:
		"""Returns the near `x`, `y`. The origin point (top left) of the rectangle."""
		return Point(self.x, self.y)
	
	def end_point(self) -> Point:
		"""Returns the far `x`, `y`. The end point (bottom right) of the rectangle."""
		return Point(self.x2, self.y2)
	
	def dimensions(self) -> Dimensions:
		"""Returns the dimensions of the rectangle."""
		return Dimensions(self.w, self.h)
	
	def __eq__(self, other) -> bool:
		(x, y, w, h) = other
		
		return self.x == other.x\
		   and self.y == other.y\
		   and self.w == other.w\
		   and self.h == other.h
	
	def __str__(self) -> str:
		return f"Rectangle: {self.w}w by {self.h}h at {self.x}x, {self.y}y"
