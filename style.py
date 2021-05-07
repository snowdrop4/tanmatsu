import copy

import terminal.output as to


class Style:
	def inherit(other, **kwargs):
		s = copy.deepcopy(other)
		
		for (k, v) in kwargs.items():
			if k in vars(s):
				setattr(s, k, v)
			else:
				raise TypeError(f"Style.inherit() got an unexpected keyword argument '{k}'")
		
		return s
	
	def __init__(self, foreground=None, background=None, bold=None):
		self.foreground = foreground
		self.background = background
		self.bold = bold
	
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
