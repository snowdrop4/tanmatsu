# Let demo import from root directory
import os
import sys

sys.path.insert(1, os.path.normpath(os.path.join(sys.path[0], '../..')))

from datetime import datetime

from tanmatsu import Tanmatsu, size
from tanmatsu.widgets import Button, FlexBox, FlexDirection, TextLog


class TimestampTextLog(TextLog):
	class Meta:
		h = size.Auto()


class TimestampButton(Button):
	class Meta:
		label = "Append Timestamp"
		h = size.FixedInteger(5)


class SuperCoolFlexBox(FlexBox):
	text_log = TimestampTextLog()
	button = TimestampButton(
		callback = lambda tl=text_log: tl.append_line(f"Button pressed on {datetime.now()}")
	)
	
	class Meta:
		flex_direction = FlexDirection.COLUMN


with Tanmatsu() as t:
	t.set_root_widget(SuperCoolFlexBox())
	t.loop()
