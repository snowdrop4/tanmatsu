from enum import Enum, auto
from math import floor
from fractions import Fraction
from typing import Callable, Any

from tri_declarative import with_meta

from tanmatsu.screenbuffer import Screenbuffer
from tanmatsu.geometry import Rectangle, Dimensions, Point
from .base import Widget
from .box import Box
from .container import Container
from .scrollable import Scrollable


class FlexDirection(Enum):
	COLUMN = auto()
	"""Flex from top to bottom."""
	
	ROW    = auto()
	"""Flex from left to right."""


class JustifyContent(Enum):
	FLEX_START    = auto()
	"""Layout items beginning from the start of the flex."""
	
	FLEX_END      = auto()
	"""Layout items beginning from the end of the flex."""
	
	CENTER        = auto()
	"""Layout items around the center of the flex."""
	
	SPACE_BETWEEN = auto()
	"""
	Layout items, with the first item at the start of the flex, and the last
	item at the end of the flex. Free is space equally distributed
	between all the items.
	"""
	
	SPACE_AROUND  = auto()
	"""
	Layout items with free space distributed such that each item has equal
	non-collapsing margins on either side.
	"""
	
	SPACE_EVENLY  = auto()
	"""
	Layout items with free space distributed such that the gaps between any two
	items, and any item and the nearest edge, are the same.
	"""

