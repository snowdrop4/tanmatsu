import tanmatsu.input as ti
from tanmatsu import draw, debug
from tanmatsu.screenbuffer import Screenbuffer
from tanmatsu.geometry import Rectangle, Dimensions, Point
from .base import Widget


class Scrollable(Widget):
	"""
	A widget that can scroll. Does nothing else.
	Widgets that need to scroll should inherit from this class.
	
	:param scroll_direction: Must be either :attr:`NONE`, :attr:`VERTICAL`,
	  or :attr:`HORIZONTAL`. Defaults to :attr:`VERTICAL`.
	"""
	
	NONE       = 0b00
	"""Not scrollable."""
	
	VERTICAL   = 0b01
	"""Scrollable vertically."""
	
	HORIZONTAL = 0b10
	"""Scrollable horizontally."""
	
	def __init__(self, *args, scroll_direction: int = VERTICAL, **kwargs):
		super().__init__(*args, **kwargs)
		self.set_scroll_direction(scroll_direction)
		
		self.__scroll_position = Point(0, 0)
	
	def layout(self, *args, **kwargs):
		super().layout(*args, **kwargs)
		
		if self.__scroll_direction != Scrollable.NONE:
			if self.__scroll_direction & Scrollable.VERTICAL:
				self.__vertical_scrollbar_rectangle = self._Widget__available_space.duplicate()
				self._Widget__available_space.w -= 1
			
			if self.__scroll_direction & Scrollable.HORIZONTAL:
				self.__horizontal_scrollbar_rectangle = self._Widget__available_space.duplicate()
				self._Widget__available_space.h -= 1
			
			# Shorten both scrollbars if scrolling along both
			# directions is turned on.
			if self.__scroll_direction == (Scrollable.VERTICAL | Scrollable.HORIZONTAL):
				self.__vertical_scrollbar_rectangle.h   -= 1
				self.__horizontal_scrollbar_rectangle.w -= 1
	
	def draw(self, s: Screenbuffer, clip: Rectangle | None = None):
		super().draw(s, clip=clip)
		
		if self.__scroll_direction != Scrollable.NONE:
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
	
	def scrollable(self) -> bool:
		"""Whether the widget is scrollable or not."""
		return self.__scroll_direction != Scrollable.NONE
	
	def set_scroll_direction(self, scroll_direction: int):
		"""Set the scroll direction to `scroll_direction`."""
		if scroll_direction > 0b11 or scroll_direction < 0b00:
			raise ValueError("Scrollable.set_scroll_direction(): \
				`scroll_direction` is a bitmask and must be equal to \
				`Scrollable.NONE`, `Scrollable.VERTICAL`, or `Scrollable.HORIZONTAL`, \
				or a combination thereof.")
		
		self.__scroll_direction = scroll_direction
	
	def scroll(self, content_size: Dimensions | None, delta_x: int = 0, delta_y: int = 0):
		"""
		Scroll the widget by the specified deltas.
		
		:param content_size: The dimensions of the content to be scrolled.
		  This parameter may be `None` if the dimensions of the content has not
		  changed since the last time this method was called.
		"""
		if content_size is not None:
			self.__content_size = content_size
		
		if self.__scroll_direction & Scrollable.HORIZONTAL:
			self._scroll(delta_x, Scrollable.HORIZONTAL)
		
		if self.__scroll_direction & Scrollable.VERTICAL:
			self._scroll(delta_y, Scrollable.VERTICAL)
	
	def _scroll(self, scroll_delta: int, direction: int):
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
		
		# Make it so that the scrolling bottoms out when the bottom of the
		# content is at the bottom of the screen rather than when the bottom 
		# of the content is at the top of the screen.
		# 
		# Clamp this value at, or above, 0 for cases where the content is
		# smaller than the screen (scrolling into negative space doesn't
		# make sense).
		max_scroll_position = max(0, content_length - available_space)
		
		# Clamp the scroll position between 0 and the maximum scroll position
		scroll_position = max(0, scroll_position + scroll_delta)
		scroll_position = min(max_scroll_position, scroll_position)
		
		# Clamp this value at, or above, 1 for cases where the
		# content is smaller than the screen (it can't ever
		# take less than 1 screen to display the content).
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
		
		if self.scrollable() is False:
			return False
		
		match button, modifier:
			case ti.Mouse_button.SCROLL_UP,    ti.Mouse_modifier.NONE:
				self.scroll(None, delta_y=-1)
			case ti.Mouse_button.SCROLL_DOWN,  ti.Mouse_modifier.NONE:
				self.scroll(None, delta_y=+1)
			case ti.Mouse_button.SCROLL_LEFT,  ti.Mouse_modifier.NONE:
				self.scroll(None, delta_x=-1)
			case ti.Mouse_button.SCROLL_RIGHT, ti.Mouse_modifier.NONE:
				self.scroll(None, delta_x=+1)
			
			case ti.Mouse_button.SCROLL_UP,    ti.Mouse_modifier.SHIFT:
				self.scroll(None, delta_x=-1)
			case ti.Mouse_button.SCROLL_DOWN,  ti.Mouse_modifier.SHIFT:
				self.scroll(None, delta_x=+1)
			
			case _:
				return False
		
		return True
