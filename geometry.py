class Point():
	def __init__(self, x, y):
		self.x = x
		self.y = y
	
	def set(self, x, y):
		self.x = x
		self.y = y
	
	def duplicate(self):
		return Point(self.x, self.y)
	
	def __eq__(self, other):
		(x, y) = other
		return self.x == x and self.y == y
	
	def __str__(self):
		return f"Point: {self.x1}x, {self.y1}y"


class Dimensions():
	def __init__(self, w, h):
		self.w = w
		self.h = h
	
	def set(self, w, h):
		self.w = w
		self.h = h
	
	def duplicate(self):
		return Dimensions(self.w, self.h)
	
	def __eq__(self, other):
		(w, h) = other
		return self.w == w and self.h == h
	
	def __str__(self):
		return f"Dimensions: {self.w}w by {self.h}h"


class Rectangle():
	def __init__(self, x, y, w, h):
		self.x1 = x
		self.y1 = y
		self.w = w
		self.h = h
	
	@property
	def x(self):
		return self.x1
	
	@x.setter
	def x(self, v):
		self.x1 = v
	
	@property
	def y(self):
		return self.y1
	
	@y.setter
	def y(self, v):
		self.y1 = v
	
	@property
	def x2(self):
		return self.x1 + (self.w - 1)
	
	@property
	def y2(self):
		return self.y1 + (self.h - 1)
	
	def intersects(self, rectangle):
		a = self.x1 <= rectangle.x2
		b = self.x2 >= rectangle.x1
		c = self.y1 <= rectangle.y2
		d = self.y2 >= rectangle.y1
		
		return a and b and c and d
	
	def contains(self, x, y):
		a = self.x1 <= x <= self.x2
		b = self.y1 <= y <= self.y2
		
		return a and b
	
	def overlap_rectangle(self, other):
		x1 = max(self.x1, other.x1)
		y1 = max(self.y1, other.y1)
		
		x2 = min(self.x2, other.x2)
		y2 = min(self.x2, other.y2)
		
		w = x2 - x1 + 1
		h = y2 - y1 + 1
		
		return Rectangle(x1, y1, w, h)
	
	def duplicate(self):
		return Rectangle(self.x, self.y, self.w, self.h)
	
	def duplicate_origin_point(self):
		return Point(self.x1, self.y1)
	
	def duplicate_end_point(self):
		return Point(self.x2, self.y2)
	
	def duplicate_dimensions(self):
		return Dimensions(self.w, self.h)
	
	def __str__(self):
		return f"Rectangle: {self.w}w by {self.h}h at {self.x1}x, {self.y1}y"
	
	def __eq__(self, other):
		(x, y, w, h) = other
		return self.x == x and self.y == y and self.w == w and self.h == h
