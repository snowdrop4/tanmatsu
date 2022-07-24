import sys
import os


# Otherwise known as:
#     ESC
#     \033
ESCAPE = b"\x1B"

HIGH = b"h"
"""The high signal. Used to turn a mode on."""

LOW  = b"l"
"""The low signal. Used to turn a mode off."""


# ==============================================================================
# General Output
# ==============================================================================

def write(s: str):
	"""Write the given string to stdout."""
	os.write(sys.stdout.fileno(), s.encode())


def write_bytes(b: bytes):
	"""Write the given bytes to stdout."""
	os.write(sys.stdout.fileno(), b)


# ==============================================================================
# Cursor Positioning
# ==============================================================================

def set_position(x: int, y: int):
	"""
	Set the cursor position to (`x`, `y`). Output from :func:`write`/
	:func:`write_bytes` is produced from the cursor position.
	"""
	
	# Legacy nonsense: cursor control is 1-normalised instead of 0-normalised,
	# so adjust for that here rather than ruining the rest of the code.
	# 
	# Even more legacy nonsense: the column and row parameters are the
	# wrong way round(!).
	write_bytes(ESCAPE + b'[%d;%dH' % (y + 1, x + 1))


# ==============================================================================
# Clear Screen
# ==============================================================================

def clear_screen():
	"""Clear the screen."""
	write_bytes(ESCAPE + b'[2J')


# ==============================================================================
# Text Colours
# ==============================================================================

def set_foreground_colour_8bit(c: int):
	"""
	Set the foreground to an 8 bit colour. The new colour applies to all
	output from then on, until overwritten.
	"""
	write_bytes(ESCAPE + b'[38;5;%dm' % c)


def set_background_colour_8bit(c: int):
	"""
	Set the background to an 8 bit colour. The new colour applies to all
	output from then on, until overwritten.
	"""
	write_bytes(ESCAPE + b'[48;5;%dm' % c)


def str_foreground_colour_24bit(c: tuple[int, int, int]) -> bytes:
	"""
	Returns the format code for setting the foreground colour
	to a 24bit colour.
	"""
	return ESCAPE + b'[38;2;%d;%d;%dm' % (c[0], c[1], c[2])


def set_foreground_colour_24bit(c: tuple[int, int, int]):
	"""
	Sets the foreground to a 24 bit colour. The new colour applies to all
	output from then on, until overwritten.
	"""
	write_bytes(str_foreground_colour_24bit(c))


def str_background_colour_24bit(c: tuple[int, int, int]) -> bytes:
	"""
	Returns the format code for setting the background colour
	to a 24bit colour.
	"""
	return ESCAPE + b'[48;2;%d;%d;%dm' % (c[0], c[1], c[2])


def set_background_colour_24bit(c: tuple[int, int, int]):
	"""
	Sets the background to a 24 bit colour. The new colour applies to all
	output from then on, until overwritten.
	"""
	write_bytes(str_background_colour_24bit(c))


# ==============================================================================
# Text Attributes
# ==============================================================================

def str_bold(bold: bool):
	"""Returns the format code for setting the output text weight."""
	if bold:
		return ESCAPE + b'[1m'
	else:
		return ESCAPE + b'[22m'


def set_bold(bold: bool):
	"""
	Sets the text weight. The text weight applies to all output from then on,
	until overwitten.
	"""
	write_bytes(str_bold(bold))


# ==============================================================================
# Terminal Modes
# ==============================================================================

def set_mode_alternate_screenbuffer(signal: bytes):
	"""
	Enter, or exit, an alternate screen buffer. Saves the position of the cursor
	and the state of the screenbuffer before entry. Restores both upon
	exit.
	
	See: https://terminalguide.namepad.de/mode/p1049/
	
	:param signal: Must be either :attr:`HIGH` or :attr:`LOW`.
	"""
	write_bytes(ESCAPE + b'[?1049' + signal)


def set_mode_line_wrap(signal: bytes):
	"""
	Turn automatic line wrap on or off.
	
	See: https://terminalguide.namepad.de/mode/p7/
	
	:param signal: Must be either :attr:`HIGH` or :attr:`LOW`.
	"""
	write_bytes(ESCAPE + b'[?7' + signal)


def set_mode_mouse_up_down_tracking(signal: bytes):
	"""
	Turn mouse input on or off.
	
	See: https://terminalguide.namepad.de/mode/p1000/
	
	:param signal: Must be either :attr:`HIGH` or :attr:`LOW`.
	"""
	write_bytes(ESCAPE + b'[?1000' + signal)


def set_mode_mouse_report_format_digits(signal: bytes):
	"""
	Turn sensible mouse input formatting on or off.
	
	See: https://terminalguide.namepad.de/mode/p1006/
	
	:param signal: Must be either :attr:`HIGH` or :attr:`LOW`.
	"""
	write_bytes(ESCAPE + b'[?1006' + signal)


# ==============================================================================
# Terminal Title
# ==============================================================================

def set_terminal_title(title: str):
	write_bytes(ESCAPE + b']2;' + title.encode() + ESCAPE + b'\\')
