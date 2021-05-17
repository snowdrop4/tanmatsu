import typing
import itertools

from tri_declarative import with_meta

import terminal.input as ti
import theme
import debug
from .box import Box
from .scrollable import Scrollable
from geometry import Rectangle, Dimensions, Point
from screenbuffer import Screenbuffer


# Given a string, generates a series of tuples of type (str, str).
# 
# 
# First string in the tuple:
# 
# A wrapped line.
# 
# Will be at most `max_width` long. If it is not the last line, it will contain
# a \n at the end. The last line may or may not have a \n at the end.
# 
# Adds an blank line containing a single space character after the last line
# if the last line ends in a \n. If it doesn't end in an \n, adds a single space
# character to the end of it instead.
# 
# We need to guarantee that there's space for the cursor to inhabit after the
# last line. Adding a space character makes drawing the cursor vastly more
# simple, as we can simply iterate over all the characters in the lines returned
# by this function and set the style on the character drawn to the cursor style
# if the cursor is on top of that character.
# 
# This means we don't need to add a special case when drawing the cursor if it
# happens to be positioned after the last character in the text.
# 
# 
# Second string in the tuple:
# 
# The gutter character corresponding to the wrapped line.
#
# If the line is wrapped, the gutter character will be set to "⮷".
# If the line isn't wrapped, the gutter character will be " ".
def wrap(text: str, max_width: int) -> typing.Generator[(str, str), None, None]:
	i = 0
	
	while i < len(text):
		newline = text.find("\n", i, i + max_width)
		
		if newline == -1:
			if i + max_width == len(text):  # last line not ending with a "\n"
				yield (text[i:], "⮷")
				yield (" ", " ")  # the cursor needs to be able to occupy the next line as this line is the exact wrap width
				break
			if i + max_width > len(text):  # last line not ending with a "\n"
				yield (text[i:] + " ", " ")
				break
			else:  # normal wrapped line
				yield (text[i:i + max_width], "⮷")
				i += max_width
		else:
			if newline + 1 == len(text):  # last line ending with a "\n"
				yield (text[i:newline + 1], " ")
				yield (" ", " ")  # cursor needs to be able to occupy the next line as this line ends in a "\n"
				break
			else:  # normal line ending with a "\n"
				yield (text[i:newline + 1], " ")
				i = newline + 1


