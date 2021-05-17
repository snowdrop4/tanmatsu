from style import Style


class Theme:
	"""Abstract base class."""
	
	default = None
	"""The default style to be used, unless overridden."""
	
	focused = None
	"""Currently focused widget."""
	
	active = None
	"""Currently active tab (used by the TabBox widget, for example)."""
	
	inactive = None
	"""Current inactive tab (used by the TabBox widget, for example)."""
	
	cursor = None
	"""Cursor (used by the TextBox widget, for example)."""


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
