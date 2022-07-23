from tri_declarative import with_meta

from tanmatsu.wctools import wcchunks
from tanmatsu.geometry import Rectangle
from tanmatsu.screenbuffer import Screenbuffer
from .box import Box


@with_meta
class TextLog(Box):
	"""
	A widget that displays multiple lines of text, with new lines being added
	to the bottom and old ones scrolling upwards. Like a traditional terminal.
	
	:param lines: The lines the TextLog should contain.
	:paramtype lines: list[str]
	"""
	
	def __init__(self, *args, lines: list[str] = [], **kwargs):
		super().__init__(*args, **kwargs)
		
		self.__lines = lines
	
	def append_line(self, line):
		"""Append a line to the TextLog."""
		self.__lines.append(line)
	
	@property
	def lines(self) -> list[str]:
		"""
		:getter: Gets the text lines contained within the TextLog.
		:setter: Sets the text lines.
		"""
		return self.__lines
	
	@lines.setter
	def lines(self, lines: list[str]):
		self.__lines = lines
	
	def draw(self, s: Screenbuffer, clip: Rectangle | None = None):
		super().draw(s, clip=clip)
		
		# Since we chunk each line in `self.lines` into (potentially) multiple
		# lines so that it will fit on the screen, we can't just go by the
		# number of lines in `self.lines` when determining whether we've drawn
		# enough lines.
		drawn_lines = 0
		
		# Start at the bottom of the screen and draw upwards. Exit when we
		# reach the top.
		# 
		# We thus reverse the list of lines, and then reverse the list of chunks
		# for each line.
		for line in reversed(self.__lines):
			line_chunks = list(wcchunks(line, self._Widget__available_space.w))
			number_of_chunks = len(line_chunks)
			
			for i, chunk in enumerate(reversed(line_chunks)):
				# Is this line out of bounds?
				if drawn_lines + i >= self._Widget__available_space.h:
					return
				
				wc_offset = 0
				for character in chunk:
					wc_offset += s.set(
						self._Widget__available_space.x + wc_offset,
						self._Widget__available_space.y2 - i - drawn_lines,
						character,
						clip=clip,
					)
			
			drawn_lines += number_of_chunks
