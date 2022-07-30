from tri_declarative import with_meta

import tanmatsu.input as ti
from tanmatsu.screenbuffer import Screenbuffer
from tanmatsu.geometry import Rectangle, Dimensions, Point
from .base import Widget
from .box import Box
from .scrollable import Scrollable


@with_meta
class List(Box, Scrollable):
	"""
	Widget that holds a number of widgets of a uniform height, with
	a cursor to navigate between them.
	
	:param children: The widgets the List should contain.
	:paramtype children: list[Widget]
	"""
	
	def __init__(self,  *args, children: list[Widget], item_height: int, **kwargs):
		super().__init__(*args, **kwargs)
		
		self._children = children
		self.cursor = 0
		
		self.item_height = item_height
	
	@property
	def cursor(self) -> int:
		"""
		:getter: Get cursor location, i.e., the index of the
		         currently selected child.
		:setter: Set the cursor location.
		"""
		return self.__cursor
	
	@cursor.setter
	def cursor(self, value: int):
		value = max(value, 0)
		value = min(value, len(self.children))
		self.__cursor = value
		
		self.focused_child = self.children[self.cursor]
		self.focusable_children = { "_": self.focused_child }
		
		if self._Widget__available_space is not None:
			active_item_y1 = self._Widget__available_space.y1 +  self.cursor      * self.item_height
			active_item_y2 = self._Widget__available_space.y1 + (self.cursor + 1) * self.item_height
			
			delta_y = 0
			
			if active_item_y1 < self.viewport.y1:
				delta_y = active_item_y1 - self.viewport.y1
			if active_item_y2 > self.viewport.y2:
				delta_y = active_item_y2 - self.viewport.y2 - 1
			
			self.scroll(None, delta_y=delta_y)
	
	@property
	def children(self) -> list[Widget]:
		"""
		:getter: Get the children, i.e., the list items.
		:setter: Set the children.
		"""
		return self._children
	
	@children.setter
	def children(self, value: list[Widget]):
		self._children = value
		self.cursor = min(self.cursor, len(value))
	
	@property
	def active_child(self) -> Widget:
		"""
		:getter: Get the currently active child widget (i.e., the widget that
		         the cursor is currently pointing to).
		"""
		return self.children[self.cursor]
	
	def up(self):
		"""
		Move the cursor up.
		"""
		self.cursor = max(self.cursor - 1, 0)
	
	def down(self):
		"""
		Move the cursor down.
		"""
		self.cursor = min(self.cursor + 1, len(self.children) - 1)
	
	def layout(self, *args, **kwargs):
		super().layout(*args, **kwargs)
		
		# Gutter
		# ‾‾‾‾‾‾
		
		# Reserve space for a gutter in order to draw the cursor there.
		# 
		# First, record the space we want the gutter to occupy (to be used as a
		#   clip when drawing said gutter later).
		# Second, modify `self._Widget__available_space` to compensate.
		self.gutter = Rectangle(
			self._Widget__available_space.x,
			self._Widget__available_space.y,
			1,
			self._Widget__available_space.h,
		)
		
		self._Widget__available_space.x += 1
		self._Widget__available_space.w -= 1
		
		# Calculating usable space
		# ‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾
		content_size = Dimensions(
			self._Widget__available_space.w - 1,
			len(self.children) * self.item_height
		)
		
		usable_space = self.get_scrollable_area(content_size)
		
		# Children
		# ‾‾‾‾‾‾‾‾
		for (i, v) in enumerate(self.children):
			position = Point(
				usable_space.x - self._Scrollable__scroll_position.x,
				usable_space.y - self._Scrollable__scroll_position.y + (i * self.item_height)
			)
			
			size = Dimensions(
				usable_space.w,
				self.item_height,
			)
			
			v.layout(position, size, size)
		
		# Scroll bar
		# ‾‾‾‾‾‾‾‾‾‾
		self.layout_scrollbar(content_size)
		self.scroll()
	
	def draw(self, s: Screenbuffer, clip: Rectangle | None = None):
		super().draw(s, clip=clip)
		
		for (i, v) in enumerate(self.children):
			item_clip = Rectangle(
				self._Widget__available_space.x - self._Scrollable__scroll_position.x,
				self._Widget__available_space.y - self._Scrollable__scroll_position.y + (i * self.item_height),
				self._Widget__available_space.w,
				self.item_height,
			)
			
			v.draw(s, clip=clip & item_clip & self._Widget__available_space)
			
			if i == self.cursor:
				for j in range(0, self.item_height):
					s.set(
						self.gutter.x,
						item_clip.y + j,
						">",
						clip=clip & self.gutter
					)
	
	def keyboard_event(
		self,
		key: ti.Keyboard_key | str,
		modifier: ti.Keyboard_modifier
	) -> bool:
		if super().keyboard_event(key, modifier):
			return True
		
		match key:
			case ti.Keyboard_key.UP_ARROW:
				self.up()
			case ti.Keyboard_key.DOWN_ARROW:
				self.down()
			case _:
				return False
		
		return True
