from style import Style


class DefaultTheme:
	FOREGROUND = (241, 242, 246)
	BACKGROUND = ( 47,  53,  66)
	HIGHLIGHT = (255,  71,  87)
	
	default = Style(foreground=FOREGROUND, background=BACKGROUND, bold=False)
	highlight = Style.inherit(default, foreground=HIGHLIGHT)
	
	tab_active   = Style.inherit(default)
	tab_inactive = Style.inherit(default, foreground=(116, 125, 140))
	
	textbox_cursor = Style.inherit(default, foreground=BACKGROUND, background=FOREGROUND)
