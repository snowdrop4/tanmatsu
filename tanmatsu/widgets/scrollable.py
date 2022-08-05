import tanmatsu.input as ti
from tanmatsu import draw
from tanmatsu.screenbuffer import Screenbuffer
from tanmatsu.geometry import Rectangle, Dimensions, Point
from .base import Widget


class Scrollable(Widget):
	"""
	A widget that can scroll. Does nothing else.
	Widgets that need to scroll should inherit from this class.
	
	:param scroll_direction: Must be either :attr:`NONE`, :attr:`VERTICAL`,
	                         :attr:`HORIZONTAL`, or :attr:`BOTH`.
	                         Defaults to :attr:`VERTICAL`.
	:paramtype scroll_direction: int
	
	The layout function of a descendant of this widget should look like:
	
	.. code-block:: python
	   
	   def layout(self, *args, **kwargs):
	       super().layout(*args, **kwargs)
	       
	       content_size = <calculate content size>
	       
	       self.layout_scrollbar(content_size)
	       self.scroll()
	"""
	
	NONE       = 0b00
	"""Not scrollable at all."""
	
	VERTICAL   = 0b01
	"""Scrollable vertically."""
	
	HORIZONTAL = 0b10
	"""Scrollable horizontally."""
	
	BOTH       = 0b11
	"""Scrollable in both directions."""
	
	def __init__(self, *args, scroll_direction: int = VERTICAL, **kwargs):
		super().__init__(*args, **kwargs)
		self.scroll_direction = scroll_direction
		
		self.__scroll_position = Point(0, 0)
		self.__content_size = Dimensions(0, 0)
	
	def layout(self, *args, **kwargs):
		super().layout(*args, **kwargs)
	
	def __get_scrollable_area_and_directions(
		self,
		content_size: Dimensions
	) -> tuple[Rectangle, bool, bool]:
		scrollable_area = self._Widget__available_space.duplicate()
		
		h_scroll_required = content_size.w > scrollable_area.w
		v_scroll_required = content_size.h > scrollable_area.h
		
		if h_scroll_required:
			scrollable_area.h -= 1
			if content_size.h > scrollable_area.h:
				scrollable_area.w -= 1
				v_scroll_required = True
		elif v_scroll_required:
			scrollable_area.w -= 1
			if content_size.w > scrollable_area.w:
				scrollable_area.h -= 1
				h_scroll_required = True
		
		return (scrollable_area, h_scroll_required, v_scroll_required)
	
	def get_scrollable_area(self, content_size: Dimensions) -> Rectangle:
		(scrollable_area, _, _) = self.__get_scrollable_area_and_directions(content_size)
		return scrollable_area

	def layout_scrollbar(self, content_size: Dimensions):
		"""
		Layout the scrollbar. Must be called before :meth:`scroll`,
		inside the layout function of descendants of this class.
		"""
		self.__content_size = content_size
		
		self.__vertical_scrollbar_rectangle   = self._Widget__available_space.duplicate()
		self.__horizontal_scrollbar_rectangle = self._Widget__available_space.duplicate()
		
		(scrollable_area,
		 h_scroll_required,
		 v_scroll_required) = self.__get_scrollable_area_and_directions(self.__content_size)
		self._Widget__available_space = scrollable_area
		
		match (h_scroll_required, v_scroll_required, self.__scroll_direction):
			case (True, False, Scrollable.HORIZONTAL) | (True, False, Scrollable.BOTH):
				self.__vertical_scrollbar_rectangle   = Rectangle(0,0,0,0)
			case (False, True, Scrollable.VERTICAL  ) | (False, True, Scrollable.BOTH):
				self.__horizontal_scrollbar_rectangle = Rectangle(0,0,0,0)
			case (False, False, _):
				self.__horizontal_scrollbar_rectangle = Rectangle(0,0,0,0)
				self.__vertical_scrollbar_rectangle   = Rectangle(0,0,0,0)
	
	def draw(self, s: Screenbuffer, clip: Rectangle | None = None):
		super().draw(s, clip=clip)
		
		if (self.__scroll_direction != Scrollable.NONE):
			if self.__scroll_direction & Scrollable.VERTICAL:
				draw.scrollbar(
					s,
					self.__vertical_scrollbar_rectangle,
					self.__vertical_scrollbar_handle_length,
					self.__vertical_scroll_percent,
					Scrollable.VERTICAL,
					clip=clip,
				)
			
			if self.__scroll_direction & Scrollable.HORIZONTAL:
				draw.scrollbar(
					s,
					self.__horizontal_scrollbar_rectangle,
					self.__horizontal_scrollbar_handle_length,
					self.__horizontal_scroll_percent,
					Scrollable.HORIZONTAL,
					clip=clip,
				)
	
	@property
	def scrollable(self) -> bool:
		"""
		:getter: Get whether the widget is scrollable or not.
		         I.e., whether the scroll direction ≠ :code:`Scrollable.NONE`.
		"""
		return self.__scroll_direction != Scrollable.NONE
	
	@property
	def scroll_direction(self) -> int:
		"""
		:getter: Get the scroll direction.
		:setter: Set the scroll direction.
		"""
		return self.__scroll_direction
	
	@scroll_direction.setter
	def scroll_direction(self, scroll_direction: int):
		if scroll_direction > 0b11 or scroll_direction < 0b00:
			raise ValueError(("Scrollable.set_scroll_direction(): "
				"`scroll_direction` is a bitmask and must be equal to "
				"`Scrollable.NONE`, `Scrollable.VERTICAL`, or `Scrollable.HORIZONTAL`, "
				"or a combination thereof."
			))
		
		self.__scroll_direction = scroll_direction
	
	def scroll(self, delta_x: int = 0, delta_y: int = 0):
		"""
		Scroll the widget by the specified deltas. Must be called after
		:meth:`layout_scrollbar`, inside the layout function of
		descendants of this class.
		"""
		if self.__scroll_direction & Scrollable.HORIZONTAL:
			self.__scroll(delta_x, Scrollable.HORIZONTAL)
		
		if self.__scroll_direction & Scrollable.VERTICAL:
			self.__scroll(delta_y, Scrollable.VERTICAL)
	
	def __scroll(self, scroll_delta: int, direction: int):
		if direction == Scrollable.VERTICAL:
			content_length   = self.__content_size.h
			available_space  = self._Widget__available_space.h
			scroll_position  = self.__scroll_position.y
			scrollbar_length = self.__vertical_scrollbar_rectangle.h - 2
		elif direction == Scrollable.HORIZONTAL:
			content_length   = self.__content_size.w
			available_space  = self._Widget__available_space.w
			scroll_position  = self.__scroll_position.x
			scrollbar_length = self.__horizontal_scrollbar_rectangle.w - 2
		else:
			raise ValueError(("Scrollable._scroll(): Invalid value for `direction`. "
				"Must equal either `Scrollable.VERTICAL`, or `Scrollable.HORIZONTAL`"
			))
		
		# Make it so that the scrolling bottoms out when the bottom of the
		#   content is at the bottom of the screen rather than when the bottom
		#   of the content is at the top of the screen.
		# 
		# Clamp this value at, or above, 0 for cases where the content is
		#   smaller than the screen (scrolling into negative space doesn't
		#   make sense).
		max_scroll_position = max(0, content_length - available_space)
		
		# Clamp the scroll position between 0 and the maximum scroll position
		scroll_position = max(0, scroll_position + scroll_delta)
		scroll_position = min(max_scroll_position, scroll_position)
		
		# Clamp this value at, or above, 1 for cases where the
		#   content is smaller than the screen (it can't ever
		#   take less than 1 screen to display the content).
		screens_to_display_content = content_length / max(1, available_space)
		screens_to_display_content = max(1, screens_to_display_content)
		
		scrollbar_handle_length = int(scrollbar_length / screens_to_display_content)
		scrollbar_handle_length = max(1, scrollbar_handle_length)
		
		if max_scroll_position == 0:
			scroll_percent = 0
		else:
			scroll_percent = scroll_position / max_scroll_position
		
		if direction == Scrollable.VERTICAL:
			self.__scroll_position.y = scroll_position
			self.__vertical_scrollbar_handle_length = scrollbar_handle_length
			self.__vertical_scroll_percent = scroll_percent
		elif direction == Scrollable.HORIZONTAL:
			self.__scroll_position.x = scroll_position
			self.__horizontal_scrollbar_handle_length = scrollbar_handle_length
			self.__horizontal_scroll_percent = scroll_percent
		
		self.viewport = Rectangle(
			self._Widget__available_space.x + self.__scroll_position.x,
			self._Widget__available_space.y + self.__scroll_position.y,
			self._Widget__available_space.w,
			self._Widget__available_space.h
		)
	
	def mouse_event(
		self,
		button: ti.Mouse_button,
		modifier: ti.Mouse_modifier,
		state: ti.Mouse_state,
		position: Point
	) -> bool:
		if super().mouse_event(button, modifier, state, position):
			return True
		
		if self.scrollable is False:
			return False
		
		match button, modifier:
			# Mouse wheel
			case ti.Mouse_button.SCROLL_UP,    ti.Mouse_modifier.NONE:
				self.scroll(delta_y=-1)
			case ti.Mouse_button.SCROLL_DOWN,  ti.Mouse_modifier.NONE:
				self.scroll(delta_y=+1)
			case ti.Mouse_button.SCROLL_LEFT,  ti.Mouse_modifier.NONE:
				self.scroll(delta_x=-1)
			case ti.Mouse_button.SCROLL_RIGHT, ti.Mouse_modifier.NONE:
				self.scroll(delta_x=+1)
			# Mouse wheel + shift
			case ti.Mouse_button.SCROLL_UP,    ti.Mouse_modifier.SHIFT:
				self.scroll(delta_x=-1)
			case ti.Mouse_button.SCROLL_DOWN,  ti.Mouse_modifier.SHIFT:
				self.scroll(delta_x=+1)
			# Fallthrough
			case _:
				return False
		
		return True
