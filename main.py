import tanmatsu
from tanmatsu import widgets, size, debug
import tests.utils as test


class ButtonList(widgets.List):
	class Meta:
		children = [ widgets.Button(label="Delete tab", callback=None) ]
		item_height = 10


class Split(widgets.FlexBox):
	text_box = widgets.TextBox()
	text_log = widgets.TextLog()
	
	class Meta:
		flex_direction = widgets.FlexBox.HORIZONTAL
		border_label = "hello! really really looooooooooooooooooooong label xd たたふたた asdasd"


class RootWidget(widgets.TabBox):
	split = Split()
	list = ButtonList()


with tanmatsu.Tanmatsu() as t:
	f = RootWidget()
	t.set_root_widget(f)
	
	f.list.children[0].callback = lambda: f.del_tab_by_label("list")
	
	f.split.text_box.text = test.random_prose()
	debug.set_output_widget(f.split.text_log)
	
	t.loop()
