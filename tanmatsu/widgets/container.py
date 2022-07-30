from tri_declarative import declarative

from .base import Widget


@declarative(Widget, 'children')
class Container(Widget):
	"""
	A widget that can have children widgets. Abstract base class.
	
	:param children: Dictionary containing child widgets. Keys are `str`
	                 (the names of the widgets) and values are
	                 `Widget` objects (the children).
	:paramtype children: dict[str, Widget]
	"""
	
	def __init__(self, *args, children: dict[str, Widget], **kwargs):
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
	
	def add_child(self, name: str, widget: Widget):
		"""
		Add a child object `widget` named `name`.
		If a widget with that name already exists,
		then the widget corresponding to the name is updated instead.
		
		:param name: The name of the widget to add.
		:paramtype name: str
		
		:param widget: The widget object to add.
		:paramtype widget: Widget
		"""
		self.children[name] = widget
	
	def del_child_by_name(self, name: str):
		"""
		Delete the child widget with name `name`.
		
		:param name: The name of the widget to delete.
		:paramtype name: str
		
		:raises KeyError: if the name does not exist in the children.
		"""
		del self.children[name]
	
	def del_child_by_widget(self, widget: Widget):
		"""
		Delete the child `widget`.
		
		:param widget: The widget object to delete.
		:paramtype widget: Widget
		
		:raises KeyError: if the object `widget` does not exist in the children.
		"""
		for (child_name, child_widget) in self.children.items():
			if child_widget == widget:
				del self.children[child_name]
				return
		raise KeyError(str(widget))
