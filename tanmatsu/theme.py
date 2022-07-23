from abc import ABC, abstractmethod

from tanmatsu.style import Style


class Theme(ABC):
	"""Abstract base class."""
	
	@property
	@abstractmethod
	def default(self) -> Style:
		"""
		The default style to be used, unless overridden
		by one of the succeeding styles.
		"""
		raise NotImplementedError
	
	@property
	@abstractmethod
	def focused(self) -> Style:
		"""Style used for the currently focused widget."""
		raise NotImplementedError
	
	@property
	@abstractmethod
	def active(self) -> Style:
		"""
		Style used for the currently active tab
		(e.g., in the `TabBox` widget).
		"""
		raise NotImplementedError
	
	@property
	@abstractmethod
	def inactive(self) -> Style:
		"""
		Style used for the currently inactive tab
		(e.g., in the `TabBox` widget).
		"""
		raise NotImplementedError
	
	@property
	@abstractmethod
	def cursor(self) -> Style:
		"""
		Style used for the cursor (e.g., in the `TextBox` widget).
		"""
		raise NotImplementedError


class DefaultTheme(Theme):
	"""Default theme provided by tanmatsu."""
	
	FOREGROUND = (241, 242, 246)
	BACKGROUND = ( 47,  53,  66)
	HIGHLIGHT  = (255,  71,  87)
	
	default = Style(foreground=FOREGROUND, background=BACKGROUND, bold=False)
	focused = Style.inherit(default, foreground=HIGHLIGHT)
	
	active   = Style.inherit(default)
	inactive = Style.inherit(default, foreground=(116, 125, 140))
	
	cursor = Style.inherit(default, foreground=BACKGROUND, background=FOREGROUND)
