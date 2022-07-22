import re
from enum import (Enum, auto)

from parsy import (generate, string, regex, test_char, char_from, any_char, fail, index)

import terminal as tt
from geometry import Point


# ==============================================================================
# Event types
# ==============================================================================
class Event_type(Enum):
	MOUSE    = auto()
	KEYBOARD = auto()


# ==============================================================================
# Mouse
# ==============================================================================
class Mouse_state(Enum):
	PRESSED  = auto()
	RELEASED = auto()


class Mouse_button(Enum):
	LMB = auto()
	MMB = auto()
	RMB = auto()
	
	SCROLL_UP    = auto()
	SCROLL_DOWN  = auto()
	SCROLL_LEFT  = auto()
	SCROLL_RIGHT = auto()


mouse_button_lookup = {
	0: Mouse_button.LMB,
	1: Mouse_button.MMB,
	2: Mouse_button.RMB,
	
	64: Mouse_button.SCROLL_UP,
	65: Mouse_button.SCROLL_DOWN,
	66: Mouse_button.SCROLL_LEFT,
	67: Mouse_button.SCROLL_RIGHT,
}


@generate
def mouse_sequence():
	yield string(b"\x1B[<")
	
	button = yield regex(re.compile(rb"[0-9]+")).map(int)
	yield string(b";")
	x = yield regex(re.compile(rb"[0-9]+")).map(int)
	yield string(b";")
	y = yield regex(re.compile(rb"[0-9]+")).map(int)
	
	pressed  = string(b"M").result(Mouse_state.PRESSED)
	released = string(b"m").result(Mouse_state.RELEASED)
	
	button = mouse_button_lookup[button]
	button_state = yield pressed | released
	position = Point(x, y)
	return (Event_type.MOUSE, (button, button_state, position))


# ==============================================================================
# Keyboard
# ==============================================================================
MODIFIER_NONE  = 0b0000
MODIFIER_SHIFT = 0b0001
MODIFIER_ALT   = 0b0010
MODIFIER_CTRL  = 0b0100


class Keyboard_key(Enum):
	TAB = auto()
	ENTER = auto()
	BACKSPACE = auto()
	ESCAPE = auto()
	
	F1  = auto()
	F2  = auto()
	F3  = auto()
	F4  = auto()
	F5  = auto()
	F6  = auto()
	F7  = auto()
	F8  = auto()
	F9  = auto()
	F10 = auto()
	F11 = auto()
	F12 = auto()
	
	INSERT = auto()
	DELETE = auto()
	HOME = auto()
	END  = auto()
	PAGE_UP   = auto()
	PAGE_DOWN = auto()
	
	UP_ARROW    = auto()
	DOWN_ARROW  = auto()
	LEFT_ARROW  = auto()
	RIGHT_ARROW = auto()


# Keycodes encountered after \x1B[
keyboard_keycode_lookup = {
	b"2": Keyboard_key.INSERT,
	b"3": Keyboard_key.DELETE,
	b"5": Keyboard_key.PAGE_UP,
	b"6": Keyboard_key.PAGE_DOWN,
	
	b"15": Keyboard_key.F5,
	b"17": Keyboard_key.F6,  # yes, it skips 16. 💩
	b"18": Keyboard_key.F7,
	b"19": Keyboard_key.F8,
	b"20": Keyboard_key.F9,
	b"21": Keyboard_key.F10,
	b"23": Keyboard_key.F11,  # skips 22, too.
	b"24": Keyboard_key.F12,
}

# Special keycodes encountered all on their own.
special_keyboard_keycode_lookup = {
	b"\x09": Keyboard_key.TAB,
	b"\x0a": Keyboard_key.ENTER,
	b"\x7f": Keyboard_key.BACKSPACE,
}


