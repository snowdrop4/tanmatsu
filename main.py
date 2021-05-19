import tanmatsu
from tanmatsu import widgets, size, debug
import tests.utils as test


class RootWidget(widgets.TabBox):
	いろはいろはいろはいろは1 = widgets.TextLog()
	いろはいろはいろはいろは2 = widgets.TextBox()
	いろはいろはいろはいろは3 = widgets.TextBox()
	the_quick_brown_fox = widgets.TextBox()
	textlog = widgets.TextLog()


with tanmatsu.Tanmatsu() as t:
	f = RootWidget()
	t.set_root_widget(f)
	
	f.いろはいろはいろはいろは2.text = test.random_prose()
	f.いろはいろはいろはいろは1.set_lines(test.random_prose().split("\n"))
	for i in range(0, 1):
		f.いろはいろはいろはいろは1.append_line("たたたたたたたたたたたたたたたたたたたたたたたたたたたたたたたたたたたたたたたたたたたたたたたたたたたたたたたたたたた")
	
	# f.buttonlist.cursor = 1
	# f.buttonlist.items[0].callback = lambda: f.textbox.set_text(test.random_prose())
	debug.set_output_widget(f.textlog)
	
	t.loop()
