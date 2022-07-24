import os
import sys
import fcntl
import signal
import shutil
import termios
import selectors

import tanmatsu.input as ti
import tanmatsu.output as to
from tanmatsu import screenbuffer, debug
from tanmatsu.widgets.base import Widget
from tanmatsu.geometry import Rectangle, Dimensions, Point


def exhaust_file_descriptor(fd):
	buff = b''
	
	while True:
		try:
			buff += os.read(fd, 1024)
		except BlockingIOError:
			return buff


class Tanmatsu:
	"""
	:param title: The title the terminal window should be set to.
	:paramtype title: str
	
	This class fulfils two functions:
	
	- Configures the terminal emulator (setting proper modes and so on).
	- Handles the main TUI loop (draw, take input, process input).
	
	As a bare minimum, a program written with tanmatsu must perform the
	following three steps:
	
	1. Instantiate `Tanmatsu()` as a context manager.
	2. Set the root widget with :meth:`set_root_widget`.
	3. Start the main TUI loop with :meth:`loop`.
	
	For example:
	
	.. code-block:: python
	   
	   from tanmatsu import Tanmatsu
	   from tanmatsu.widgets import TextBox
	   
	   with Tanmatsu() as t:
	       t.set_root_widget(TextBox(text="Hello! こんにちは！"))
	       t.loop()
	"""
	
	def __init__(self, title: str | None = None):
		# Get the terminal's w/h and set up a screenbuffer object
		(w, h) = shutil.get_terminal_size()
		self.screenbuffer = screenbuffer.Screenbuffer(w, h)
		
		self.__setup_stdinout()  # Set the proper stdin/stdout modes
		self.__setup_terminal()  # Set the proper terminal emulator modes
		self.__setup_selector()  # Set up input handling
		
		if title is not None:
			to.set_terminal_title(title)
	
	def __setup_stdinout(self):
		# Normally stdin and stdout are set to the same file descriptor.
		# This doesn't work, as we need to set stdin and stdout to different modes.
		# 
		# Manually open two separate file descriptors for stdin and stdout:
		sys.stdin  = open("/dev/stdin",  "r")
		sys.stdout = open("/dev/stdout", "w")
		
		# Set up blocking and non-blocking bitmasks for stdin:
		self.stdin_fcntl_initial     = fcntl.fcntl(sys.stdin.fileno(), fcntl.F_GETFL)
		self.stdin_fcntl_nonblocking = self.stdin_fcntl_initial |  os.O_NONBLOCK
		self.stdin_fcntl_blocking    = self.stdin_fcntl_initial & ~os.O_NONBLOCK
		# ... and do the same for stdout:
		self.stdout_fcntl_initial     = fcntl.fcntl(sys.stdout.fileno(), fcntl.F_GETFL)
		self.stdout_fcntl_nonblocking = self.stdout_fcntl_initial |  os.O_NONBLOCK
		self.stdout_fcntl_blocking    = self.stdout_fcntl_initial & ~os.O_NONBLOCK
		
		# And then set stdin to be non-blocking and stdout to be blocking:
		fcntl.fcntl(sys.stdin.fileno(),  fcntl.F_SETFL, self.stdin_fcntl_nonblocking)
		fcntl.fcntl(sys.stdout.fileno(), fcntl.F_SETFL, self.stdout_fcntl_blocking)
		
		# Fiddle with the control modes for stdin:
		self.stdin_termios_initial        = termios.tcgetattr(sys.stdin.fileno())
		self.stdin_termios_no_buffer_echo = termios.tcgetattr(sys.stdin.fileno())
		
		# Configure the `c_cflag` bitmask inside the `termios` struct that
		# contains the control modes.
		# 
		# Turn off the following control modes:
		# 
		# termios.ICANON = False: do not buffer input until the enter button is pressed
		# termios.ECHO   = False: do not echo keys pressed to the screen
		self.stdin_termios_no_buffer_echo[3] &= ~termios.ICANON
		self.stdin_termios_no_buffer_echo[3] &= ~termios.ECHO
		
		termios.tcsetattr(sys.stdin.fileno(), termios.TCSADRAIN, self.stdin_termios_no_buffer_echo)
	
	def __teardown_stdinout(self):
		fcntl.fcntl(sys.stdin.fileno(),  fcntl.F_SETFL, self.stdin_fcntl_initial)
		fcntl.fcntl(sys.stdout.fileno(), fcntl.F_SETFL, self.stdout_fcntl_initial)
		
		termios.tcsetattr(sys.stdin.fileno(), termios.TCSADRAIN, self.stdin_termios_initial)
	
	def __setup_terminal(self):
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
			f(to.HIGH)
	
	def __teardown_terminal(self):
		for f in self.terminal_modes:
			f(to.LOW)
	
	def __setup_selector(self):
		# Terminal resizes are notified through signals, but if we act on the
		# resize right away (as soon as we receive the signal), we end up with
		# a safety problem. Given that the resize signal can come at any time,
		# we might be executing other code when it does, which means we might
		# end up with crashing or worse.
		# 
		# Thus, we create a pipe and write to it every time we receive a
		# resize signal. We can then select on the pipe and on STDIN, to safely
		# handle input.
		
		# Create the pipe
		(self.resize_pipe_r, self.resize_pipe_w) = os.pipe()
		
		# Turn off blocking on the read end of the resize pipe,
		# as we block with our selector instead.
		resize_pipe_r_fcntl = fcntl.fcntl(self.resize_pipe_r, fcntl.F_GETFL)
		resize_pipe_r_fcntl = resize_pipe_r_fcntl | os.O_NONBLOCK
		fcntl.fcntl(self.resize_pipe_r, fcntl.F_SETFL, resize_pipe_r_fcntl)
		
		# Connect SIGWINCH (terminal resize signal) to our handler function
		# that will populate the resize pipe.
		signal.signal(signal.SIGWINCH, self.resize_signal_handler)
		
		# Create our selector and connect our handler functions for STDIN input
		# and terminal resizes.
		self.selector = selectors.DefaultSelector()
		self.selector.register(sys.stdin,          selectors.EVENT_READ, self.process_stdin_input)
		self.selector.register(self.resize_pipe_r, selectors.EVENT_READ, self.process_resize_input)
	
	def __teardown_selector(self):
		os.close(self.resize_pipe_r)
		os.close(self.resize_pipe_w)
		
		self.selector.close()
	
	def __enter__(self):
		return self
	
	def __exit__(self, exception_type, exception_value, traceback):
		self.__teardown_stdinout()
		self.__teardown_terminal()
		self.__teardown_selector()
		
		debug.flush_print_buffer()
		
		return False
	
	# Build a list, starting out from the root widget, and descending
	# until we find the focused widget (i.e., the end of the focus chain).
	def get_current_focus_chain(self):
		focus_chain = [self.root_widget]
		while focus_chain[-1].focused_child is not None:
			focus_chain.append(focus_chain[-1].focused_child)
		return focus_chain
	
	def get_current_focused_widget(self):
		widget = self.root_widget
		while widget.focused_child is not None:
			widget = widget.focused_child
		return widget
	
	# Blocks. Waits for input on STDIN, or for a terminal resize, and then
	# calls the appropriate function.
	def process_input(self):
		for (key, _) in self.selector.select():
			key.data()  # call the handler function we stored in the data field
	
	def handle_mouse_event(self, data):
		(button, modifier, state, position) = data
		
		# Start at the bottom of the focus chain (i.e., the currently focused
		# widget), and go up until we find a widget that consumes the event.
		focus_chain = self.get_current_focus_chain()
		
		for i in reversed(focus_chain):
			if i.mouse_event(button, modifier, state, position):
				return
	
	def handle_keyboard_event(self, data):
		(key, modifier) = data
		
		if key == ti.Keyboard_key.TAB:
			self.tab(reverse=modifier == ti.Keyboard_modifier.SHIFT)
			return
		
		# Start at the bottom of the focus chain (i.e., the currently focused
		# widget), and go up until we find a widget that consumes the event.
		focus_chain = self.get_current_focus_chain()
		
		for i in reversed(focus_chain):
			if i.keyboard_event(key, modifier):
				return
	
	def process_stdin_input(self):
		raw_input = exhaust_file_descriptor(sys.stdin.fileno())
		
		for (event_type, event_data) in ti.parse_input(raw_input):
			match event_type:
				case ti.Event_type.MOUSE:
					self.handle_mouse_event(event_data)
				case ti.Event_type.KEYBOARD:
					self.handle_keyboard_event(event_data)
	
	def process_resize_input(self):
		# Just clear everything from the pipe; the contents don't matter
		# (nothing is writing to the pipe except `resize_signal_handler()`).
		_ = exhaust_file_descriptor(self.resize_pipe_r)
		
		(w, h) = shutil.get_terminal_size()
		self.screenbuffer.resize(w, h)
	
	def resize_signal_handler(self, signum, frame):
		# Write something random to the pipe. The presence of something in
		# the pipe will be taken as a sign that a resize event happened.
		os.write(self.resize_pipe_w, b"_")
	
	def tab(self, reverse=False):
		# It's easier to operate on a list like this, rather than
		# operate directly on the widgets themselves, as list indexing syntax
		# greatly simplifies things. At the end of this function, we'll update
		# the real focus chain in the widgets themselves based on this list.
		focus_chain = self.get_current_focus_chain()
		
		# We need to define a bunch of helper functions to help navigate
		# the focus chain:
		
		# Goes down and returns the leftmost child widget, if possible.
		# 
		# The parameter `f` must be assigned to a function with one parameter,
		# that converts said parameter to a list.
		# 
		# `f` can optionally produce a reversed list, in which case this
		# function will return the rightmost child widget instead.
		def get_down_and_left_or_none(f, widget):
			try:
				return f(widget.focusable_children.values())[0]
			except (AttributeError, IndexError):
				return None
		
		# Takes the widget to the right of `current_child` from among the
		# children of `parent`. `current_child` must be a child of `parent`.
		# 
		# The parameter `f` must be assigned to a function with one parameter,
		# that converts said parameter to a list.
		# 
		# `f` can optionally produce a reversed list, in which case this
		# function will return the widget to the left instead.
		def get_right_or_none(f, parent, current_child):
			try:
				for (i, v) in enumerate(f(parent.focusable_children.values())):
					if v is current_child:
						return f(parent.focusable_children.values())[i + 1]
				
				raise ValueError("`current_child` must be a child of `parent`.")
			except IndexError:
				return None
		
		def backward(focus_chain):
			f = lambda x: list(reversed(x))
			
			# Is there a widget to the left?
			try:
				left = get_right_or_none(f, focus_chain[-2], focus_chain[-1])
				
				# If the previous line didn't throw an exception, go left!
				focus_chain[-1] = left
			except IndexError:
				left = None
			
			# If we successfully went left, or we're at the root widget,
			# go one level down and to the rightmost widget.
			# Repeat until we are at the deepest, rightmost widget.
			# 
			# This leaves us at the deepest and rightmost widget,
			# that is one widget to the left of the previously focused widget.
			if left or len(focus_chain) == 1:
				while down := get_down_and_left_or_none(f, focus_chain[-1]):
					focus_chain.append(down)
			else:
				# There's nowhere left to go but up.
				focus_chain.pop()
			
			return focus_chain
		
		def forward(focus_chain):
			f = lambda x: list(x)
			
			# Is there a widget below?
			down = get_down_and_left_or_none(f, focus_chain[-1])
			
			# Go down, if a widget did exist below.
			if down:
				focus_chain.append(down)
				return focus_chain  # We're done, that's all we needed to do!
			
			# Failing that...
			
			# Try to go right. If that fails, go up. Repeat until we either
			# successfully go right, or go up so far we hit the root widget.
			while focus_chain[-1] is not self.root_widget:
				right = get_right_or_none(f, focus_chain[-2], focus_chain[-1])
				
				if right:
					focus_chain[-1] = right
					break
				
				focus_chain = focus_chain[:-1]
			
			return focus_chain
		
		if reverse:
			focus_chain = backward(focus_chain)
		else:
			focus_chain = forward(focus_chain)
		
		# Now we have the updated `focus_chain` list, traverse it and
		# update the `focused_child` for each widget.
		for (parent, focused_child) in zip(focus_chain, focus_chain[1:] + [None]):
			parent.focused_child = focused_child
	
	def draw(self):
		# Find the end of the focus chain, and mark that widget as focused
		# for drawing purposes.
		# 
		# Marking the focused widget *now*, in the drawing function, isn't
		# necessarily "pretty", but it vastly simplifies things compared to
		# doing it "properly". There are a lot less bugs that can happen,
		# a lot less lines of code to worry about, less state to keep track of,
		# and widgets don't need to worry about keeping the `focused` property
		# of their child widget(s) valid when widgets are made active/inactive
		# (e.g., a TabBox switching tabs), or widgets are added/deleted/moved.
		current_focused_widget = self.get_current_focused_widget()
		current_focused_widget.focused = True
		
		# Clear the screenbuffer
		self.screenbuffer.clear()
		
		# Layout root widget
		position = Point(0, 0)
		size = Dimensions(self.screenbuffer.w, self.screenbuffer.h)
		self.root_widget.layout(position, size, size)
		
		# Draw root widget to the screenbuffer
		clip = Rectangle(0, 0, self.screenbuffer.w, self.screenbuffer.h)
		self.root_widget.draw(self.screenbuffer, clip=clip)
		
		# Output the screenbuffer to the screen (stdout)
		self.screenbuffer.write()
		
		# Defocus the widget we just focused, so that there aren't multiple
		# focused widgets next time we draw.
		current_focused_widget.focused = False
	
	def set_root_widget(self, widget: Widget):
		"""
		Set the root widget. A root widget must be set before
		:meth:`loop` is called.
		
		:param widget: The widget to set as the root widget.
		:paramtype widget: Widget
		"""
		self.root_widget = widget
	
	def loop(self):
		"""
		Enter the main TUI loop—drawing to the screen,
		processing input, and redrawing.
		"""
		while True:
			self.draw()
			self.process_input()
