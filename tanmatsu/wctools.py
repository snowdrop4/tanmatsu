from wcwidth import wcwidth, wcswidth


# Returns the substring that is `prefix_length` columns long, starting from the
# beginning of string `s`.
def wcslice(s: str, prefix_length: int) -> str:
	i = 0
	total_width = 0
	
	while i < prefix_length and i < len(s):
		char_width = wcwidth(s[i])
		
		if total_width + char_width > prefix_length:
			return s[:i]
		
		total_width += char_width
		i += 1
	
	return s[:i]


# Find `c` in `s`, in range `start` to `end`.
# 
# `start` and `end` are offsets in string `s`. The return value of this function
# is also an offset in string `s`, or -1 if `c` cannot be found.
# 
# This function is character width aware, meaning that it counts the total
# width of the characters encountered against `end`, rather than the total
# number of characters encountered, when determining whether `end` has been
# reached and the search should thus be terminated.
# 
# wcfind("いろaは", "a", 0, 3) == -1, because "a" is outside the search range.
# 
# wcfind("いろaは", "a", 0, 5) ==  3, because "a" is inside the search range,
#                                    and 3 is the character offset in the string of "a".
def wcfind(s: str, c: str, start: int, end: int) -> int:
	total_width = 0
	
	for (i, v) in enumerate(s[start:]):
		total_width += wcwidth(v)
		if start + total_width >= end:
			return -1
		if v == c:
			return start + i
	
	return -1


def wcoffset_to_column(s: str, o: int) -> int:
	return wcswidth(s[:o + 1])


def wccolumn_to_offset(s: str, c: int) -> int:
	total_width = 0
	for (i, v) in enumerate(s):
		char_width = wcwidth(v)
		if total_width + char_width > c:
			return i
		else:
			total_width += char_width
	return i


# Returns string `s` cropped to `length`. The last character in the returned
# string will be "…" if a crop took place.
def wccrop(s: str, length: int) -> str:
	cropped = wcslice(s, length)
	
	# Did the label get cropped?
	if len(cropped) < len(s):
		# If there's one column of space at the end of the cropped label,
		# append the elision indicator to the end:
		if wcswidth(cropped) == length - 1:
			cropped = cropped + "…"
		# Otherwise, change the last character to the elision indicator:
		else:
			cropped = cropped[:-1] + "…"
	
	return cropped
