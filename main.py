import tanmatsu
from tanmatsu import widgets, size, debug
import tests.utils as test


buttons = [ widgets.Button(label=f"ボタンボタンボタンボタンボタンボタンボタンボタンボタン{i}123", callback=lambda: 0) for i in range(0,10)]


class RootWidget(widgets.TabBox):
	text_box = widgets.TextBox()
	text_log = widgets.TextLog()
	list = widgets.List(buttons, 10)


with tanmatsu.Tanmatsu() as t:
	f = RootWidget()
	t.set_root_widget(f)
	
	f.text_box.text = test.random_prose()
	debug.set_output_widget(f.text_log)
	
	t.loop()
