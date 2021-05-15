import os
import sys
import termios

import terminal.output as to
import terminal as tt


stdin = sys.stdin.fileno()

old_termios = termios.tcgetattr(stdin)
new_termios = termios.tcgetattr(stdin)

new_termios[3] = new_termios[3] & ~termios.ICANON & ~termios.ECHO

termios.tcsetattr(stdin, termios.TCSADRAIN, new_termios)

to.set_mode_alternate_screenbuffer(to.HIGH)
to.set_mode_mouse_up_down_tracking(to.HIGH)
to.set_mode_mouse_report_format_digits(to.HIGH)

while True:
	k = os.read(stdin, 1024)
	
	h = k.hex()
	h = " ".join([ h[i:i + 2] for i in range(0, len(h), 2) ])
	print(f"{k}\t\t\t{h}")

termios.tcsetattr(stdin, termios.TCSADRAIN, old_termios)

to.set_mode_alternate_screenbuffer(to.LOW)
to.set_mode_mouse_up_down_tracking(to.LOW)
to.set_mode_mouse_report_format_digits(to.LOW)
