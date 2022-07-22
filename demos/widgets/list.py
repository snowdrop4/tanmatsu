# Let demo import from root directory
import sys, os
sys.path.insert(1, os.path.normpath(os.path.join(sys.path[0], '../..')))

from tanmatsu import Tanmatsu
from tanmatsu.widgets import List, Button, TextLog


children = []
text_log = TextLog()
children.append(Button(label="Button 1", callback=lambda: text_log.append_line(f"Button 1 pressed")))
children.append(Button(label="Button 2", callback=lambda: text_log.append_line(f"Button 2 pressed")))
children.append(Button(label="Button 3", callback=lambda: text_log.append_line(f"Button 3 pressed")))
children.append(text_log)

class SuperCoolList(List):
	class Meta:
		children = children
		item_height = 5

with Tanmatsu() as t:
	t.set_root_widget(SuperCoolList())
	t.loop()
