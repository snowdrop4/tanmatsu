from tri_declarative import with_meta

import geometry
from .container import Container
from .box import Box
from .scrollable import Scrollable


@with_meta
class FlexBox(Container, Box, Scrollable):
	VERTICAL   = 0
	HORIZONTAL = 1
	
	def __init__(
		self, *args, flex_direction=VERTICAL, **kwargs,
	):
		super().__init__(*args, **kwargs)
		
		if (flex_direction != FlexBox.VERTICAL) and (
			flex_direction != FlexBox.HORIZONTAL
		):
			raise ValueError(
				"Invalid value for `flex_direction`. \
					Must equal either `FlexBox.VERTICAL` or `FlexBox.HORIZONTAL`."
			)
		
		self.flex_direction = flex_direction
	
	def layout(self, x, y, parent_w, parent_h, requested_w, requested_h):
		super().layout(x, y, parent_w, parent_h, requested_w, requested_h)
		
		# No children? Nothing to do.
		if len(self.children) == 0:
			return
		
		if self.flex_direction == FlexBox.HORIZONTAL:
			w_per_child = int(self._Widget__available_space.w / len(self.children))
			h_per_child = self._Widget__available_space.h
		else:
			h_per_child = int(self._Widget__available_space.h / len(self.children))
			w_per_child = self._Widget__available_space.w
		
		position = self._Widget__available_space.duplicate_origin_point()  # keep track of the current position for drawing
		total_size = geometry.Dimensions(0, 0)  # keep track of the width/height for calculating scroll position
		
		position.x = self._Widget__available_space.x
		position.y = self._Widget__available_space.y
		
		for (k, v) in self.children.items():
			v.layout(
				position.x - self._Scrollable__scroll_position.x,
				position.y - self._Scrollable__scroll_position.y,
				self._Widget__available_space.w,
				self._Widget__available_space.h,
				w_per_child,
				h_per_child,
			)
			
			if self.flex_direction == FlexBox.HORIZONTAL:
				position.x += v._Widget__calculated_size.w  # increment the current `x` by the width of the widget
				total_size.w += v._Widget__calculated_size.w  # do the same with the maximum `w`
				total_size.h = max(total_size.h, v._Widget__calculated_size.h)  # set a new maximum `h` if needed
			else:
				position.y += v._Widget__calculated_size.h
				total_size.w = max(total_size.w, v._Widget__calculated_size.w)
				total_size.h += v._Widget__calculated_size.h
		
		self._Scrollable__total_content_size = total_size
		
		self.scroll()
	
	def draw(self, s, clip=None):
		super().draw(s, clip=clip)
		
		for (k, v) in self.children.items():
			v.draw(s, clip=clip.overlap_rectangle(self._Widget__available_space))
