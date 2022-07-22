from __future__ import annotations


class Point():
	"""
	Coordinates on a 2D plane.
	
	:ivar x: `x` coordinate.
	:vartype x: int
	
	:ivar y: `y` coordinate.
	:vartype y: int
	"""
	
	def __init__(self, x: int, y: int):
		self.x = x
		self.y = y
	
	def set(self, x: int, y: int):
		"""Set the coordinates to `x`, `y`."""
		self.x = x
		self.y = y
	
	def duplicate(self) -> Self:
		"""Returns a copy of the coordinates."""
		return Point(self.x, self.y)
	
	def __eq__(self, other: Point) -> bool:
		"""Whether this point is equal to point `other` (compare-by-value)."""
		return self.x == other.x and self.y == other.y
	
	def __str__(self) -> str:
		"""Returns a string representation of the point."""
		return f"Point: {self.x}x, {self.y}y"


class Dimensions():
	"""
	Dimensions on a 2D plane.
	
	:ivar w: width (`w` dimension).
	:vartype w: int
	
	:ivar h: height (`h` dimension).
	:vartype h: int
	"""
	
	def __init__(self, w: int, h: int):
		self.w = w
		self.h = h
	
	def set(self, w: int, h: int):
		"""Set the dimensions to `w`, `h`."""
		self.w = w
		self.h = h
	
	def duplicate(self) -> Self:
		"""Returns a copy of the dimensions."""
		return Dimensions(self.w, self.h)
	
	def __eq__(self, other: Dimensions) -> bool:
		"""
		Whether the width and height of this dimensions object
		is equal to the width and height of the dimensions object `other`.
		"""
		return self.w == other.w\
		   and self.h == other.h
	
	def __lt__(self, other: Rectangle | Dimensions) -> bool:
		"""
		Whether the width and height of this dimensions object are both
		less than the width and height of object `other`.
		"""
		return self.w < other.w\
		   and self.h < other.h
	
	def __le__(self, other: Rectangle | Dimensions) -> bool:
		"""
		Whether the width and height of this dimensions object are both
		less than or equal to the width and height of object `other`.
		"""
		return self.w <= other.w\
		   and self.h <= other.h
	
	def __gt__(self, other: Rectangle | Dimensions) -> bool:
		"""
		Whether the width and height of this dimensions object are both
		greater than the width and height of object `other`.
		"""
		return self.w > other.w\
		   and self.h > other.h
	
	def __ge__(self, other: Rectangle | Dimensions) -> bool:
		"""
		Whether the width and height of this dimensions object are both
		greater than or equal to the width and height of object `other`.
		"""
		return self.w >= other.w\
		   and self.h >= other.h
	
	def __str__(self) -> str:
		"""Returns a string representation of the dimensions."""
		return f"Dimensions: {self.w}w by {self.h}h"


class Rectangle():
	"""
	Coordinates and dimensions on a 2D plane.
	
	:ivar x: `x` coordinate.
	:vartype x: int
	
	:ivar y: `y` coordinate.
	:vartype y: int
	
	:ivar w: width (`w` dimension).
	:vartype w: int
	
	:ivar h: height (`h` dimension).
	:vartype h: int
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
		return self.x1 <= other.x2\
		   and self.x2 >= other.x1\
		   and self.y1 <= other.y2\
		   and self.y2 >= other.y1
	
	def containsp(self, other: Point) -> bool:
		"""Whether this rectangle contains point `other`."""
		return self.x <= other.x <= self.x2\
		   and self.y <= other.y <= self.y2
	
	def containsr(self, other: Rectangle) -> bool:
		"""Whether this rectangle contains rectangle `other`."""
		return self.x1 <= other.x1\
		   and self.y1 <= other.y1\
		   and self.x2 >= other.x2\
		   and self.y2 >= other.y2
	
	def duplicate(self) -> Self:
		"""Returns a copy of this rectangle."""
		return Rectangle(self.x, self.y, self.w, self.h)
	
	def origin_point(self) -> Point:
		"""
		Returns the near `x`, `y`. In other words, the origin point
		(top left) of the rectangle.
		"""
		return Point(self.x, self.y)
	
	def end_point(self) -> Point:
		"""
		Returns the far `x`, `y`. In other words, the end point
		(bottom right) of the rectangle.
		"""
		return Point(self.x2, self.y2)
	
	def dimensions(self) -> Dimensions:
		"""Returns the dimensions of the rectangle."""
		return Dimensions(self.w, self.h)
	
	def __eq__(self, other: Rectangle) -> bool:
		"""
		Whether this rectangle's position in space and dimensions
		are equal to rectangle `other`.
		"""
		return self.x == other.x\
		   and self.y == other.y\
		   and self.w == other.w\
		   and self.h == other.h
	
	def __lt__(self, other: Rectangle | Dimensions) -> bool:
		"""
		Whether this rectangle's width and height are both
		less than the width and height of object `other`.
		"""
		return self.w < other.w\
		   and self.h < other.h
	
	def __le__(self, other: Rectangle | Dimensions) -> bool:
		"""
		Whether this rectangle's width and height are both
		less than or equal to the width and height of object `other`.
		"""
		return self.w <= other.w\
		   and self.h <= other.h
	
	def __gt__(self, other: Rectangle | Dimensions) -> bool:
		"""
		Whether this rectangle's width and height are both
		greater than the width and height of object `other`.
		"""
		return self.w > other.w\
		   and self.h > other.h
	
	def __gt__(self, other: Rectangle | Dimensions) -> bool:
		"""
		Whether this rectangle's width and height are both
		greater than or equal to the width and height of object `other`.
		"""
		return self.w >= other.w\
		   and self.h >= other.h
	
	def __and__(self, other: Rectangle) -> Rectangle:
		"""
		Returns the rectangle that represents the overlap
		between this rectangle and rectangle `other`.
		"""
		x1 = max(self.x1, other.x1)
		y1 = max(self.y1, other.y1)
		
		x2 = min(self.x2, other.x2)
		y2 = min(self.y2, other.y2)
		
		w = x2 - x1 + 1
		h = y2 - y1 + 1
		
		return Rectangle(x1, y1, w, h)
	
	def __str__(self) -> str:
		"""Returns a string representation of the rectangle."""
		return f"Rectangle: {self.w}w by {self.h}h at {self.x}x, {self.y}y"
