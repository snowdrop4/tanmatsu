import tanmatsu
from tanmatsu import widgets
import tests.utils as test


class ButtonList(widgets.List):
	class Meta:
		border_label = "List"
		children = [
			widgets.Button(label="Button 1", callback=None),
			widgets.Button(label="Button 2", callback=None),
			widgets.Button(label="Button 3", callback=None),
		]
		item_height = 5


class VertSplit(widgets.FlexBox):
	text_box = widgets.TextBox(border_label="Text Box", text=test.random_prose())
	text_log = widgets.TextLog(border_label="Text Log")
	button_list = ButtonList()
	
	class Meta:
		flex_direction = widgets.FlexBox.HORIZONTAL


with tanmatsu.Tanmatsu(title="Tanmatsu!") as t:
	rw = VertSplit()
	t.set_root_widget(rw)
	
	for (i, v) in enumerate(rw.button_list.children):
		v.callback = lambda i=i: rw.text_log.append_line(f"Button {i + 1} pressed")
	
	t.loop()
