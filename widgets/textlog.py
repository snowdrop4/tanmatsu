import typing

from .box import Box


def lines_to_wrap(string_length: int, line_length: int) -> int:
	return (string_length // line_length) + (1 if string_length % line_length else 0)


def chunks(text: str, line_length: int) -> typing.Generator[str, None, None]:
	if text == "":
		yield ""
	else:
		for i in range(0, len(text), line_length):
			yield text[i:i + line_length]


# A widget that displays multiple lines of text, with new lines
# being added to the bottom and old ones scrolling upwards.
class TextLog(Box):
	def __init__(self, *args, lines=[], **kwargs):
		super().__init__(*args, **kwargs)
		
		self.lines = lines
	
	def add_line(self, line):
		self.lines.append(line)
	
	def draw(self, s, clip=None):
		super().draw(s, clip=clip)
		
		# Since we chunk each line in `self.lines` into (potentially) multiple
		# lines so that it will fit on the screen, we can't just go by the
		# number of lines in `self.lines`.
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
				for j, character in enumerate(chunk):
					s.set(
						self._Widget__available_space.x + j,
						self._Widget__available_space.y2 - i - drawn_lines,
						character,
						clip=clip,
					)
				
				# Would the next line chunk we'd draw be out of bounds?
				if drawn_lines + i + 1 >= self._Widget__available_space.h:
					return
			
			drawn_lines += number_of_chunks
