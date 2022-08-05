from math import floor
from fractions import Fraction

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
			x_sizes = self.__layout_children_flex_axis(
				self._Widget__available_space.w,
				lambda widget: widget.w)
			y_sizes = self.__layout_children_nonflex_axis(
				self._Widget__available_space.h,
				lambda widget: widget.h
			)
			
			content_size = Dimensions(
				sum(x_sizes.values()),
				max(y_sizes.values(), default=0)
			)
		else:
			x_sizes = self.__layout_children_nonflex_axis(
				self._Widget__available_space.w,
				lambda widget: widget.w)
			y_sizes = self.__layout_children_flex_axis(
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
			x_sizes = self.__layout_children_flex_axis(
				usable_space.w,
				lambda widget: widget.w
			)
			y_sizes = self.__layout_children_nonflex_axis(
				usable_space.h,
				lambda widget: widget.h
			)
			
			content_size = Dimensions(
				sum(x_sizes.values()),
				max(y_sizes.values(), default=0)
			)
		else:
			x_sizes = self.__layout_children_nonflex_axis(
				usable_space.w,
				lambda widget: widget.w
			)
			y_sizes = self.__layout_children_flex_axis(
				usable_space.h,
				lambda widget: widget.h
			)
			
			content_size = Dimensions(
				max(x_sizes.values(), default=0),
				sum(y_sizes.values())
			)
		
		# Keep track of the current position for drawing
		curr_pos = self._Widget__available_space.origin_point()
		
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
				curr_pos.x += widget_size.w
			else:
				curr_pos.y += widget_size.h
		
		self.layout_scrollbar(content_size)
		self.scroll()
	
	def __layout_children_flex_axis(self, usable_space: int, getter):
		# Keep track of all the size resolutions we have done
		resolved_sizes = { }
		
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
			resolved_sizes[i] = size
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
			resolved_sizes[i] = size
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
				resolved_sizes[i] = auto_each
				space_left -= auto_each
				remaining_widgets -= 1
			
		return resolved_sizes
	
	def __layout_children_nonflex_axis(self, usable_space: int, getter):
		resolved_sizes = { }
		
		for i in self.children.values():
			match type(getter(i)).__name__:
				case "FixedInteger":
					resolved_sizes[i] = getter(i).size
				case "Fraction":
					resolved_sizes[i] = floor(getter(i).fraction * usable_space)
				case "Auto":
					resolved_sizes[i] = usable_space
		
		return resolved_sizes
	
	def draw(self, s: Screenbuffer, clip: Rectangle | None = None):
		super().draw(s, clip=clip)
		
		for (k, v) in self.children.items():
			v.draw(s, clip=clip & self._Widget__available_space)
