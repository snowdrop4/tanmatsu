import tanmatsu
from tanmatsu import widgets, size, debug
import tests.utils as test


def okay_c():
	debug.print("okay")


def cancel_c():
	debug.print("cancel")


class ButtonBox(widgets.FlexBox):
	okay = widgets.Button(label="Okay", callback=okay_c)
	cancel = widgets.Button(label="Cancel", callback=cancel_c)
	
	class Meta:
		flex_direction = widgets.FlexBox.HORIZONTAL
		scroll_direction = widgets.Scrollable.NONE
		border = True
		
		h = size.FixedInteger(50)
		w = size.FixedInteger(50)


# class ButtonList(widgets.List):
# 	test = 6
# 	
# 	class Meta:
# 		items = [
# 			widgets.Button(label="Okay", callback=okay_c),
# 			widgets.Button(label="Cancel", callback=cancel_c)
# 		]
# 		item_height = 7


buttons = [
	widgets.Button(label="Okay", callback=okay_c),
	widgets.Button(label="Cancel", callback=cancel_c)
]


class RootWidget(widgets.FlexBox):
	textbox = widgets.TextBox()
	textlog = widgets.TextLog()
	bb = ButtonBox()
	# buttonlist = widgets.List(buttons, 7)
	
	class Meta:
		flex_direction = widgets.FlexBox.HORIZONTAL
		scroll_direction = widgets.Scrollable.HORIZONTAL | widgets.Scrollable.VERTICAL
		border = True
		
		w = size.ParentRequested()
		h = size.ParentRequested()


with tanmatsu.Tanmatsu() as t:
	f = RootWidget()
	t.set_root_widget(f)
	
	f.textbox.text = test.random_prose()
	# f.buttonlist.cursor = 1
	# f.buttonlist.items[0].callback = lambda: f.textbox.set_text(test.random_prose())
	debug.set_output_widget(f.textlog)
	
	t.loop()
