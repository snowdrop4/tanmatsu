# Let demo import from root directory
import os
import sys

from tanmatsu.widgets.flexbox import JustifyContent

sys.path.insert(1, os.path.normpath(os.path.join(sys.path[0], '../..')))

from tanmatsu import Tanmatsu, size
from tanmatsu.widgets import (Button, FlexBox, FlexDirection, JustifyContent,
                              TextBox)


class Button1(Button):
	class Meta:
		label = "Button 1"
		callback = None
		w = size.Fraction(1, 4)
		h = size.FixedInteger(5)


class Button2(Button):
	class Meta:
		label = "Button 2"
		callback = None
		w = size.Fraction(1, 4)
		h = size.FixedInteger(5)


class Button3(Button):
	class Meta:
		label = "Button 3"
		callback = None
		w = size.FixedInteger(50)
		h = size.FixedInteger(5)


class Buttons(FlexBox):
	b1 = Button1()
	b2 = Button2()
	b3 = Button3()
	
	class Meta:
		flex_direction = FlexDirection.ROW
		justify_content = JustifyContent.SPACE_BETWEEN


class TextBoxes(FlexBox):
	top = TextBox(text="How much wood would a woodchuck chuck if a woodchuck could chuck wood?")
	bottom = TextBox(text="He would chuck, he would, as much as he could, and chuck as much wood as a woodchuck would if a woodchuck could chuck wood.")
	
	class Meta:
		flex_direction = FlexDirection.ROW


class Main(FlexBox):
	top    = TextBoxes()
	bottom = Buttons()
	
	class Meta:
		flex_direction = FlexDirection.COLUMN


with Tanmatsu() as t:
	t.set_root_widget(Main())
	t.loop()
