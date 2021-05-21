from tri_declarative import with_meta
from wcwidth import wcswidth

import tanmatsu.input as ti
from tanmatsu import draw, theme, debug
from tanmatsu.wctools import wccrop
from tanmatsu.screenbuffer import Screenbuffer
from tanmatsu.geometry import Rectangle, Dimensions, Point
from .base import Widget
from .container import Container


@with_meta
class TabBox(Container):
	"""Widget that contains other widgets, arranged as tabs."""
	
	def __init__(self, *args, active_tab: Widget | None = None, **kwargs):
		super().__init__(*args, **kwargs)
		
		if active_tab:
			v = self.children[active_tab]
			self.__active_tab = v
			self.focusable_children = { active_tab: v }
		else:
			k, v = list(self.children.items())[0]
			self.__active_tab = v
			self.focusable_children = { k: v }
		
		self.tab_min_label_width = 10
		self.tab_decoration_width = 2
		self.tab_min_width = self.tab_min_label_width + self.tab_decoration_width
	
	def layout(self, *args, **kwargs):
		super().layout(*args, **kwargs)
		
		# Work out how much space we get for each tab:
		tab_count = len(self.children)
		available_space = self._Widget__available_space.w - 2
		
		if tab_count * self.tab_min_width < available_space:
			self.__tab_width = available_space // tab_count
		else:
			self.__tab_width = self.tab_min_width
		
		# Mark out room for the tab bar:
		self.__tab_bar_rectangle = self._Widget__available_space.duplicate()
		self.__tab_bar_rectangle.h = 2
		
		self._Widget__available_space.y += 2
		self._Widget__available_space.h -= 2
		
		# Mark out room for the box attached to the bottom of the tab bar:
		self.__border_rectangle = self._Widget__available_space.duplicate()
		
		self._Widget__available_space.x += 1
		self._Widget__available_space.y += 1
		self._Widget__available_space.w -= 2
		self._Widget__available_space.h -= 2
		
		# Layout the active tab:
		self.__active_tab.layout(
			self._Widget__available_space.origin_point(),
			self._Widget__available_space.dimensions(),
			self._Widget__available_space.dimensions()
		)
	
	def draw(self, s: Screenbuffer, clip: Rectangle | None = None):
		super().draw(s, clip=clip)
		
		if self.focused:
			style = theme.DefaultTheme.focused
		else:
			style = None
		
		draw.rectangle(s, self.__border_rectangle, clip=clip, style=style)
		self.__active_tab.draw(s, clip=clip & self._Widget__available_space)
		
		for (i, (label, tab)) in enumerate(self.children.items()):
			if tab is self.__active_tab:
				style = theme.DefaultTheme.active
			else:
				style = theme.DefaultTheme.inactive
			
			tab_rectangle = Rectangle(
				self.__tab_bar_rectangle.x + (i * self.__tab_width) + 1,
				self.__tab_bar_rectangle.y,
				self.__tab_width,
				2
			)
			
			self.draw_tab(s, tab_rectangle, label, clip, style)
	
	def draw_tab(self, s, tab_rectangle, label, clip, style):
		def draw_pillar(x, top):
			s.set(x, tab_rectangle.y + 0, top, clip=clip, style=style)
			s.set(x, tab_rectangle.y + 1, "│", clip=clip, style=style)
			s.set(x, tab_rectangle.y + 2, "╧", clip=clip, style=style)
		
		# Draw the tab borders:
		draw_pillar(tab_rectangle.x1, "╭")
		draw_pillar(tab_rectangle.x2, "╮")
		
		for i in range(tab_rectangle.x1 + 1, tab_rectangle.x2):
			s.set      (i, tab_rectangle.y + 0, "─", clip=clip, style=style)
			s.set_style(i, tab_rectangle.y + 2, style, clip=clip)
		
		# Draw the tab labels:
		space_for_label = tab_rectangle.w - self.tab_decoration_width
		cropped_label = wccrop(label, space_for_label)
		
		wc_offset = 0
		for character in cropped_label:
			wc_offset += s.set(
				tab_rectangle.x1 + 1 + wc_offset,
				tab_rectangle.y + 1,
				character,
				clip=clip,
				style=style
			)
	
	def left(self):
		"""Switches tab to the left."""
		self.__switch_tab(list(reversed(self.children.items())))
	
	def right(self):
		"""Switches tab to the right."""
		self.__switch_tab(list(self.children.items()))
	
	def __switch_tab(self, c):
		for i, (k, v) in enumerate(c):
			if v is self.__active_tab:
				ak, av = c[0 if i + 1 == len(c) else i + 1]
				self.__active_tab = av
				self.focusable_children = { ak: av }
				break
		
		if self.focused_child is not None:
			self.focused_child = self.__active_tab
	
	def keyboard_event(
		self,
		key: ti.Keyboard_key,
		modifier: ti.Keyboard_modifier
	) -> bool:
		if super().keyboard_event(key, modifier):
			return True
		
		match key:
			case ti.Keyboard_key.PAGE_UP:
				self.left()
			case ti.Keyboard_key.PAGE_DOWN:
				self.right()
			case _:
				return False
		
		return True
