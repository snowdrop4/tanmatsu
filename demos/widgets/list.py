# Let demo import from root directory
import os
import sys

sys.path.insert(1, os.path.normpath(os.path.join(sys.path[0], '../..')))

from tanmatsu import Tanmatsu
from tanmatsu.widgets import Button, List, TextLog

children = []
text_log = TextLog()

class SuperCoolList(List):
	class Meta:
		children = [
			Button(label="Button 1", callback=lambda: text_log.append_line(f"Button 1 pressed")),
			Button(label="Button 2", callback=lambda: text_log.append_line(f"Button 2 pressed")),
			Button(label="Button 3", callback=lambda: text_log.append_line(f"Button 3 pressed")),
			text_log
		]
		item_height = 5

with Tanmatsu() as t:
	t.set_root_widget(SuperCoolList())
	t.loop()
