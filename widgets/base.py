import geometry
import theme
import size


# Base widget class. Doesn't do much on its own. Parent class of all widgets.
class Widget():
	def __init__(
		self,
		w=size.ParentRequested(),
		h=size.ParentRequested(),
		theme=theme.DefaultTheme(),
	):
		self.w = w
		self.h = h
		self.theme = theme
		
		self.focused = False
		self.focused_child = None
		
		self.__calculated_size = None
		self.__available_space = None
	
	def get_min_size(self, parent_w, parent_h):
		return (self.w.min(parent_w), self.h.min(parent_h))
	
	def get_max_size(self, parent_w, parent_h):
		return (self.w.max(parent_w), self.h.max(parent_h))
	
	def get_actual_size(self, parent_w, parent_h, requested_w, requested_h):
		return (
			self.w.resolve(parent_w, requested_w),
			self.h.resolve(parent_h, requested_h),
		)
	
	def layout(self, x, y, parent_w, parent_h, requested_w, requested_h):
		(w, h) = self.get_actual_size(parent_w, parent_h, requested_w, requested_h)
		
		# The actual size of the widget.
		self.__calculated_size = geometry.Rectangle(x, y, w, h)
		
		# The remaining space after subtracting decorations,
		# like scrollbars or borders.
		self.__available_space = geometry.Rectangle(x, y, w, h)
	
	# If a widget has child widgets, it must make sure to give the correct clip
	# to them when drawing.
	# 
	# It must call `clip.overlap_rectangle(self._Widget__available_space)`,
	# and then pass the resulting clip to the child widget, so that the clips
	# correctly propogate down the chain.
	def draw(self, s, clip=None):
		pass
	
	# True:  Treat the mouse event as consumed. Do not pass the mouse
	#        event to other widgets after this one.
	# 
	# False: Treat the mouse event as ignored. Pass the mouse event to
	#        other widgets after this one.
	def mouse_event(self, button, x, y, button_state):
		return False
	
	# True:  Treat the keyboard event as consumed. Do not pass the keyboard
	#        event to other widgets after this one.
	# 
	# False: Treat the keyboard event as ignored. Pass the keyboard event to
	#        other widgets after this one.
	def keyboard_event(self, key, modifier):
		return False
