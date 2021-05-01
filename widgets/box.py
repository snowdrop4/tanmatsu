import draw
import theme
from .base import Widget


# A widget that can draw a border around itself.
class Box(Widget):
	def __init__(self, *args, border=True, **kwargs):
		super().__init__(*args, **kwargs)
		
		self.__border = border
	
	def layout(self, *args, **kwargs):
		super().layout(*args, **kwargs)
		
		if self.__border:
			self.__border_rectangle = self._Widget__available_space.duplicate()
			
			self._Widget__available_space.x += 1
			self._Widget__available_space.y += 1
			self._Widget__available_space.w -= 2
			self._Widget__available_space.h -= 2
	
	def draw(self, s, clip=None):
		super().draw(s, clip=clip)
		
		if self.__border:
			if self.focused:
				style = theme.DefaultTheme.highlight
			else:
				style = None
			
			draw.rectangle(s, self.__border_rectangle, clip=clip, style=style)
