import sys
import shutil
import termios
import os

from . import output as to
import debug


# ==============================================================================
# Escape codes/prefixes
# ==============================================================================

ESCAPE = b"\x1B"
HIGH = b"h"
LOW  = b"l"


class Terminal:
	def __init__(self):
		# Normally stdin and stdout are set to the same file descriptor.
		# This is no good, as we need stdin to be nonblocking and stdout to be
		# blocking.
		# 
		# Manually open two separate file descriptors for stdin and stdout:
		sys.stdin  = open("/dev/stdin",  "r")
		sys.stdout = open("/dev/stdout", "w")
		
		os.set_blocking(sys.stdin.fileno(),  False)
		os.set_blocking(sys.stdout.fileno(), True)
		
		
		# Fiddle with the control modes for stdin:
		STDIN_TERMIOS = termios.tcgetattr(sys.stdin.fileno())
		
		# Configure the `c_cflag` bitmask inside the `termios` struct that
		# contains the control modes.
		# 
		# Turn off the following control modes:
		# 
		# termios.ICANON = False: do not buffer input until the enter button is pressed
		# termios.ECHO   = False: do not echo keys pressed to the screen
		STDIN_TERMIOS[3] = STDIN_TERMIOS[3] & ~termios.ICANON & ~termios.ECHO
		
		termios.tcsetattr(sys.stdin.fileno(), termios.TCSADRAIN, STDIN_TERMIOS)
		
		
		# Fiddle with the terminal emulator options:
		self.terminal_modes = []
		
		# Drop the terminal into an alternative screenbuffer just for us,
		# so that we can draw to it at will without overwriting the terminal
		# history.
		# 
		# This way, when the user quits our program, no trace of it will be
		# left in their terminal.
		self.terminal_modes += [to.set_mode_alternate_screenbuffer]
		
		# Stop the terminal from reflowing text when it is resized.
		# It causes flickering as it fights with the redrawing we do on
		# terminal resize.
		self.terminal_modes += [to.set_mode_line_wrap]
		
		# Turn on mouse events.
		self.terminal_modes += [to.set_mode_mouse_up_down_tracking]
		
		# Use variable length ASCII digits to report mouse location in order
		# to support terminals of any size.
		self.terminal_modes += [to.set_mode_mouse_report_format_digits]
		
		for f in self.terminal_modes:
			f(HIGH)
	
	def __enter__(self):
		return self
	
	def __exit__(self, exception_type, exception_value, traceback):
		for f in self.terminal_modes:
			f(LOW)
		
		debug.flush_print_buffer()
		
		sys.stdin.close()
		sys.stdout.close()
		
		return False


def get_terminal_size():
	return shutil.get_terminal_size()
