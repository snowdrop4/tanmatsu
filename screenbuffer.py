import terminal.output as to
import theme
from geometry import Rectangle, Point
from style import Style


class Screenbuffer:
	"""
	Buffer holding characters to be written to the screen.
	"""
	
	def __init__(self, w: int, h: int):
		self.resize(w, h)
	
	def resize(self, w: int, h: int):
		"""Resize the screenbuffer to `w`, `h`."""
		
		self.w = w
		self.h = h
		
		ds = theme.DefaultTheme.default
		self.buffer       = [ [ b' ' for j in range(0, w) ] for i in range(0, h) ]
		self.style_buffer = [ [ ds   for j in range(0, w) ] for i in range(0, h) ]
	
	def clear(self):
		for i in range(len(self.buffer)):
			for j in range(len(self.buffer[i])):
				self.buffer[i][j] = b' '
				self.style_buffer[i][j] = theme.DefaultTheme.default
	
	def set(self, 
		x: int,
		y: int,
		v: str,
		clip: Rectangle | None = None,
		style: Style | None = None
	):
		"""
		Set the character at the given `x`, `y` to `v`. If `style` is given,
		said character will be set to `style` as well.
		
		This function does nothing if `clip` is given and `x`, `y` is outside
		the clip.
		"""
		
		# Make sure we don't get an empty string. Empty space in the
		# screenbuffer is represented by space characters, so an empty string
		# making its way into the screenbuffer screws up alignment for the line
		# it's in.
		if v == "":
			raise ValueError("Screenbuffer.set: cannot set to an empty string")
		
		# Exit if we're outside the clip zone.
		if (clip and not clip.contains(Point(x, y))):
			return
		
		try:
			self.buffer[y][x] = v.encode()
		except IndexError:
			return
		
		self.set_style(x, y, style, clip=clip)
	
	def set_style(self, x: int, y: int, v: Style, clip: Rectangle | None = None):
		"""
		Set the style of the character at the given `x`, `y` to `style`.
		
		This function does nothing if `clip` is given and `x`, `y` is outside
		the clip.
		"""
		
		if v is None:
			return
		
		if (clip and not clip.contains(Point(x, y))):
			return
		
		try:
			self.style_buffer[y][x] = v
		except IndexError:
			return
	
	def write(self):
		last_seen_style = None
		
		# Loop over each row in both buffers:
		for (i, (bl, sl)) in enumerate(zip(self.buffer, self.style_buffer)):
			line_buffer = b''
			
			# Loop over each column in both rows:
			for (bv, sv) in zip(bl, sl):
				# Instead of naively outputting the entire set of formatting
				# escape codes for every single character, perform primitive
				# run-length encoding/compression by only outputting each
				# formatting escape code when it differs from the currently
				# active formatting escape code.
				line_buffer += sv.get_diff(last_seen_style) + bv
				last_seen_style = sv
			
			# Finally, write `line_buffer` to the terminal.
			# 
			# Using new line characters instead of manually setting the cursor
			# position for each line causes the terminal to scroll down one
			# line at the end, even if the new line character is omitted in
			# the final line. It is not immediately clear why this would
			# be the case.
			to.set_position(0, i)
			to.write_bytes(line_buffer)
