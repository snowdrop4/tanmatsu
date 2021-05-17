from tri_declarative import with_meta

from tanmatsu.screenbuffer import Screenbuffer
from tanmatsu.geometry import Rectangle, Dimensions, Point
from .box import Box
from .container import Container
from .scrollable import Scrollable


@with_meta
class FlexBox(Container, Box, Scrollable):
	"""
	A widget that contains other widgets. Has similar behaviour to `flexbox`
	from CSS.
	
	:param flex_direction: Must be either :attr:`VERTICAL` or
	  :attr:`HORIZONTAL`. Defaults to :attr:`VERTICAL`.
	"""
	
	VERTICAL   = 0
	"""Flex from top to bottom. Equivalent to `flex-direction: column` in CSS."""
	
	HORIZONTAL = 1
	"""Flex from left to right. Equivalent to `flex-direction: row` in CSS."""
	
	def __init__(
		self, *args, flex_direction: int = VERTICAL, **kwargs,
	):
		super().__init__(*args, **kwargs)
		
		self.set_flex_direction(flex_direction)
	
	def get_flex_direction(self) -> int:
		return self.flex_direction
	
	def set_flex_direction(self, flex_direction: int):
		if flex_direction != FlexBox.VERTICAL and flex_direction != FlexBox.HORIZONTAL:
			raise ValueError(
				"Invalid value for `flex_direction`. \
					Must equal either `FlexBox.VERTICAL` or `FlexBox.HORIZONTAL`."
			)
		
		self.flex_direction = flex_direction
	
	def layout(self, *args, **kwargs):
		super().layout(*args, **kwargs)
		
		# No children? Nothing to do.
		if len(self.children) == 0:
			return
		
		# Work out how much space we have for each child, supposing that it was
		# shared equally between them.
		if self.flex_direction == FlexBox.HORIZONTAL:
			w_per_child = int(self._Widget__available_space.w / len(self.children))
			h_per_child = self._Widget__available_space.h
		else:
			h_per_child = int(self._Widget__available_space.h / len(self.children))
			w_per_child = self._Widget__available_space.w
		size_per_child = Dimensions(w_per_child, h_per_child)
		
		curr_pos = self._Widget__available_space.origin_point()  # keep track of the current curr_pos for drawing
		total_size = Dimensions(0, 0)  # keep track of the width/height for calculating scroll curr_pos
		
		for (k, v) in self.children.items():
			widget_pos = Point(
				curr_pos.x - self._Scrollable__scroll_position.x,
				curr_pos.y - self._Scrollable__scroll_position.y
			)
			
			v.layout(
				widget_pos,
				self._Widget__available_space.dimensions(),
				size_per_child
			)
			
			if self.flex_direction == FlexBox.HORIZONTAL:
				curr_pos.x += v._Widget__calculated_size.w  # increment the current `x` by the width of the widget
				total_size.w += v._Widget__calculated_size.w  # do the same with the maximum `w`
				total_size.h = max(total_size.h, v._Widget__calculated_size.h)  # set a new maximum `h` if needed
			else:
				curr_pos.y += v._Widget__calculated_size.h
				total_size.w = max(total_size.w, v._Widget__calculated_size.w)
				total_size.h += v._Widget__calculated_size.h
		
		self.scroll(total_size)
	
	def draw(self, s: Screenbuffer, clip: Rectangle | None = None):
		super().draw(s, clip=clip)
		
		for (k, v) in self.children.items():
			v.draw(s, clip=clip & self._Widget__available_space)
