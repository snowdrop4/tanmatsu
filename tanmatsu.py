import os
import sys
import fcntl
import signal
import selectors

import terminal as tt
import terminal.input as ti
import screenbuffer
from geometry import Rectangle, Dimensions, Point


def exhaust_file_descriptor(fd):
	buff = b''
	
	while True:
		try:
			buff += os.read(fd, 1024)
		except BlockingIOError:
			return buff


class Tanmatsu:
	def __init__(self):
		(w, h) = tt.get_terminal_size()
		self.screenbuffer = screenbuffer.Screenbuffer(w, h)
		
		# Terminal resizes are notified through signals, but if we act on the
		# resize right away (as soon as we receive the signal), we end up with
		# a safety problem not unsimilar to threaded code. As the resize
		# signal can come at any time, we might be executing other code 
		# when does, which means we might end up with crashing or worse.
		# 
		# Thus, we create a pipe and write to it every time we receive a
		# resize signal. We can then select on the pipe and on STDIN, to safely
		# handle input.
		(self.resize_pipe_r, self.resize_pipe_w) = os.pipe()
		signal.signal(signal.SIGWINCH, self.resize_signal_handler)
		
		self.selector = selectors.DefaultSelector()
		self.selector.register(sys.stdin,          selectors.EVENT_READ, self.process_stdin_input)
		self.selector.register(self.resize_pipe_r, selectors.EVENT_READ, self.process_resize_input)
		
		# Turn off blocking on the resize pipe, as we block with our selector
		# instead. At this point, `stdin` has already been set to non-blocking
		# in the `Terminal` class.
		self.resize_pipe_fcntl_original = fcntl.fcntl(self.resize_pipe_r, fcntl.F_GETFL)
		self.resize_pipe_fcntl_nonblock = self.resize_pipe_fcntl_original | os.O_NONBLOCK
		fcntl.fcntl(self.resize_pipe_r, fcntl.F_SETFL, self.resize_pipe_fcntl_nonblock)
	
	def __del__(self):
		self.selector.close()
		
		os.close(self.resize_pipe_r)
		os.close(self.resize_pipe_w)
	
	def set_root_widget(self, widget):
		self.root_widget = widget
	
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
		(button, button_state, position) = data
		
		# Start at the bottom of the focus chain (i.e., the currently focused
		# widget), and go up until we find a widget that consumes the event.
		focus_chain = self.get_current_focus_chain()
		
		for i in reversed(focus_chain):
			if i.mouse_event(button, button_state, position):
				return
	
	def handle_keyboard_event(self, data):
		(key, modifier) = data
		
		if key == ti.Keyboard_key.TAB:
			self.tab(reverse=modifier == ti.MODIFIER_SHIFT)
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
		
		(w, h) = tt.get_terminal_size()
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
