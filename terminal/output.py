import sys
import os

import terminal as tt


# ==============================================================================
# Output
# ==============================================================================

def write(s: str):
	os.write(sys.stdout.fileno(), s.encode())


def write_bytes(b: bytes):
	os.write(sys.stdout.fileno(), b)


# ==============================================================================
# Positioning
# ==============================================================================

def set_position(x, y):
	# Legacy nonsense: cursor control is 1-normalised instead of 0-normalised,
	# so adjust for that here rather than ruining the rest of the code.
	# 
	# Even more legacy nonsense: the rows and columns parameters are the
	# wrong way round(!).
	write_bytes(tt.ESCAPE + b'[%d;%dH' % (y + 1, x + 1))


# ==============================================================================
# Resetting
# ==============================================================================

def clear_screen():
	write_bytes(tt.ESCAPE + b'[2J')


# ==============================================================================
# Colours
# ==============================================================================

def set_foreground_colour_8bit(c):
	write_bytes(tt.ESCAPE + b'[38;5;%dm' % c)


def set_background_colour_8bit(c):
	write_bytes(tt.ESCAPE + b'[48;5;%dm' % c)


# Accepts either a tuple containing 3 values, or 3 separate arguments.
def str_foreground_colour_24bit(*args):
	l = len(args)
	
	if l == 1:
		a = args[0]
	elif l == 3:
		a = args
	else:
		raise ValueError("Argument must be either of: three seperate integers,\
			or a single tuple containing three integers.")
	
	return tt.ESCAPE + b'[38;2;%d;%d;%dm' % (a[0], a[1], a[2])


# Accepts either a tuple containing 3 values, or 3 separate arguments.
def set_foreground_colour_24bit(*args):
	write_bytes(str_foreground_colour_24bit(*args))


# Accepts either a tuple containing 3 values, or 3 separate arguments.
def str_background_colour_24bit(*args):
	l = len(args)
	
	if l == 1:
		a = args[0]
	elif l == 3:
		a = args
	else:
		raise ValueError("Argument must be either of: three seperate integers,\
			or a single tuple containing three integers.")
	
	return tt.ESCAPE + b'[48;2;%d;%d;%dm' % (a[0], a[1], a[2])


# Accepts either a tuple containing 3 values, or 3 separate arguments.
def set_background_colour_24bit(*args):
	write_bytes(str_background_colour_24bit(*args))


# ==============================================================================
# Attributes
# ==============================================================================


def set_reset_formatting():
	write_bytes(tt.ESCAPE + b'[0m')


def str_bold(bold):
	if bold:
		return tt.ESCAPE + b'[1m'
	else:
		return tt.ESCAPE + b'[22m'


def set_bold(*args):
	write_bytes(str_bold(*args))


# ==============================================================================
# Modes
# ==============================================================================

# https://terminalguide.namepad.de/mode/p1049/
def set_mode_alternate_screenbuffer(signal):
	write_bytes(tt.ESCAPE + b'[?1049' + signal)


# https://terminalguide.namepad.de/mode/p7/
def set_mode_line_wrap(signal):
	write_bytes(tt.ESCAPE + b'[?7' + signal)


# https://terminalguide.namepad.de/mode/p1000/
def set_mode_mouse_up_down_tracking(signal):
	write_bytes(tt.ESCAPE + b'[?1000' + signal)


# https://terminalguide.namepad.de/mode/p1006/
def set_mode_mouse_report_format_digits(signal):
	write_bytes(tt.ESCAPE + b'[?1006' + signal)
