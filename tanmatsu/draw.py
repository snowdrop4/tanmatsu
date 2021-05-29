from tanmatsu import geometry, screenbuffer, widgets


def rectangle(
	s: screenbuffer.Screenbuffer, r: geometry.Rectangle, clip=None, style=None
):
	if clip and not r.intersects(clip):
		return
	
	s.set(r.x1, r.y1, "╔", clip, style)
	s.set(r.x2, r.y1, "╗", clip, style)
	
	s.set(r.x1, r.y2, "╚", clip, style)
	s.set(r.x2, r.y2, "╝", clip, style)
	
	for i in range(1, (r.w - 1)):
		s.set(r.x1 + i, r.y1, "═", clip, style)
		s.set(r.x1 + i, r.y2, "═", clip, style)
	
	for i in range(1, (r.h - 1)):
		s.set(r.x1, r.y1 + i, "║", clip, style)
		s.set(r.x2, r.y1 + i, "║", clip, style)


def scrollbar(
	s: screenbuffer.Screenbuffer,
	r: geometry.Rectangle,
	handle_length,
	scroll_percent,
	direction,
	clip=None,
	style=None,
):
	# Derive the size of the scrollbar from `r`.
	match direction:
		case widgets.Scrollable.VERTICAL:
			sbr = geometry.Rectangle(r.x2, r.y1, 1, r.h)
		case widgets.Scrollable.HORIZONTAL:
			sbr = geometry.Rectangle(r.x1, r.y2, r.w, 1)
		case _:
			raise ValueError(
				"draw.scrollbar(): Invalid value for `direction`. \
				Must equal either `Scrollable.VERTICAL`, or `Scrollable.HORIZONTAL`."
			)
	
	if clip and not sbr.intersects(clip):
		return
	
	def draw_vertical():
		# Draw arrows at the top and bottom.
		s.set(sbr.x, sbr.y1, "▴", clip, style)  # ▵ ▿ ▓
		s.set(sbr.x, sbr.y2, "▾", clip, style)
		
		# Draw the bar between the arrows.
		for i in range(sbr.y1 + 1, sbr.y2):
			s.set(sbr.x, i, "░", clip, style)
		
		# Draw the handle.
		handle_offset = int((sbr.h - 2 - handle_length) * scroll_percent)
		for i in range(handle_offset, handle_offset + handle_length):
			s.set(sbr.x, sbr.y1 + 1 + i, "▓", clip, style)
	
	def draw_horizontal():
		# Draw arrows to the left and right.
		s.set(sbr.x1, sbr.y, "◂", clip, style)  # ◃ ▹ ▓
		s.set(sbr.x2, sbr.y, "▸", clip, style)
		
		# Draw the bar between the arrows.
		for i in range(sbr.x1 + 1, sbr.x2):
			s.set(i, sbr.y, "░", clip, style)
		
		# Draw the handle.
		handle_offset = int((sbr.w - 2 - handle_length) * scroll_percent)
		for i in range(handle_offset, handle_offset + handle_length):
			s.set(sbr.x1 + 1 + i, sbr.y, "▓", clip, style)
	
	match direction:
		case widgets.Scrollable.VERTICAL:
			draw_vertical()
		case widgets.Scrollable.HORIZONTAL:
			draw_horizontal()
