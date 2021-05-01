from tri_declarative import with_meta

import draw
import geometry
import theme
import terminal.input as ti
import debug
from .container import Container


@with_meta
class TabBox(Container):
	def __init__(self, *args, active_tab=None, **kwargs):
		super().__init__(*args, **kwargs)
		
		if active_tab:
			v = self.children[active_tab]
			self.__active_tab = v
			self.focusable_children = { active_tab: v }
		else:
			k, v = list(self.children.items())[0]
			self.__active_tab = v
			self.focusable_children = { k: v }
	
	def layout(self, x, y, parent_w, parent_h, requested_w, requested_h):
		super().layout(x, y, parent_w, parent_h, requested_w, requested_h)
		
		tab_count = len(self.children)
		min_tab_width = 5
		total_decoration_length = tab_count * 2
		available_space = self._Widget__available_space.w - 2
		self.__tab_width = (tab_count * min_tab_width) + total_decoration_length
		
		if self.__tab_width <= available_space:
			self.__tab_width = int((available_space - total_decoration_length) / tab_count)
		
		self.__tab_rectangle = geometry.Rectangle(
			self._Widget__available_space.x,
			self._Widget__available_space.y,
			self.__tab_width * tab_count,
			2
		)
		
		self._Widget__available_space.y += 2
		self._Widget__available_space.h -= 2
		
		self.__border_rectangle = self._Widget__available_space.duplicate()
		
		self._Widget__available_space.x += 1
		self._Widget__available_space.y += 1
		self._Widget__available_space.w -= 2
		self._Widget__available_space.h -= 2
		
		self.__active_tab.layout(
			self._Widget__available_space.x,
			self._Widget__available_space.y,
			self._Widget__available_space.w,
			self._Widget__available_space.h,
			self._Widget__available_space.w,
			self._Widget__available_space.h
		)
	
	def draw(self, s, clip=None):
		super().draw(s, clip=clip)
		
		if self.focused:
			style = theme.DefaultTheme.highlight
		else:
			style = None
		
		draw.rectangle(s, self.__border_rectangle, clip=clip, style=style)
		
		def draw_pillar(top):
			s.set(current_x, self.__tab_rectangle.y,     top, clip=clip, style=style)
			s.set(current_x, self.__tab_rectangle.y + 1, "│", clip=clip, style=style)
			s.set(current_x, self.__tab_rectangle.y + 2, "╧", clip=clip, style=style)
		
		current_x = self.__tab_rectangle.x
		for i, (k, v) in enumerate(self.children.items()):
			if self.__active_tab is v:
				style = theme.DefaultTheme.tab_active
			else:
				style = theme.DefaultTheme.tab_inactive
			
			current_x += 1
			draw_pillar("╭")
			current_x += 1
			
			for j in range(min(self.__tab_width, len(k))):
				s.set(current_x, self.__tab_rectangle.y,      "─", clip=clip, style=style)
				s.set(current_x, self.__tab_rectangle.y + 1, k[j], clip=clip, style=style)
				s.set_style(current_x, self.__tab_rectangle.y + 2, style, clip=clip)
				current_x += 1
			
			draw_pillar("╮")
		
		self.__active_tab.draw(s, clip=clip.overlap_rectangle(self._Widget__available_space))
	
	def left(self):
		self.__switch_tab(list(reversed(self.children.items())))
	
	def right(self):
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
	
	def keyboard_event(self, key, modifier):
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
