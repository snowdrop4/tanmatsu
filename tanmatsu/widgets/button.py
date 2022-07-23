from typing import Callable, NoReturn

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
	:paramtype label: str
	
	:param callback: The function the button should call when activated.
	:paramtype callback: Callable[..., NoReturn]
	"""
	
	def __init__(self,
		*args,
		label: str = "Button",
		callback: Callable[..., NoReturn] | None,
		**kwargs
	):
		super().__init__(*args, **kwargs)
		
		self.__label = label
		self.callback = callback
	
	@property
	def label(self) -> str:
		"""
		:getter: Gets the button's label, i.e., the text to
		         show on the button.
		:setter: Sets the button's label.
		"""
		return self.__label
	
	@label.setter
	def label(self, value: str):
		self.__label = value
	
	@property
	def callback(self) -> Callable[..., NoReturn]:
		"""
		:getter: Gets the button's callback function,
		         i.e., the function called when the button is activated.
		:setter: Sets the button's callback function.
		"""
		return self.__callback
	
	@callback.setter
	def callback(self, value: Callable[..., NoReturn]):
		self.__callback = value
	
	def draw(self, s: Screenbuffer, clip: Rectangle | None = None):
		super().draw(s, clip=clip)
		
		label = wccrop(self.__label, self._Widget__available_space.w)
		
		widget_midpoint = self._Widget__available_space.w // 2
		label_midpoint = wcswidth(self.__label) // 2
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
		key: ti.Keyboard_key | str,
		modifier: ti.Keyboard_modifier
	) -> bool:
		if super().keyboard_event(key, modifier):
			return True
		
		if key == ti.Keyboard_key.ENTER:
			if self.__callback:
				self.__callback()
			return True
		
		return False
