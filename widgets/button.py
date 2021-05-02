from typing import Callable

import terminal.input as ti
from .box import Box
from screenbuffer import Screenbuffer
from geometry import Rectangle


class Button(Box):
	"""
	A button widget. Calls the callback when activated.
	
	:param label: The text to show on the button.
	:param callback: The function the button should call when activated.
	"""
	
	def __init__(self, *args, label: str = "Button", callback: Callable, **kwargs):
		super().__init__(*args, **kwargs)
		
		self.label = label
		self.callback = callback
	
	def draw(self, s: Screenbuffer, clip: Rectangle | None = None):
		super().draw(s, clip=clip)
		
		widget_midpoint = self._Widget__available_space.w // 2
		label_midpoint = len(self.label) // 2
		
		x_offset = max(0, widget_midpoint - label_midpoint)
		y = self._Widget__available_space.y + self._Widget__available_space.h // 2
		
		for (i, character) in enumerate(self.label):
			x = self._Widget__available_space.x + x_offset + i
			
			# If the label is overflowing, break the loop
			if x >= self._Widget__available_space.x2:
				break
			else:
				s.set(
					x,
					y,
					character,
					clip=clip,
					style=None
				)
	
	def keyboard_event(self, key: ti.Keyboard_key, modifier: int):
		if super().keyboard_event(key, modifier):
			return True
		
		if key == ti.Keyboard_key.ENTER:
			self.callback()
			return True
		
		return False
