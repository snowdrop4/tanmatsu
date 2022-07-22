import geometry
import draw
import terminal.input as ti
from .base import Widget


# A widget that can scroll.
class Scrollable(Widget):
	NONE       = 0b00
	VERTICAL   = 0b01
	HORIZONTAL = 0b10
	
	def __init__(self, *args, scroll_direction=VERTICAL, **kwargs):
		super().__init__(*args, **kwargs)
		
		if scroll_direction > 0b11 or scroll_direction < 0b00:
			raise ValueError("`scroll_direction` is a bitmask and must be equal to \
				`Scrollable.NONE`, `Scrollable.VERTICAL`, or `Scrollable.HORIZONTAL`, \
				or a combination thereof.")
		
		self.__scroll_direction = scroll_direction
		
		self.__scroll_position = geometry.Point(0, 0)
		
		self.__total_content_size = geometry.Dimensions(0, 0)
	
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
	
	def draw(self, s, clip=None):
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
		return self.__scroll_direction != Scrollable.NONE
	
	def scroll(self, delta_x=0, delta_y=0):
		if self.__scroll_direction & Scrollable.HORIZONTAL:
			self.scroll_(delta_x, Scrollable.HORIZONTAL)
		
		if self.__scroll_direction & Scrollable.VERTICAL:
			self.scroll_(delta_y, Scrollable.VERTICAL)
	
	def scroll_(self, line_delta, direction):
		if direction == Scrollable.VERTICAL:
			content_length   = self.__total_content_size.h
			available_space  = self._Widget__available_space.h
			scroll_position  = self.__scroll_position.y
			scrollbar_length = self.__vertical_scrollbar_rectangle.h - 2
		elif direction == Scrollable.HORIZONTAL:
			content_length   = self.__total_content_size.w
			available_space  = self._Widget__available_space.w
			scroll_position  = self.__scroll_position.x
			scrollbar_length = self.__horizontal_scrollbar_rectangle.w - 2
		else:
			raise ValueError("Invalid value for `direction`. \
				Must equal either `Scrollable.VERTICAL`, or `Scrollable.HORIZONTAL`.")
		
		# Make it so that the scrolling bottoms out when the bottom of the
		# content is at the bottom of the screen rather than when the bottom 
		# of the content is at the top of the screen.
		# 
		# Clamp this value at, or above, 0 for cases where the content is
		# smaller than the screen (scrolling into negative space doesn't
		# make sense).
		max_scroll_position = max(0, content_length - available_space)
		
		# Clamp the scroll position between 0 and the maximum scroll position
		scroll_position = max(0, scroll_position + line_delta)
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
	
	def mouse_event(self, button, button_state, position):
		if super().mouse_event(button, button_state, position):
			return True
		
		match button:
			case ti.Mouse_button.SCROLL_UP:
				self.scroll(delta_y=-1)
			case ti.Mouse_button.SCROLL_DOWN:
				self.scroll(delta_y=1)
			case ti.Mouse_button.SCROLL_LEFT:
				self.scroll(delta_x=-1)
			case ti.Mouse_button.SCROLL_RIGHT:
				self.scroll(delta_x=1)
			case _:
				return False
		
		return True
