from wcwidth import wcswidth

import tanmatsu.output as to
from tanmatsu import theme
from tanmatsu.style import Style
from tanmatsu.geometry import Rectangle, Point


class Screenbuffer:
	"""
	Buffer holding characters to be written to the screen.
	"""
	
	def __init__(self, w: int, h: int):
		self.resize(w, h)
	
	def resize(self, w: int, h: int):
		self.w = w
		self.h = h
		
		ds = theme.DefaultTheme.default
		self.buffer       = [ [ ' ' for j in range(0, w) ] for i in range(0, h) ]
		self.style_buffer = [ [ ds  for j in range(0, w) ] for i in range(0, h) ]
	
	def clear(self):
		for i in range(len(self.buffer)):
			for j in range(len(self.buffer[i])):
				self.buffer[i][j] = ' '
				self.style_buffer[i][j] = theme.DefaultTheme.default
	
	def set(self,
		x: int,
		y: int,
		character: str,
		clip: Rectangle | None = None,
		style: Style | None = None
	) -> int:
		"""
		Set the value at the given `x`, `y` to `character`. If `style` is given,
		the style of said value will be set to `style` as well.
		
		This function does nothing if `clip` is given and `x`, `y` is outside
		the clip.
		
		:return: The delta between the given `x` and the next valid column
		  in the row. In other words, the width of `character`.
		:rtype: int
		
		:raises ValueError: If `character` is an empty string.
		
		When looping over a string containing arbitrary text, the return
		value of this function should be used as a cumulative offset
		on the `x` argument in subsequent calls to this function.
		
		Failure to account for the fact that any given character may have
		a width between 0 and 2 columns in the terminal may result in
		malformed output.
		
		For example:
		
		.. code-block:: python
		   
		   line = 'Hello! こんにちは！'
		   x_offset = 0
		   
		   for character in line:
		       x_offset += s.set(
		           x + x_offset,
		           y,
		           character,
		           clip=clip,
		           style=style
		       )
		"""
		
		# Make sure we don't get an empty string. Empty space in the
		# screenbuffer is represented by space characters, so an empty string
		# making its way into the screenbuffer screws up alignment for the line
		# it's in.
		if character == "":
			raise ValueError("Screenbuffer.set(): cannot set to an empty string")
		
		# Exit if we're outside the clip zone.
		if (clip and not clip.containsp(Point(x, y))):
			return 0
		
		try:
			self.buffer[y][x] = character
		except IndexError:
			return 0
		
		self.set_style(x, y, style, clip=clip)
		
		return wcswidth(character)
	
	def set_style(self,
		x: int,
		y: int,
		style: Style | None,
		clip: Rectangle | None = None
	):
		"""
		Set the style of the character at the given `x`, `y` to `style`.
		
		This function does nothing if `clip` is given and `x`, `y` is outside
		the clip.
		"""
		
		if style is None:
			return
		
		if (clip and not clip.containsp(Point(x, y))):
			return
		
		try:
			self.style_buffer[y][x] = style
		except IndexError:
			return
	
	def set_string(self,
		x: int,
		y: int,
		string: str,
		style: Style | None = None,
		clip: Rectangle | None = None
	) -> int:
		"""
		Convenience function. Works the same way as :meth:`set`, but writes
		an entire string, starting at `x`, `y`, rather than a single character.
		
		:return: The delta between the given `x` and the next valid column
		  in the row, after all characters in `string` have been set.
		:rtype: int
		"""
		
		x_offset = 0
		for character in string:
			x_offset += self.set(
				x + x_offset,
				y,
				character,
				clip=clip,
				style=style
			)
		return x_offset
	
	def write(self):
		last_seen_style = None
		
		# Loop over each row in both buffers:
		for (i, (bl, sl)) in enumerate(zip(self.buffer, self.style_buffer)):
			line_buffer = b''
			error = 0  # number of columns we need to skip due to multi-column character we just encountered
			
			# Loop over each column in both rows:
			for (bv, sv) in zip(bl, sl):
				if error > 0:
					# The last character we wrote was a multi-column character.
					# We need to skip a number of columns equal to the extra
					# columns the character took up, compared to the standard
					# one-column width.
					error -= 1
					continue
				else:
					error = wcswidth(bv) - 1
				
				# Instead of naively outputting the entire set of formatting
				# escape codes for every single character, perform primitive
				# run-length encoding/compression by only outputting each
				# formatting escape code when it differs from the currently
				# active formatting escape code.
				line_buffer += sv.get_diff(last_seen_style) + bv.encode()
				last_seen_style = sv
			
			# Finally, write `line_buffer` to the terminal.
			# 
			# We use `to.set_position` here instead of new line characters
			# as new line characters seem to cause the terminal to scroll down
			# one line at the end, even if no new line character is present in
			# the final line. It is not immediately clear why this would
			# be the case.
			to.set_position(0, i)
			to.write_bytes(line_buffer)
