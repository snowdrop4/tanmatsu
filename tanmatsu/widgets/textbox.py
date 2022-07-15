from typing import Generator
import itertools

from tri_declarative import with_meta

import tanmatsu.input as ti
from tanmatsu import theme, debug
from tanmatsu.wctools import wcslice, wcfind, wcoffset_to_column, wccolumn_to_offset, wcwrap, wcchunks
from tanmatsu.geometry import Rectangle, Dimensions, Point
from tanmatsu.screenbuffer import Screenbuffer
from .box import Box
from .scrollable import Scrollable


# Given a string, generates a series of tuples of type (str, str).
# 
# 
# First string in the tuple:
# ‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾
# A wrapped line.
# 
# Will be at most `max_width` long. If it is not the last line, it will contain
# a \n at the end. The last line may or may not have a \n at the end.
# 
# If the last line ends in a \n, or if the last line doesn't end in a \n but is
# the exact wrap width, adds an line containing a single space character after
# the last line.
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
# ‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾
# The gutter character corresponding to the wrapped line.
#
# If the line is wrapped, the gutter character will be set to "⮷".
# If the line isn't wrapped, the gutter character will be " ".
def wrap(text: str, max_width: int) -> Generator[tuple[str, str], None, None]:
	if len(text) == 0:
		yield (" ", " ")
		return
	
	i = 0
	
	while i < len(text):
		newline = wcfind(text, "\n", i, i + max_width)
		
		if newline == -1:
			if i + max_width == len(text):  # last line ending exactly at the wrap width, with no "\n"
				yield (text[i:], "⮷")
				yield (" ", " ")  # cursor needs to be able to occupy the next line as this line is the exact wrap width
				break
			if i + max_width > len(text):  # last line ending before the wrap width, with no "\n"
				yield (text[i:] + " ", " ")
				break
			else:  # normal wrapped line
				yield (wcslice(text[i:], max_width), "⮷")
				i += max_width
		else:
			if newline + 1 == len(text):  # last line ending exactly at the wrap width, with a "\n"
				yield (text[i:], " ")
				yield (" ", " ")  # cursor needs to be able to occupy the next line as this line is the exact wrap width
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
	
	:ivar cursor: The position of the cursor.
	:vartype cursor: int
	
	:ivar text: The text the TextBox should contain.
	:vartype text: str
	
	:ivar editable: Whether the TextBox should be editable or not.
	:vartype editable: bool
	"""
	
	def __init__(self, *args, text: str = "", editable: bool = True, **kwargs):
		super().__init__(*args, **kwargs)
		
		self._cursor = 0
		self._text = text
		self.editable = editable
		
		self.__cached_text = text
		self.__cached_wrap_width = 0
	
	@property
	def cursor(self):
		return self._cursor
	
	@cursor.setter
	def cursor(self, value: int):
		value = max(0, value)
		value = min(len(self.text), value)
		
		diff = value - self._cursor
		self._cursor = value
		
		# Scroll the widget until the cursor is in view:
		if self._Widget__available_space is not None:
			# Find what line the cursor is on:
			characters_seen = 0
			cursor_line = 0
			
			for (i, v) in enumerate(map(lambda x: len(x[0]), self.wrapped)):
				if characters_seen + v > self._cursor:
					break
				cursor_line += 1
				characters_seen += v
			
			# Find the extent of the lines visible on the screen:
			start_line = self._Scrollable__scroll_position.y
			end_line   = self._Scrollable__scroll_position.y + self._Widget__available_space.h - 1
			
			# Work out the positive or negative difference between the line the
			# line the cursor is on, and the topmost or bottommost visible line:
			delta_y = 0
			
			if cursor_line < start_line:
				delta_y = cursor_line - start_line
			
			if cursor_line > end_line:
				delta_y = cursor_line - end_line
			
			self.scroll(None, delta_y=delta_y)
	
	@property
	def text(self):
		return self._text
	
	@text.setter
	def text(self, value: str):
		self._text = value
		self.cursor = min(self.cursor, len(self.text))
	
	@property
	def wrap_width(self):
		return self._Widget__available_space.w - 1
	
	@property
	def wrapped(self):
		# Optimisation: only re-wrap the text when it's actually necessary:
		if (
			   self.__cached_text       != self.text
			or self.__cached_wrap_width != self.wrap_width
		):
			self._wrapped = list(wrap(self.text, self.wrap_width))
			self.__cached_text = self.text
			self.__cached_wrap_width = self.wrap_width
		
		return self._wrapped
	
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
	
	def line_wrap_info(self, c1: int, c2: int) -> tuple[[str], int, int]:
		# Wrap the line we're given. Add a " " on the end if it's the last line
		# and doesn't end in a "\n", like the `wrap` function does.
		if c2 == len(self.text) and self.text[-1] != "\n":
			wrapped = list(wcchunks(self.text[c1:c2] + " ", self.wrap_width))
		else:
			wrapped = list(wcchunks(self.text[c1:c2], self.wrap_width))
		
		# Find which subline we're on, and the start of that subline.
		line_start = c1
		subline_num = 0
		for (subline_num, line_length) in enumerate(map(len, wrapped)):
			if self.cursor >= line_start and self.cursor < line_start + line_length:
				break
			line_start += line_length
		
		subline_offset = self.cursor - line_start
		
		return (wrapped, subline_num, subline_offset)
	
	def up(self):
		(c1, c2) = self.curr_line()
		(c_wrapped, c_subline_num, c_subline_offset) = self.line_wrap_info(c1, c2)
		
		# If we're in a wrapped line, move inside the line:
		if c_subline_num > 0:
			column = wcoffset_to_column(c_wrapped[c_subline_num],     c_subline_offset)
			offset = wccolumn_to_offset(c_wrapped[c_subline_num - 1], column)
			
			self.cursor = self.cursor - c_subline_offset - len(c_wrapped[c_subline_num - 1]) + offset
		# If we're on the first line, move the cursor to the start:
		elif c1 == 0:
			self.cursor = 0
		# Else move into the previous line:
		else:
			(p1, p2) = self.prev_line()
			(p_wrapped, p_subline_num, p_subline_offset) = self.line_wrap_info(p1, p2)
			
			column = wcoffset_to_column(c_wrapped[c_subline_num], c_subline_offset)
			offset = wccolumn_to_offset(p_wrapped[-1], column)
			
			self.cursor = self.cursor - c_subline_offset - len(p_wrapped[-1]) + offset
	
	def down(self):
		(c1, c2) = self.curr_line()
		(c_wrapped, c_subline_num, c_subline_offset) = self.line_wrap_info(c1, c2)
		
		# If we're in a wrapped line, move inside the line:
		if c_subline_num < len(c_wrapped) - 1:
			column = wcoffset_to_column(c_wrapped[c_subline_num],     c_subline_offset)
			offset = wccolumn_to_offset(c_wrapped[c_subline_num + 1], column)
			
			self.cursor = self.cursor - c_subline_offset + len(c_wrapped[c_subline_num]) + offset
		# If we're on the last line, move the cursor to the end:
		elif c2 == len(self.text):
			self.cursor = c2
		# Else move into the next line:
		else:
			(n1, n2) = self.next_line()
			(n_wrapped, n_subline_num, n_subline_offset) = self.line_wrap_info(n1, n2)
			
			column = wcoffset_to_column(c_wrapped[c_subline_num], c_subline_offset)
			offset = wccolumn_to_offset(n_wrapped[0], column)
			
			self.cursor = self.cursor - c_subline_offset + len(c_wrapped[c_subline_num]) + offset
	
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
	
	def layout(self, *args, **kwargs):
		super().layout(*args, **kwargs)
		
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
			
			# Draw the line
			wc_offset = 0
			for character in line:
				# If we attempt to draw this character, it screws up the screen.
				# Turn it into a space character instead of skipping this
				# character entirely, as although both \n and ' ' are
				# non-visible, this position in the text box is a potentially
				# valid space for the cursor to occupy.
				if character == "\n":
					character = " "
				
				# If we're on the character the cursor is currently occupying,
				# set the theme appropriately.
				if self.editable and self.cursor == characters_seen:
					style = theme.DefaultTheme.cursor
				else:
					style = None
				
				wc_offset += s.set(
					self._Widget__available_space.x + wc_offset,
					y,
					character,
					clip=clip,
					style=style
				)
				
				characters_seen += 1
			
			# Draw the gutter character
			s.set(
				self._Widget__available_space.x2,
				y,
				gutter,
				clip=clip,
				style=None
			)

	
	def keyboard_event(
		self,
		key: ti.Keyboard_key,
		modifier: ti.Keyboard_modifier
	) -> bool:
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
