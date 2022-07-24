from __future__ import annotations
import copy

import tanmatsu.output as to


class Style:
	"""
	Represents the styling available to an invididual character in the terminal.
	
	:param foreground: The foreground (text) colour
	:paramtype foreground: tuple[int, int, int]
	
	:param background: The background colour
	:paramtype background: tuple[int, int, int]
	
	:param bold: Whether the text ought to be bold or not
	:paramtype bold: bool
	"""
	
	def __init__(
		self,
		foreground: tuple[int, int, int] | None = None,
		background: tuple[int, int, int] | None = None,
		bold: bool | None = None
	):
		self.foreground = foreground
		self.background = background
		self.bold = bold
	
	@staticmethod
	def inherit(other: Style, **kwargs):
		"""
		Create a copy of `other`, and then apply the values specified in
		`**kwargs` to this copy.
		
		:param other: other `Style` object to copy.
		:paramtype other: Style
		
		For example, assuming we have the base style:
		
		.. code-block:: python
		   
		   base = Style(forground=(255, 255, 255), background=(0, 0, 0))
		
		we can do:
		
		.. code-block:: python
		   
		   red = Style.inherit(base, foreground=(255, 0, 0))
		
		to create a clone of the base style, except with a red foreground.
		"""
		
		s = copy.deepcopy(other)
		
		for (k, v) in kwargs.items():
			if k in vars(s):
				setattr(s, k, v)
			else:
				raise TypeError(f"Style.inherit(): unexpected keyword argument '{k}'")
		
		return s
	
	def __str__(self):
		return f"{self.foreground} - {self.background} - {self.bold}"
	
	@property
	def escape_sequence(self):
		return self.get_diff(None)
	
	def get_diff(self, other):
		s = b''
		
		# Quick optimisation: we can return nothing if the thing
		# we're comparing against is ourself.
		if self is other:
			return s
		
		if self.foreground is not None and (other is None or self.foreground != other.foreground):
			s += to.str_foreground_colour_24bit(self.foreground)
		
		if self.background is not None and (other is None or self.background != other.background):
			s += to.str_background_colour_24bit(self.background)
		
		if self.bold is not None and (other is None or self.bold != other.bold):
			s += to.str_bold(self.bold)
		
		return s
