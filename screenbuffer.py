import terminal.output as to
import theme
import style


class Screenbuffer:
	def __init__(self, w, h):
		self.resize(w, h)
	
	def resize(self, w, h):
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
	
	def set(self, x, y, v: str, clip=None, style=None):
		# Make sure we don't get an empty string. Empty space in the
		# screenbuffer is represented by space characters, so an empty string
		# making its way into the screenbuffer screws up alignment for the line
		# it's in.
		if v == "":
			raise ValueError("Screenbuffer.set: cannot set to an empty string")
		
		# Exit if we're outside the clip zone.
		if (clip and not clip.contains(x, y)):
			return
		
		try:
			self.buffer[y][x] = v.encode()
		except IndexError:
			return
		
		self.set_style(x, y, style, clip=clip)
	
	def set_style(self, x, y, v: style.Style, clip=None):
		if v is None:
			return
		
		if (clip and not clip.contains(x, y)):
			return
		
		try:
			self.style_buffer[y][x] = v
		except IndexError:
			return
	
	def draw(self):
		self.root_widget.layout(0, 0, self.w, self.h, self.w, self.h)
		self.root_widget.draw(self)
	
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
