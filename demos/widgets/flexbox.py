# Let demo import from root directory
import sys, os
sys.path.insert(1, os.path.normpath(os.path.join(sys.path[0], '../..')))

from tanmatsu import Tanmatsu, size
from tanmatsu.widgets import FlexBox, TextBox


class Left(FlexBox):
	top = TextBox(text="How much wood would a woodchuck chuck if a woodchuck could chuck wood?")
	bottom = TextBox(text="He would chuck, he would, as much as he could, and chuck as much wood as a woodchuck would if a woodchuck could chuck wood.")
	
	class Meta:
		w = size.Fraction(1, 3)


class VertSplit(FlexBox):
	left  = Left()
	right = TextBox(text="T A N M A T S U")
	
	class Meta:
		flex_direction = FlexBox.HORIZONTAL


with Tanmatsu() as t:
	t.set_root_widget(VertSplit())
	t.loop()
