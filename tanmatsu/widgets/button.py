from typing import Callable

from tri_declarative import with_meta
from wcwidth import wcswidth

import tanmatsu.input as ti
from tanmatsu.geometry import Rectangle
from tanmatsu.screenbuffer import Screenbuffer
from tanmatsu.wctools import wccrop
from .box import Box


@with_meta
class Button(Box):
	"""
	A button widget. Calls the callback when activated.
	
	:param label: The text to show on the button.
	:param callback: The function the button should call when activated.
	
	:ivar label: The text to show on the button.
	:ivar callback: The function the button should call when activated.
	"""
	
	def __init__(self, *args, label: str = "Button", callback: Callable | None, **kwargs):
		super().__init__(*args, **kwargs)
		
		self.label = label
		self.callback = callback
	
	def draw(self, s: Screenbuffer, clip: Rectangle | None = None):
		super().draw(s, clip=clip)
		
		label = wccrop(self.label, self._Widget__available_space.w)
		
		widget_midpoint = self._Widget__available_space.w // 2
		label_midpoint = wcswidth(self.label) // 2
		x_centering_offset = max(0, widget_midpoint - label_midpoint)
		
		s.set_string(
			self._Widget__available_space.x + x_centering_offset,
			self._Widget__available_space.y + self._Widget__available_space.h // 2,
			label,
			style=None,
			clip=clip
		)
	
	def keyboard_event(
		self,
		key: ti.Keyboard_key,
		modifier: ti.Keyboard_modifier
	) -> bool:
		if super().keyboard_event(key, modifier):
			return True
		
		if key == ti.Keyboard_key.ENTER:
			if self.callback:
				self.callback()
			return True
		
		return False
