# Let demo import from root directory
import os
import sys

sys.path.insert(1, os.path.normpath(os.path.join(sys.path[0], '../..')))

from tanmatsu import Tanmatsu
from tanmatsu.widgets import TabBox, TextBox


class HelloTextBox(TextBox):
	text = "Hello! こんにちは！"

class GoodbyeTextBox(TextBox):
	text = "Goodbye! さよなら！"

class SuperCoolTabBox(TabBox):
	hello = HelloTextBox()
	goodbye = GoodbyeTextBox()

with Tanmatsu() as t:
	t.set_root_widget(SuperCoolTabBox())
	t.loop()
