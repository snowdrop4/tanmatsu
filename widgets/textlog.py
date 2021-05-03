from typing import Generator

from .box import Box
from screenbuffer import Screenbuffer
from geometry import Rectangle


def lines_to_wrap(string_length: int, line_length: int) -> int:
	return (string_length // line_length) + (1 if string_length % line_length else 0)


def chunks(text: str, line_length: int) -> Generator[str]:
	if text == "":
		yield ""
	else:
		for i in range(0, len(text), line_length):
			yield text[i:i + line_length]


class TextLog(Box):
	"""
	A widget that displays multiple lines of text, with new lines being added
	to the bottom and old ones scrolling upwards. Like a traditional terminal.
	
	:param lines: The lines the TextLog should contain.
	"""
	
	def __init__(self, *args, lines: list[str] = [], **kwargs):
		super().__init__(*args, **kwargs)
		
		self.lines = lines
	
	def append_line(self, line):
		"""Append a line to the TextLog."""
		self.lines.append(line)
	
	def get_lines(self) -> list[str]:
		"""Return the current contents of the TextLog."""
		return self.lines
	
	def set_lines(self, lines: list[str]):
		"""Set the contents of the TextLog."""
		self.lines = lines
	
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
		for line in reversed(self.lines):
			line_chunks = list(chunks(line, self._Widget__available_space.w))
			number_of_chunks = len(line_chunks)
			
			for i, chunk in enumerate(reversed(line_chunks)):
				# Is this line out of bounds?
				if drawn_lines + i >= self._Widget__available_space.h:
					return
				
				for j, character in enumerate(chunk):
					s.set(
						self._Widget__available_space.x + j,
						self._Widget__available_space.y2 - i - drawn_lines,
						character,
						clip=clip,
					)
			
			drawn_lines += number_of_chunks
