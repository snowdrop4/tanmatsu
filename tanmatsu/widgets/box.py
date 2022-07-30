from tanmatsu import draw, theme
from tanmatsu.wctools import wccrop
from tanmatsu.geometry import Rectangle
from tanmatsu.screenbuffer import Screenbuffer
from .base import Widget


class Box(Widget):
	"""
	A widget that can draw a border around itself. Does nothing else.
	Widgets that need a border should inherit from this class.
	
	:param border: Whether the border should be drawn or not.
	:paramtype border: bool
	
	:param border_label: A label to be drawn in the top-left of the border.
	:paramtype border_label: str | None
	"""
	
	def __init__(
		self,
		*args,
		border: bool = True,
		border_label: str | None = None,
		**kwargs
	):
		super().__init__(*args, **kwargs)
		
		self.__border = border
		self.__border_label = border_label
	
	@property
	def border(self) -> bool:
		"""
		:getter: Get whether a border is drawn around this widget.
		:setter: Set whether a border is drawn around this widget.
		"""
		return self.__border
	
	@border.setter
	def border(self, border: bool):
		self.__border = border
	
	@property
	def border_label(self) -> str | None:
		"""
		:getter: Get the label drawn in the upper left of this
		         widget's border.
		:setter: Set the label that should be drawn in the upper
		         left of this widget's border. If set to :code:`None`,
		         no border label will be drawn.
		"""
		return self.__border_label
	
	@border_label.setter
	def border_label(self, label: str | None):
		"""
		:param label: The label text. 
		:paramtype label: str | None
		"""
		self.__border_label = label
	
	def layout(self, *args, **kwargs):
		super().layout(*args, **kwargs)
		
		if self.__border:
			self.__border_rectangle = self._Widget__available_space.duplicate()
			
			self._Widget__available_space.x += 1
			self._Widget__available_space.y += 1
			self._Widget__available_space.w -= 2
			self._Widget__available_space.h -= 2
			
			if self.__border_label:
				available_width = self.__border_rectangle.w - 4
				self.__cropped_label = wccrop(self.__border_label, available_width)
	
	def draw(self, s: Screenbuffer, clip: Rectangle | None = None):
		super().draw(s, clip=clip)
		
		if self.__border:
			if self.focused:
				style = theme.DefaultTheme.focused
			else:
				style = None
			
			draw.rectangle(s, self.__border_rectangle, clip=clip, style=style)
			
			if self.__border_label:
				s.set(
					self.__border_rectangle.x + 1,
					self.__border_rectangle.y,
					"|",
					clip=clip,
					style=style
				)
				
				label_length = s.set_string(
					self.__border_rectangle.x + 2,
					self.__border_rectangle.y,
					self.__cropped_label,
					clip=clip,
					style=style
				)
				
				s.set(
					self.__border_rectangle.x + 2 + label_length,
					self.__border_rectangle.y,
					"|",
					clip=clip,
					style=style
				)
