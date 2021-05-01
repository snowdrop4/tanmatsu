from tri_declarative import declarative

from .base import Widget


# A widget that can have children widgets.
@declarative(Widget, 'children')
class Container(Widget):
	def __init__(self, children, *args, **kwargs):
		super(Container, self).__init__(*args, **kwargs)
		
		self.children = children
		
		# Used when changing widget focus with the `tab` key in `tanmatsu.py`.
		# 
		# If a subset of child widgets ought to be skipped when cycling focus
		# through child widgets then `active_children` must be assigned to a
		# new dictionary which excludes said widgets.
		# 
		# By default, this can be completely ignored unless the above
		# functionality is required.
		self.focusable_children = children
