from abc import ABC, abstractmethod

import tanmatsu.input as ti
from tanmatsu import size, theme
from tanmatsu.screenbuffer import Screenbuffer
from tanmatsu.geometry import Rectangle, Dimensions, Point


class Widget(ABC):
	"""
	Abstract base class. Parent class of all widgets.
	
	:param w: used for calculating the width of this widget.
	:paramtype w: tanmatsu.size.SizeResolver
	
	:param h: used for calculating the height of this widget.
	:paramtype h: tanmatsu.size.SizeResolver
	
	:param theme: used for calculating the theme controlling the
	              styles used to draw this widget.
	:paramtype theme: tanmatsu.theme.Theme
	"""
	
	def __init__(
		self,
		w: size.SizeResolver = size.ParentRequested(),
		h: size.SizeResolver = size.ParentRequested(),
		theme: theme.Theme = theme.DefaultTheme(),
	):
		self.w = w
		self.h = h
		self.theme = theme
		
		self.focused = False
		self.focused_child = None
		
		self.__calculated_size = None
		self.__available_space = None
	
	def get_min_size(self, parent_size: Dimensions) -> Dimensions:
		"""
		Returns the minimum possible size that the widget could resolve to
		  when :meth:`layout` is called.
		"""
		return Dimensions(self.w.min(parent_size.w), self.h.min(parent_size.h))
	
	def get_max_size(self, parent_size: Dimensions) -> Dimensions:
		"""
		Returns the maximum possible size that the widget could resolve to
		  when :meth:`layout` is called.
		"""
		return Dimensions(self.w.max(parent_size.w), self.h.max(parent_size.h))
	
	def get_actual_size(
		self,
		parent_size: Dimensions,
		requested_size: Dimensions
	) -> Dimensions:
		"""
		Returns the actual size that the widget will resolve to
		  when :meth:`layout` is called.
		"""
		return Dimensions(
			self.w.resolve(parent_size.w, requested_size.w),
			self.h.resolve(parent_size.h, requested_size.h),
		)
	
	def layout(
		self,
		position: Point,
		parent_size: Dimensions,
		requested_size: Dimensions
	):
		"""
		Calculates the widget layout. Will be called before every :meth:`draw`.
		
		:param position: The location of this widget in space.
		:paramtype position: Point
		
		:param parent_size: The size of the parent widget. Used when resolving
		                    sizes. See the classes in module :mod:`size`.
		:paramtype parent_size: Dimensions
		
		:param requested_size: The size that the parent widget requests this
		                       widget to be. Used when resolving sizes.
		                       See the classes in module :mod:`size`.
		:paramtype requested_size: Dimensions
		"""
		size = self.get_actual_size(parent_size, requested_size)
		
		# The actual size of the widget.
		self.__calculated_size = Rectangle(position.x, position.y, size.w, size.h)
		
		# The remaining space after subtracting decorations,
		#   like scrollbars or borders.
		self.__available_space = Rectangle(position.x, position.y, size.w, size.h)
	
	@abstractmethod
	def draw(self, s: Screenbuffer, clip: Rectangle | None = None):
		"""
		Draws the widget to the given screenbuffer.
		
		:param screenbuffer: The Screenbuffer to draw to.
		:paramtype screenbuffer: Screenbuffer
		
		:param clip: An area, outside of which, this widget should not be drawn.
		:paramtype clip: Rectangle
		
		.. note::
		   If a widget has child widgets, it must make sure to pass the correct
		   clip to them when drawing.
		   
		   The widget must pass :attr:`self._Widget__available_space` to the
		   :meth:`geometry.Rectangle.__and__` method of the clip it
		   receives, and then pass the resulting clip to the child widget when
		   calling :meth:`draw` on it, so that the clips correctly combine and
		   propogate down the chain.
		"""
		pass
	
	def mouse_event(
		self,
		button: ti.Mouse_button,
		modifier: ti.Mouse_modifier,
		state: ti.Mouse_state,
		position: Point
	) -> bool:
		"""
		Process a mouse event.
		
		:return:
		  `True`: Treat the mouse event as consumed. Do not pass the mouse
		  event to other widgets after this one.
		
		  `False`: Treat the mouse event as ignored. Pass the mouse event
		  to other widgets after this one.
		"""
		return False
	
	def keyboard_event(
		self,
		key: ti.Keyboard_key | str,
		modifier: ti.Keyboard_modifier
	) -> bool:
		"""
		Process a keyboard event.
		
		:param key: Either a string indicating the character entered,
		            or a enum indicating the special key pressed
		            (e.g., ENTER, TAB, HOME, and so on).
		:paramtype key: tanmatsu.input.Keyboard_key | str
		
		:param modifier: A bitmask indicating the modifier key held down,
		                 if any.
		:paramtype modifier: tanmatsu.input.Keyboard_modifier
		
		:return:
		  `True`: Treat the keyboard event as consumed. Do not pass the keyboard
		  event to other widgets after this one.
		
		  `False`: Treat the keyboard event as ignored. Pass the keyboard event
		  to other widgets after this one.
		"""
		return False
