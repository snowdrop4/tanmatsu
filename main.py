import tanmatsu
import terminal
import widgets
import size
import test.utils as test
import debug


def okay_c():
	debug.print("okay")


def cancel_c():
	debug.print("cancel")


class ButtonContainer(widgets.FlexBox):
	okay = widgets.Button(label="Okay", callback=okay_c)
	cancel = widgets.Button(label="Cancel", callback=cancel_c)
	
	class Meta:
		flex_direction = widgets.FlexBox.HORIZONTAL
		scroll_direction = widgets.Scrollable.NONE
		border = True
		
		h = size.FixedInteger(7)


class RootWidget(widgets.FlexBox):
	textbox = widgets.TextBox()
	textlog = widgets.TextLog()
	buttonbox = ButtonContainer()
	
	class Meta:
		flex_direction = widgets.FlexBox.HORIZONTAL
		scroll_direction = widgets.Scrollable.NONE
		border = True
		
		w = size.ParentRequested()
		h = size.ParentRequested()


with tanmatsu.Tanmatsu() as t:
	f = RootWidget()
	t.set_root_widget(f)
	
	f.textbox.set_text(test.random_prose())
	debug.set_output_widget(f.textlog)
	
	while True:
		t.draw()
		t.process_input()