# Keycodes encountered after \x1BO or \x1B[
legacy_keyboard_keycode_lookup = {
	b"P": Keyboard_key.F1,
	b"Q": Keyboard_key.F2,
	b"R": Keyboard_key.F3,
	b"S": Keyboard_key.F4,
	
	b"H": Keyboard_key.HOME,
	b"F": Keyboard_key.END,
	
	b"A": Keyboard_key.UP_ARROW,
	b"B": Keyboard_key.DOWN_ARROW,
	b"C": Keyboard_key.RIGHT_ARROW,
	b"D": Keyboard_key.LEFT_ARROW,
	
	# Special case. Produced when SHIFT+TAB is pressed. We must make sure we
	# set the modifier bitmask to `MODIFIER_SHIFT` when encountering this.
	b"Z": Keyboard_key.TAB,
}


@generate
def key_sequence():
	yield string(b"\x1B[")
	
	code = yield regex(re.compile(rb"[0-9]{1,2}"))
	
	tilde = yield string(b"~").optional()
	
	if tilde is None:  # Sequence has a bitmask.
		yield string(b";")
		modifier_bitmask = yield regex(re.compile(rb"[0-9]")).map(int)
		yield string(b"~")
		
		# The modifier bitmask, for whatever depraved reason, is incremented
		# by one after the bits have been masked. Thus we need to
		# deincrement it before it's usable.
		# 
		# I.e., the bitmask for the shift key is 0b0001, and the bitmask
		# for the alt key is 0b0010, but the value we're given when 
		# the shift and alt key is pressed is `(0b0001 & 0b0010) + 1`,
		# giving 0b0100 instead of 0b0011.
		modifier_bitmask = modifier_bitmask -1
	else:
		modifier_bitmask = MODIFIER_NONE
	
	key = keyboard_keycode_lookup[code]
	
	return (Event_type.KEYBOARD, (key, modifier_bitmask))


# Legacy special case for F1-F4.
@generate
def legacy_f1_to_f4():
	yield string(b"\x1BO")
	code = yield regex(re.compile(rb"[PQRS]"))
	
	key = legacy_keyboard_keycode_lookup[code]
	return (Event_type.KEYBOARD, (key, MODIFIER_NONE))


# Arrow, home, and end keys.
@generate
def legacy_key_sequence():
	yield string(b"\x1B[")
	code = yield regex(re.compile(rb"[A-Z]"))
	
	key = legacy_keyboard_keycode_lookup[code]
	
	# Special case. \x1B[Z is produced when pressing SHIFT+TAB. No other
	# keycodes parsed by this function have any modifier keys associated
	# with them.
	if key == Keyboard_key.TAB:
		modifier_bitmask = MODIFIER_SHIFT
	else:
		modifier_bitmask = MODIFIER_NONE
	
	return (Event_type.KEYBOARD, (key, modifier_bitmask))


# F1-F1, arrow, home, and end keys with a modifier key pressed.
@generate
def legacy_key_sequence_with_modifier():
	yield string(b"\x1B[1;")
	modifier_bitmask = yield regex(re.compile(rb"[0-9]")).map(int)
	code = yield regex(re.compile(rb"[A-Z]"))
	
	modifier_bitmask = modifier_bitmask -1  # see comment in function `key_sequence()` for explanation
	key = legacy_keyboard_keycode_lookup[code]
	return (Event_type.KEYBOARD, (key, modifier_bitmask))


@generate
def special_key():
	code = yield any_char
	code = code.to_bytes(1, "big")
	
	if code in special_keyboard_keycode_lookup:
		key = special_keyboard_keycode_lookup[code]
		return (Event_type.KEYBOARD, (key, MODIFIER_NONE))
	else:
		return fail("expecting special key codepoint")


