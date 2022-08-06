from typing import Callable, Any
from math import floor
from fractions import Fraction

from tri_declarative import with_meta

from tanmatsu.screenbuffer import Screenbuffer
from tanmatsu.geometry import Rectangle, Dimensions, Point
from .base import Widget
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
	
	FLEX_START    = 1
	"""Layout items beginning from the start of the flex."""
	
	FLEX_END      = 2
	"""Layout items beginning from the end of the flex."""
	
	CENTER        = 3
	"""Layout items around the center of the flex."""
	
	SPACE_BETWEEN = 4
	"""
	Layout items, with the first item at the start of the flex, and the last
	item at the end of the flex. Free is space equally distributed
	between all the items.
	"""
	
	SPACE_AROUND  = 5
	"""
	Layout items with free space distributed such that each item has equal
	non-collapsing margins on either side.
	"""
	
	SPACE_EVENLY  = 6
	"""
	Layout items with free space distributed such that the gaps between any two
	items, and any item and the nearest edge, are the same.
	"""
	
	def __init__(
		self,
		*args,
		flex_direction: int = VERTICAL,
		justify_content: int = FLEX_START,
		**kwargs,
	):
		super().__init__(*args, **kwargs)
		
		self.flex_direction = flex_direction
		self.justify_content = justify_content
	
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
				"FlexBox.flex_direction: Invalid value for `flex_direction`. "
				"Must equal either `FlexBox.VERTICAL` or `FlexBox.HORIZONTAL`."
			))
		
		self.__flex_direction = flex_direction
	
	@property
	def justify_content(self) -> int:
		"""
		:getter: Returns the justify content setting.
		:setter: Sets the justify content setting.
		         Must equal either :attr:`FLEX_START`, :attr:`FLEX_END`,
		         :attr:`CENTER`, or :attr:`SPACE_BETWEEN`.
		"""
		return self.__justify_content
	
	@justify_content.setter
	def justify_content(self, justify_content: int):
		if (justify_content != FlexBox.FLEX_START and
			justify_content != FlexBox.FLEX_END and 
		    justify_content != FlexBox.CENTER and
			justify_content != FlexBox.SPACE_BETWEEN and
			justify_content != FlexBox.SPACE_AROUND and
			justify_content != FlexBox.SPACE_EVENLY
		):
			raise ValueError((
				"FlexBox.justify_content: Invalid value for `justify_content`. "
				"Must equal `FlexBox.FLEX_START`, `FlexBox.FLEX_END`, "
				"`FlexBox.CENTER`, or `FlexBox.SPACE_BETWEEN`."
			))
		
		self.__justify_content = justify_content
	
	def layout(self, *args, **kwargs):
		super().layout(*args, **kwargs)
		
		# No children? Nothing to do.
		if len(self.children) == 0:
			self.layout_scrollbar(Dimensions(0, 0))
			self.scroll()
			return
		
		# Calculate the size of all the children widgets
		# ‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾
		
		# We have to calculate the size of all the children widgets
		#   as if there were no scrollbars.
		# Then, if the total size of all the widgets exceeds the
		#   total space available, we will need to subtract extra
		#   space to accomodate the presence of scrollbar(s).
		# Then, later, we need to layout the widgets again, taking into
		#   account the decreased amount of space available.
		
		if self.flex_direction == FlexBox.HORIZONTAL:
			x_sizes = self.__calc_children_sizes_flex_axis(
				self._Widget__available_space.w,
				lambda widget: widget.w
			)
			y_sizes = self.__calc_children_sizes_nonflex_axis(
				self._Widget__available_space.h,
				lambda widget: widget.h
			)
			
			content_size = Dimensions(
				sum(x_sizes.values()),
				max(y_sizes.values(), default=0)
			)
		else:
			x_sizes = self.__calc_children_sizes_nonflex_axis(
				self._Widget__available_space.w,
				lambda widget: widget.w
			)
			y_sizes = self.__calc_children_sizes_flex_axis(
				self._Widget__available_space.h,
				lambda widget: widget.h
			)
			
			content_size = Dimensions(
				max(x_sizes.values(), default=0),
				sum(y_sizes.values())
			)
		
		# Get the actual area we have available to layout widgets in,
		#   minus any space required by any scrollbars.
		usable_space = self.get_scrollable_area(content_size)
		
		# Layout all the children widgets
		# ‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾
		
		if self.flex_direction == FlexBox.HORIZONTAL:
			x_sizes = self.__calc_children_sizes_flex_axis(
				usable_space.w,
				lambda widget: widget.w
			)
			y_sizes = self.__calc_children_sizes_nonflex_axis(
				usable_space.h,
				lambda widget: widget.h
			)
			
			content_size = Dimensions(
				sum(x_sizes.values()),
				max(y_sizes.values(), default=0)
			)
		else:
			x_sizes = self.__calc_children_sizes_nonflex_axis(
				usable_space.w,
				lambda widget: widget.w
			)
			y_sizes = self.__calc_children_sizes_flex_axis(
				usable_space.h,
				lambda widget: widget.h
			)
			
			content_size = Dimensions(
				max(x_sizes.values(), default=0),
				sum(y_sizes.values())
			)
		
		match self.justify_content:
			case self.FLEX_START:
				self.__layout_flex_start(x_sizes, y_sizes)
			case self.FLEX_END:
				self.__layout_flex_end(x_sizes, y_sizes)
			case self.CENTER:
				self.__layout_flex_center(x_sizes, y_sizes)
			case self.SPACE_BETWEEN:
				self.__layout_flex_space_between(x_sizes, y_sizes)
			case self.SPACE_AROUND:
				self.__layout_flex_space_around(x_sizes, y_sizes)
			case self.SPACE_EVENLY:
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
		
		if self.flex_direction == FlexBox.HORIZONTAL:
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
			if self.flex_direction == FlexBox.HORIZONTAL:
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
			
			if self.flex_direction == FlexBox.HORIZONTAL:
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
		if self.flex_direction == FlexBox.HORIZONTAL:
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
		if self.flex_direction == FlexBox.HORIZONTAL:
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
		if self.flex_direction == FlexBox.HORIZONTAL:
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
		if self.flex_direction == FlexBox.HORIZONTAL:
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
		
		return calculated_sizes
	
	def draw(self, s: Screenbuffer, clip: Rectangle | None = None):
		super().draw(s, clip=clip)
		
		for (k, v) in self.children.items():
			v.draw(s, clip=clip & self._Widget__available_space)
