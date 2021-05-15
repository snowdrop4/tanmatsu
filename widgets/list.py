from tri_declarative import with_meta

from .box import Box
from .scrollable import Scrollable
from geometry import Rectangle, Dimensions, Point
from screenbuffer import Screenbuffer
import terminal.input as ti


@with_meta
class List(Box, Scrollable):
	"""
	Widget that holds a number of widgets of a uniform height, with
	a cursor to navigate between them.
	
	:ivar items: Child widgets.
	:vartype items: list[Widget]
	
	:ivar cursor: Cursor position.
	:vartype cursor: int
	"""
	
	def __init__(self, items: list, item_height: int, *args, **kwargs):
		super().__init__(*args, **kwargs)
		
		self._items = items
		self._cursor = 0
		
		self.item_height = item_height
	
	@property
	def cursor(self):
		return self._cursor
	
	@cursor.setter
	def cursor(self, value):
		value = max(value, 0)
		value = min(value, len(self.items))
		self._cursor = value
		
		self.focused_child = self.items[self.cursor]
		self.focusable_children = { "_": self.focused_child }
	
	@property
	def items(self):
		return self._items
	
	@items.setter
	def items(self, value):
		self._items = value
		self.cursor = min(self.cursor, len(value))
	
	def up(self):
		self.cursor = max(self.cursor - 1, 0)
	
	def down(self):
		self.cursor = min(self.cursor + 1, len(self.items) - 1)
	
	def layout(self, *args, **kwargs):
		super().layout(*args, **kwargs)
		
		# Reserve space for a gutter in order to draw the cursor there.
		# First, record the space we want the gutter to occupy (to be used as a
		# clip when drawing), and then modify `self._Widget__available_space`
		# to compensate.
		self.gutter = Rectangle(
			self._Widget__available_space.x,
			self._Widget__available_space.y,
			1,
			self._Widget__available_space.h,
		)
		
		self._Widget__available_space.x += 1
		self._Widget__available_space.w -= 1
		
		# Layout the items
		for (i, v) in enumerate(self.items):
			position = Point(
				self._Widget__available_space.x - self._Scrollable__scroll_position.x,
				self._Widget__available_space.y - self._Scrollable__scroll_position.y + (i * self.item_height)
			)
			
			size = Dimensions(
				self._Widget__available_space.w,
				self.item_height,
			)
			
			v.layout(position, size, size)
		
		self.scroll(Dimensions(
			self._Widget__available_space.w,
			len(self.items) * self.item_height
		))
	
	def draw(self, s: Screenbuffer, clip: Rectangle | None = None):
		super().draw(s, clip)
		
		for (i, v) in enumerate(self.items):
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
						"*",
						clip=clip & self.gutter
					)
	
	def keyboard_event(
		self,
		key: ti.Keyboard_key,
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
