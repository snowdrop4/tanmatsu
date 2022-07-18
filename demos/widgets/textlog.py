# Let demo import from root directory
import sys, os
sys.path.insert(1, os.path.normpath(os.path.join(sys.path[0], '../..')))

from datetime import datetime

from tanmatsu import Tanmatsu, size
from tanmatsu.widgets import TextLog, Button, FlexBox


class TimestampTextLog(TextLog):
	class Meta:
		w = size.ParentPercent(100)
		h = size.ParentRequested()

timestamp_text_log = TimestampTextLog()


class TimestampButton(Button):
	class Meta:
		label = "Append Timestamp"
		callback = lambda: timestamp_text_log.append_line(f"Button pressed on {datetime.now()}")
		
		w = size.ParentPercent(100)
		h = size.FixedInteger(5)

timestamp_button = TimestampButton()


class SuperCoolFlexBox(FlexBox):
	text_log = timestamp_text_log
	button = timestamp_button
	
	class Meta:
		flex_direction = FlexBox.VERTICAL


with Tanmatsu() as t:
	t.set_root_widget(SuperCoolFlexBox())
	t.loop()
