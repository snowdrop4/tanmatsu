import builtins


__lines = []
__output_widget = None


def set_output_widget(ow):
	global __output_widget
	__output_widget = ow


def print(s):
	if type(s) is not str:
		s = str(s)
	
	__lines.append(s)
	
	if __output_widget is not None:
		__output_widget.append_line(s)


def flush_print_buffer():
	for i in __lines:
		builtins.print(i)
	
	__lines.clear()