# CTRL key, combined with one of the following keys:
# 
# ASCII letter
# [
# \
# ]
# ~
# ?
@generate
def select_keys_with_ctrl():
	code = yield test_char(lambda c: c <= 0x1F and c != 0x1B, "expecting byte between 0x00 and 0x1F")
	
	match code:
		case 0x00:
			key = ' '
		# A special case on top of a special case. Pressing CTRL+TAB or
		# CTRL+ENTER does not produce a special keycode, but pressing
		# CTRL+BACKSPACE *does*. CTRL+BACKSPACE and CTRL+h produce the same
		# keycode, which is why we're dealing with this here.
		# 
		# I'm choosing to prioritise a signal indicating the BACKSPACE key was
		# pressed, over a signal showing the h key was pressed, in accordance
		# with the decision made above to treat CTRL+j and other combinations
		# that produce the same keycodes as the TAB/ENTER/BACKSPACE keys
		# as if the TAB/ENTER/BACKSPACE keys themselves were pressed.
		case 0x08:
			key = Keyboard_key.BACKSPACE
		case 0x1E:
			key = '~'
		case 0x1F:
			key = '?'
		# Fallback case. This covers the remaining ASCII letters, the left
		# square bracket, backslash, and right square bracket
		case _:
			key = chr(0x60 ^ code)
	
	return (Event_type.KEYBOARD, (key, MODIFIER_CTRL))


@generate
def select_keys_with_alt():
	yield string(b"\x1B")
	
	# Special case: If the user is holding down CTRL as well as SHIFT,
	# it will produce \x1B and then a keycode matched by
	# `select_keys_with_ctrl`.
	with_ctrl = yield select_keys_with_ctrl.optional()
	if with_ctrl is not None:
		(_, (key, _)) = with_ctrl
		return (Event_type.KEYBOARD, (key, MODIFIER_CTRL ^ MODIFIER_ALT))
	
	code = yield any_char
	code = code.to_bytes(1, "big")
	
	if code in special_keyboard_keycode_lookup:
		key = special_keyboard_keycode_lookup[code]
	else:
		key = code.decode("utf-8")
	
	return (Event_type.KEYBOARD, (key, MODIFIER_ALT))


# Make sure this parser is attempted last!
# It's a fallback that will accept *any* character.
@generate
def unicode_codepoint():
	codepoint = yield any_char
	
	# Special case: If we find the escape keycode all the way down here,
	# it probably means the user just pressed the escape key.
	# 
	# There is ambiguity with the ESCAPE key as is not escaped itself, so when
	# presented with input like `\x1Bq`, there is no way of knowing whether
	# the user pressed the ESCAPE button and the `q` button such that both
	# keycodes appeared in the input buffer inbetween calls to clear and
	# process it, or whether they pressed ALT and `q` at the same time.
	# Both actions would produce the same sequence -- `\x1Bq`.
	# 
	# Thus, in the above case, we just have to assume that they pressed
	# ALT and `q`, as correctly recognising the ALT key in all cases is
	# decidedly more important than *sometimes* mistaking the ESCAPE key
	# for the ALT key (it's a timing problem and \x1B isn't guaranteed to end
	# up in the input buffer alongside `q` even if both keys are pressed
	# simultaneously.
	if codepoint == 0x1B:
		return (Event_type.KEYBOARD, (Keyboard_key.ESCAPE, MODIFIER_NONE))
	
	match codepoint & 0b11110000:
		case 0b11000000:
			bytes_left = 1
		case 0b11100000:
			bytes_left = 2
		case 0b11110000:
			bytes_left = 3
		case _:
			bytes_left = 0
	
	for i in range(0, bytes_left):
		byte = yield any_char
		codepoint = codepoint | byte << (i + 1) * 8  # concat the bytes together
	
	return (Event_type.KEYBOARD, (chr(codepoint), MODIFIER_NONE))


# ==============================================================================
# Keyboard + mouse
# ==============================================================================
def parse_input(input):
	parser = mouse_sequence \
		| key_sequence \
		| legacy_f1_to_f4 \
		| legacy_key_sequence \
		| legacy_key_sequence_with_modifier \
		| special_key \
		| select_keys_with_ctrl \
		| select_keys_with_alt \
		| unicode_codepoint \
	
	return parser.at_least(1).parse(input)