@with_meta
class TextBox(Box, Scrollable):
	"""
	Widget containing editable or non-editable text.
	
	:param text: The text the TextBox should contain.
	:param editable: Whether the TextBox should be editable or not.
	"""
	
	def __init__(self, *args, text: str = "", editable: bool = True, **kwargs):
		super().__init__(*args, **kwargs)
		
		self.cursor = 0
		self.text = text
		self.editable = editable
	
	@property
	def wrap_width(self):
		return self._Widget__available_space.w - 1
	
	def get_text(self) -> str:
		"""Return the current contents of the TextBox."""
		return self.text
	
	def set_text(self, text: str):
		"""Set the contents of the TextBox."""
		self.text = text
		
		self.cursor = min(self.cursor, len(self.text))
	
	def curr_line(self) -> tuple[int, int]:
		start = self.text.rfind("\n", 0, self.cursor)
		end = self.text.find("\n", self.cursor)
		
		if start == -1:
			start = 0
		else:
			start += 1  # +1 so it excludes the matched "\n" from the previous line
		
		if end == -1:
			end = len(self.text)
		else:
			end += 1  # +1 so it includes the matched "\n" in this line
		
		return (start, end)
	
	def next_line(self) -> tuple[int, int] | None:
		end_of_current = self.text.find("\n", self.cursor)
		
		if end_of_current == -1:
			return None
		
		start = end_of_current + 1
		end = self.text.find("\n", start)
		
		if end == -1:
			end = len(self.text)
		else:
			end += 1  # +1 so it includes the matched "\n"
		
		return (start, end)
	
	def prev_line(self) -> tuple[int, int] | None:
		end = self.text.rfind("\n", 0, self.cursor)
		
		if end == -1:
			return None
		
		start = self.text.rfind("\n", 0, end)
		
		# +1 to the start so it excludes the matched "\n", and +1 to the end so
		# it includes the matched "\n"
		return (start + 1, end + 1)
	
	def up(self):
		c = (c1, c2) = self.curr_line()
		
		c_length = c2 - c1 - 1  # length of current line
		c_offset = self.cursor - c1  # offset of the cursor relative to the start of the current line
		c_wrapped_line_count = c_length // self.wrap_width  # number of lines the current line was wrapped into
		c_depth_into_wrapped_line = c_offset // self.wrap_width  # our position inside the wrapped line
		c_wrapped_offset = c_offset - (c_depth_into_wrapped_line * self.wrap_width)  # offset of the cursor relative to the start of the current wrapped line
		
		# If we're in a wrapped line, move inside the line:
		if c_depth_into_wrapped_line > 0:
			self.cursor -= self.wrap_width
		# If we're on the first line, move the cursor to the start:
		elif c1 == 0:
			self.cursor = 0
		# Else move into the previous line:
		else:
			p = (p1, p2) = self.prev_line()
			p_length = p2 - p1 - 1
			p_wrapped_line_count = p_length // self.wrap_width
			
			self.cursor = min(
				p1 + (p_wrapped_line_count * self.wrap_width) + c_wrapped_offset,
				p2 - 1  # -1 since p2 indicates the character after the last
			)
	
	def down(self):
		c = (c1, c2) = self.curr_line()
		
		c_length = c2 - c1 - 1  # length of current line
		c_offset = self.cursor - c1  # offset of the cursor relative to the start of the current line
		c_wrapped_line_count = c_length // self.wrap_width  # number of lines the current line was wrapped into
		c_depth_into_wrapped_line = c_offset // self.wrap_width  # our position inside the wrapped line
		c_wrapped_offset = c_offset - (c_depth_into_wrapped_line * self.wrap_width)  # offset of the cursor relative to the start of the current wrapped line
		
		# If we're in a wrapped line, move inside the line:
		if c_depth_into_wrapped_line < c_wrapped_line_count:
			self.cursor = min(
				self.cursor + self.wrap_width,
				c2 - 1  # -1 since c2 indicates the character after the last
			)
		# If we're on the last line, move the cursor to the end:
		elif c2 == len(self.text):
			self.cursor = c2
		# Else move into the next line:
		else:
			n = (n1, n2) = self.next_line()
			self.cursor = min(
				n1 + c_wrapped_offset,
				n2 - 1  # -1 since n2 indicates the character after the last
			)
	
	def left(self):
		self.cursor = max(self.cursor - 1, 0)
	
	def right(self):
		self.cursor = min(self.cursor + 1, len(self.text))
	
	def home(self):
		(c1, _) = self.curr_line()
		self.cursor = c1
	
	def end(self):
		(_, c2) = self.curr_line()
		
		if len(self.text) == c2:
			self.cursor = c2
		else:
			self.cursor = c2 - 1
	
	def character(self, c: str):
		self.text = self.text[:self.cursor] + c + self.text[self.cursor:]
		self.cursor += 1
	
	def backspace(self):
		if self.cursor > 0:
			self.text = self.text[:self.cursor - 1] + self.text[self.cursor:]
			self.cursor -= 1
	
	def delete(self):
		if self.cursor < len(self.text):
			self.text = self.text[:self.cursor] + self.text[self.cursor + 1:]
	
	def keyboard_event(self, key: ti.Keyboard_key, modifier: int) -> bool:
		if super().keyboard_event(key, modifier):
			return True
		
		if self.editable is False:
			return False
		
		match key:
			case ti.Keyboard_key.ENTER:
				self.character("\n")
			case ti.Keyboard_key.BACKSPACE:
				self.backspace()
			case ti.Keyboard_key.DELETE:
				self.delete()
			case ti.Keyboard_key.UP_ARROW:
				self.up()
			case ti.Keyboard_key.DOWN_ARROW:
				self.down()
			case ti.Keyboard_key.LEFT_ARROW:
				self.left()
			case ti.Keyboard_key.RIGHT_ARROW:
				self.right()
			case ti.Keyboard_key.HOME:
				self.home()
			case ti.Keyboard_key.END:
				self.end()
			case c if not isinstance(c, ti.Keyboard_key):
				self.character(c)
			case _:
				return False
			
		return True
	
	def layout(self, *args, **kwargs):
		super().layout(*args, **kwargs)
		
		self.wrapped = list(wrap(self.text, self.wrap_width))
		
		content_size = Dimensions(self._Widget__available_space.w, len(self.wrapped))
		self.scroll(content_size)
	
	def draw(self, s: Screenbuffer, clip: Rectangle | None = None):
		super().draw(s, clip=clip)
		
		start_line = self._Scrollable__scroll_position.y
		end_line   = self._Scrollable__scroll_position.y + self._Widget__available_space.h
		
		# We need to keep track of all characters, skipped or not, so we know
		# where the cursor is.
		characters_seen = sum(map(lambda x: len(x[0]), self.wrapped[:start_line]))
		
		for (i, (line, gutter)) in enumerate(self.wrapped[start_line:end_line]):
			y = self._Widget__available_space.y + i
			
			# Skip non-visible lines
			if (
				y < self._Widget__available_space.y1 or
				y > self._Widget__available_space.y2
			):
				characters_seen += len(line)
				continue
			
			for (j, character) in enumerate(line):
				x = self._Widget__available_space.x + j
				
				# If we attempt to draw this character, it screws up the screen.
				# Just turn it into a space, since it's meant to not be visible,
				# but it is nevertheless a valid space for the cursor to occupy.
				if character == "\n":
					character = " "
				
				# If we're on the character the cursor occupies,
				# set the theme appropriately.
				if self.editable and self.cursor == characters_seen:
					style = theme.DefaultTheme.cursor
				else:
					style = None
				
				s.set(x, y, character, clip=clip, style=style)
				
				characters_seen += 1
			
			s.set(
				self._Widget__available_space.x2,
				y,
				gutter,
				clip=clip,
				style=None
			)
