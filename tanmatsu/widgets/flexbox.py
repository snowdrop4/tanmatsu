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
	:paramtype flex_direction: int
	"""
	
	VERTICAL   = 1
	"""Flex from top to bottom. Equivalent to `flex-direction: column` in CSS."""
	
	HORIZONTAL = 2
	"""Flex from left to right. Equivalent to `flex-direction: row` in CSS."""
	
	def __init__(
		self, *args, flex_direction: int = VERTICAL, **kwargs,
	):
		super().__init__(*args, **kwargs)
		
		self.flex_direction = flex_direction
	
	@property
	def flex_direction(self) -> int:
		"""
		:getter: Returns the flex direction.
		:setter: Sets the flex direction.
		         Must equal either :attr:`VERTICAL` or :attr:`HORIZONTAL`.
		"""
		return self.__flex_direction
	
	@flex_direction.setter
	def flex_direction(self, flex_direction: int):
		if flex_direction != FlexBox.VERTICAL and flex_direction != FlexBox.HORIZONTAL:
			raise ValueError((
				"FlexBox.set_flex_direction(): Invalid value for `flex_direction`. "
				"Must equal either `FlexBox.VERTICAL` or `FlexBox.HORIZONTAL`."
			))
		
		self.__flex_direction = flex_direction
	
	def layout(self, *args, **kwargs):
		super().layout(*args, **kwargs)
		
		# No children? Nothing to do.
		if len(self.children) == 0:
			self.set_content_size(Dimensions(0, 0))
			self.layout_scrollbar()
			self.scroll()
			return
		
		# Calculate the size of all the children widgets
		# ‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾
		
		# We calculate the size of all the children widgets here,
		#   as if there were no scrollbars.
		# Then, if the total size of all the widgets exceeds the
		#   total space available, we will need to subtract extra
		#   space to accomodate the presence of scrollbar(s).
		# Then, later, we can finally layout the widgets.
		
		content_size = Dimensions(0, 0)
		
		def get_space_left():
			if self.flex_direction == FlexBox.HORIZONTAL:
				return self._Widget__available_space.w - content_size.w
			else:
				return self._Widget__available_space.h - content_size.h
		
		def get_size_per_remaining_child(remaining_children):
			if self.flex_direction == FlexBox.HORIZONTAL:
				w_per_child = int(get_space_left() / remaining_children)
				h_per_child = self._Widget__available_space.h
			else:
				h_per_child = int(get_space_left() / remaining_children)
				w_per_child = self._Widget__available_space.w
			
			return Dimensions(w_per_child, h_per_child)
		
		for (i, v) in enumerate(self.children.values()):
			actual_widget_size = v.get_actual_size(
				self._Widget__available_space.dimensions(),
				get_size_per_remaining_child(len(self.children.values()) - i)
			)
			
			if self.flex_direction == FlexBox.HORIZONTAL:
				content_size.w += actual_widget_size.w
				content_size.h = max(content_size.h, actual_widget_size.h)
			else:
				content_size.h += actual_widget_size.h
				content_size.w = max(content_size.w, actual_widget_size.w)
		
		# Get the area we can layout widgets in, minus any space
		#   reserved for scrollbars.
		usable_space = self.get_scrollable_area(content_size)
		
		# Layout all the children widgets
		# ‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾
		
		# Reset the content size, as we need to calculate it from
		#   scratch since the addition of scrollbars might have
		#   changed the usable area.
		content_size = Dimensions(0,0)
		
		# Keep track of the current position for drawing
		curr_pos = self._Widget__available_space.origin_point()
		
		for (i, v) in enumerate(self.children.values()):
			widget_pos = Point(
				curr_pos.x - self._Scrollable__scroll_position.x,
				curr_pos.y - self._Scrollable__scroll_position.y
			)
			widget_size = get_size_per_remaining_child(len(self.children.values()) - i)
			
			v.layout(
				widget_pos,
				usable_space.dimensions(),
				widget_size
			)
			actual_widget_size = v.get_actual_size(
				usable_space.dimensions(),
				widget_size
			)
			
			if self.flex_direction == FlexBox.HORIZONTAL:
				curr_pos.x += actual_widget_size.w  # increment the current `x` by the width of the widget
				content_size.w += actual_widget_size.w
				content_size.h = max(content_size.h, actual_widget_size.h)
			else:
				curr_pos.y += actual_widget_size.h
				content_size.w = max(content_size.w, actual_widget_size.w)
				content_size.h += actual_widget_size.h
		
		self.layout_scrollbar(content_size)
		self.scroll()
	
	def draw(self, s: Screenbuffer, clip: Rectangle | None = None):
		super().draw(s, clip=clip)
		
		for (k, v) in self.children.items():
			v.draw(s, clip=clip & self._Widget__available_space)