@with_meta
class FlexBox(Container, Box, Scrollable):
	"""
	A widget that contains other widgets. Has similar behaviour to `flexbox`
	from CSS.
	
	:param flex_direction: Which direction the items should be flexed.
	:paramtype flex_direction: FlexDirection
	
	:param justify_content: How the items should be distributed along the flex.
	:paramtype justify_content: JustifyContent
	"""
	
	def __init__(
		self,
		*args,
		flex_direction: FlexDirection = FlexDirection.COLUMN,
		justify_content: JustifyContent = JustifyContent.FLEX_START,
		**kwargs,
	):
		super().__init__(*args, **kwargs)
		
		self.__flex_direction = None  # Silence typechecker
		self.flex_direction = flex_direction
		
		self.__justify_content = None  # Silence typechecker
		self.justify_content = justify_content
	
	@property
	def flex_direction(self) -> FlexDirection:
		"""
		:getter: Returns the flex direction.
		:setter: Sets the flex direction.
		"""
		return self.__flex_direction
	
	@flex_direction.setter
	def flex_direction(self, flex_direction: FlexDirection):
		self.__flex_direction = flex_direction
	
	@property
	def justify_content(self) -> JustifyContent:
		"""
		:getter: Returns the justify content setting.
		:setter: Sets the justify content setting.
		"""
		return self.__justify_content
	
	@justify_content.setter
	def justify_content(self, justify_content: JustifyContent):
		self.__justify_content = justify_content
	
	def layout(self, *args, **kwargs):
		super().layout(*args, **kwargs)
		
		# No children? Nothing to do.
		if len(self.children) == 0:
			self.layout_scrollbar(Dimensions(0, 0))
			self.scroll()
			return
		
		def calc_widget_sizes(space: Rectangle) -> (
			tuple[dict[Widget, int], dict[Widget, int], Dimensions]
		):
			if self.flex_direction == FlexDirection.ROW:
				x_sizes = self.__calc_children_sizes_flex_axis(
					space.w,
					lambda widget: widget.w
				)
				y_sizes = self.__calc_children_sizes_nonflex_axis(
					space.h,
					lambda widget: widget.h
				)
				
				content_size = Dimensions(
					sum(x_sizes.values()),
					max(y_sizes.values(), default=0)
				)
			else:
				x_sizes = self.__calc_children_sizes_nonflex_axis(
					space.w,
					lambda widget: widget.w
				)
				y_sizes = self.__calc_children_sizes_flex_axis(
					space.h,
					lambda widget: widget.h
				)
				
				content_size = Dimensions(
					max(x_sizes.values(), default=0),
					sum(y_sizes.values())
				)
			
			return (x_sizes, y_sizes, content_size)
		
		# Calculate the size of all the children widgets
		# ‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾
		
		# We have to calculate the size of all the children widgets
		#   as if there were no scrollbars.
		# Then, if the total size of all the widgets exceeds the
		#   total space available, we will need to subtract extra
		#   space to accomodate the presence of scrollbar(s), and recalculate
		#   the size of all the widgets, taking into account the decreased
		#   amount of space available.
		
		(x_sizes, y_sizes, content_size) = calc_widget_sizes(self._Widget__available_space)
		
		# Get the actual area we have available to layout widgets in,
		#   minus any space required by any scrollbars.
		usable_space = self.get_scrollable_area(content_size)
		
		# Recalculate widget sizes (if necessary)
		# ‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾
		
		hori_too_big = self.flex_direction == FlexDirection.ROW    and content_size.w > usable_space.w
		vert_too_big = self.flex_direction == FlexDirection.COLUMN and content_size.h > usable_space.h
		
		if (hori_too_big or vert_too_big):
			(x_sizes, y_sizes, content_size) = calc_widget_sizes(self._Widget__available_space)
		
		# Layout all the children widgets
		# ‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾
		
		match self.justify_content:
			case JustifyContent.FLEX_START:
				self.__layout_flex_start(x_sizes, y_sizes)
			case JustifyContent.FLEX_END:
				self.__layout_flex_end(x_sizes, y_sizes)
			case JustifyContent.CENTER:
				self.__layout_flex_center(x_sizes, y_sizes)
			case JustifyContent.SPACE_BETWEEN:
				self.__layout_flex_space_between(x_sizes, y_sizes)
			case JustifyContent.SPACE_AROUND:
				self.__layout_flex_space_around(x_sizes, y_sizes)
			case JustifyContent.SPACE_EVENLY:
				self.__layout_flex_space_evenly(x_sizes, y_sizes)
			case _:
				raise NotImplementedError("Unimplemented justify_content value")
		
		self.layout_scrollbar(content_size)
		self.scroll()
	
	def __layout_flex_start(self,
		x_sizes: dict[Widget, int],
		y_sizes: dict[Widget, int],
		start_pos_offset: int = 0,
		gap: int = 0
	):
		curr_pos = self._Widget__available_space.top_left()
		
		if self.flex_direction == FlexDirection.ROW:
			curr_pos.x += start_pos_offset
		else:
			curr_pos.y += start_pos_offset
		
		for i in self.children.values():
			widget_pos = Point(
				curr_pos.x - self._Scrollable__scroll_position.x,
				curr_pos.y - self._Scrollable__scroll_position.y
			)
			widget_size = Dimensions(x_sizes[i], y_sizes[i])
			
			# Layout the widget
			i.layout(widget_pos, widget_size)
			
			# Update the position for the next widget
			if self.flex_direction == FlexDirection.ROW:
				curr_pos.x += widget_size.w + gap
			else:
				curr_pos.y += widget_size.h + gap
	
	def __layout_flex_end(self,
		x_sizes: dict[Widget, int],
		y_sizes: dict[Widget, int]
	):
		# Keep track of the current position for drawing
		curr_pos = self._Widget__available_space.top_right()
		
		for i in reversed(self.children.values()):
			widget_size = Dimensions(x_sizes[i], y_sizes[i])
			
			if self.flex_direction == FlexDirection.ROW:
				curr_pos.x -= widget_size.w
			else:
				curr_pos.y -= widget_size.h
			
			widget_pos = Point(
				curr_pos.x - self._Scrollable__scroll_position.x,
				curr_pos.y - self._Scrollable__scroll_position.y
			)
			
			# Layout the widget
			i.layout(widget_pos, widget_size)
	
	def __layout_flex_center(self,
		x_sizes: dict[Widget, int],
		y_sizes: dict[Widget, int]
	):
		# Work out how much space our widgets take up
		if self.flex_direction == FlexDirection.ROW:
			total_widget_size = sum(x_sizes.values())
			available_space = self._Widget__available_space.w
		else:
			total_widget_size = sum(y_sizes.values())
			available_space = self._Widget__available_space.h
		
		# If the widgets are larger than the available space,
		#   just layout as if we were FLEX_START.
		if total_widget_size >= available_space:
			self.__layout_flex_start(x_sizes, y_sizes)
			return
		
		# Work out our starting position offset
		start_pos_offset = (available_space - total_widget_size) // 2
		
		self.__layout_flex_start(x_sizes, y_sizes, start_pos_offset=start_pos_offset)
	
	def __layout_flex_space_between(self,
		x_sizes: dict[Widget, int],
		y_sizes: dict[Widget, int]
	):
		# Work out how much space our widgets take up
		if self.flex_direction == FlexDirection.ROW:
			total_widget_size = sum(x_sizes.values())
			available_space = self._Widget__available_space.w
		else:
			total_widget_size = sum(y_sizes.values())
			available_space = self._Widget__available_space.h
		
		# If the widgets are larger than the available space,
		#   just layout as if we were FLEX_START.
		if total_widget_size >= available_space:
			self.__layout_flex_start(x_sizes, y_sizes)
			return
		
		# Work out the gap we need between each widget
		gap = (available_space - total_widget_size) // (len(self.children) - 1)
		
		self.__layout_flex_start(x_sizes, y_sizes, gap=gap)
	
	def __layout_flex_space_around(self,
		x_sizes: dict[Widget, int],
		y_sizes: dict[Widget, int]
	):
		# Work out how much space our widgets take up
		if self.flex_direction == FlexDirection.ROW:
			total_widget_size = sum(x_sizes.values())
			available_space = self._Widget__available_space.w
		else:
			total_widget_size = sum(y_sizes.values())
			available_space = self._Widget__available_space.h
		
		# If the widgets are larger than the available space,
		#   just layout as if we were FLEX_START.
		if total_widget_size >= available_space:
			self.__layout_flex_start(x_sizes, y_sizes)
			return
		
		# Work out the gap we need to place between each 
		gap = (available_space - total_widget_size) // len(self.children)
		
		# Work out our starting position offset
		start_pos_offset = gap // 2
		
		self.__layout_flex_start(x_sizes, y_sizes, start_pos_offset=start_pos_offset, gap=gap)
	
	def __layout_flex_space_evenly(self,
		x_sizes: dict[Widget, int],
		y_sizes: dict[Widget, int]
	):
		# Work out how much space our widgets take up
		if self.flex_direction == FlexDirection.ROW:
			total_widget_size = sum(x_sizes.values())
			available_space = self._Widget__available_space.w
		else:
			total_widget_size = sum(y_sizes.values())
			available_space = self._Widget__available_space.h
		
		# If the widgets are larger than the available space,
		#   just layout as if we were FLEX_START.
		if total_widget_size >= available_space:
			self.__layout_flex_start(x_sizes, y_sizes)
			return
		
		# Work out the gap we need to place between each 
		gap = (available_space - total_widget_size) // (len(self.children) + 1)
		
		self.__layout_flex_start(x_sizes, y_sizes, start_pos_offset=gap, gap=gap)
	
	# Takes the amount of space available in a given axis, and a function that,
	#   given a widget, returns the size object for that same axis.
	# 
	# For example:
	# 
	# self.__calc_children_sizes_flex_axis(
	#     usable_space=usable_space.w,
	#     getter=lambda widget: widget.w
	# )
	# 
	# Returns a dictionary mapping children to their sizes for the axis
	#   specified, with these objects flexed along this axis (i.e., laid out
	#   as a cohesive unit; sharing the space available between them).
	def __calc_children_sizes_flex_axis(self,
		usable_space: int,
		getter: Callable[[Widget], Any]
	) -> dict[Widget, int]:
		# Keep track of all the size resolutions we have done
		calculated_sizes = { }
		
		# Keep track of how many widgets we need to layout
		remaining_widgets = 0
		
		# Keep track of how much space we've used so far
		space_left = usable_space
		
		# Sort every widget according to how its size should be determined
		fixed_integer = []
		fraction = []
		auto = []
		
		for i in self.children.values():
			match type(getter(i)).__name__:
				case "FixedInteger":
					fixed_integer.append(i)
				case "Fraction":
					fraction.append(i)
				case "Auto":
					auto.append(i)
				case _:
					raise NotImplementedError("Unimplemented size value")
			
			remaining_widgets += 1
		
		# FixedInteger
		# ‾‾‾‾‾‾‾‾‾‾‾‾
		
		# First, deal with all the FixedInteger sizes, as these are the
		#   most intransigent. Not resolving these first means that we won't
		#   know how much space there is left to distribute to sizes which
		#   resolve to a fraction of the remaining space.
		for i in fixed_integer:
			size = getter(i).size
			calculated_sizes[i] = size
			space_left -= size
			remaining_widgets -= 1
		
		# Fraction
		# ‾‾‾‾‾‾‾‾
		
		# Second, deal with the Fraction sizes, as these specify
		#   a fraction of the remaining space.
		total_fraction = Fraction(0, 1)
		
		# Find out what all the fractions add up to, so that if we end up
		#   with (for example) three widgets, each asking for 1/2 of the space,
		#   we can ask what fraction of total_fraction each widget is
		#   asking, which is 1/3.
		for i in fraction:
			total_fraction += getter(i).fraction
		
		# If the total fraction is less than 1/1, then set the total fraction
		#   to 1/1, so that we can always take a fraction of total_fraction.
		if total_fraction < Fraction(1, 1):
			total_fraction = Fraction(1, 1)
		
		space_left_for_fractions = space_left
		
		for i in fraction:
			real_fraction = getter(i).fraction / total_fraction
			size = floor(real_fraction * space_left_for_fractions)
			calculated_sizes[i] = size
			space_left -= size
			remaining_widgets -= 1
		
		# Auto
		# ‾‾‾‾
		
		# Finally, deal with the Auto sizes, as we distribute the remaining
		#   space equally among all Auto widgets.
		
		if remaining_widgets > 0:
			# Get the amount of space we can give each Auto widget
			auto_each = max(space_left // remaining_widgets, 0)
			
			for i in auto:
				calculated_sizes[i] = auto_each
				space_left -= auto_each
				remaining_widgets -= 1
			
		return calculated_sizes
	
	# Returns a dictionary mapping children to their sizes for the axis
	#   specified, with these objects *not* flexed along this axis (i.e.,
	#   laid out, without the size of one widget along this axis affecting
	#   the size of any of the other widgets).
	def __calc_children_sizes_nonflex_axis(self,
		usable_space: int,
		getter: Callable[[Widget], Any]
	) -> dict[Widget, int]:
		calculated_sizes = { }
		
		for i in self.children.values():
			match type(getter(i)).__name__:
				case "FixedInteger":
					calculated_sizes[i] = getter(i).size
				case "Fraction":
					calculated_sizes[i] = floor(getter(i).fraction * usable_space)
				case "Auto":
					calculated_sizes[i] = usable_space
				case _:
					raise NotImplementedError("Unimplemented size value")
		
		return calculated_sizes
	
	def draw(self, s: Screenbuffer, clip: Rectangle | None = None):
		super().draw(s, clip=clip)
		
		for (k, v) in self.children.items():
			v.draw(s, clip=clip & self._Widget__available_space)
