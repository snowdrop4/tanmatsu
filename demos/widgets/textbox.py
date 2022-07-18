# Let demo import from root directory
import sys, os
sys.path.insert(1, os.path.normpath(os.path.join(sys.path[0], '../..')))

from tanmatsu import Tanmatsu
from tanmatsu.widgets import TextBox


class SuperCoolTextBox(TextBox):
	text = "Hello! こんにちは！"

with Tanmatsu() as t:
	t.set_root_widget(SuperCoolTextBox())
	t.loop()
