from typing import Generator

from wcwidth import wcwidth


def wcwidth2(c: str) -> int:
	"""
	This function is the same as wcwidth, except it does not return -1 on
	encountering a newline character, and instead treats newline characters
	as having a width of 1.
	"""
	if c == "\n":
		return 1
	else:
		return wcwidth(c)


def wcswidth2(s: str) -> int:
	"""
	This function is same as wcswidth, except instead of stopping execution and
	return -1 on encountering a newline character, it counts the newline
	character as having a width of 1.
	"""
	accum = 0
	
	for c in s:
		width = wcwidth2(c)
		if width == -1:
			return -1
		accum += width
	
	return accum


def wcslice(s: str, prefix_length: int) -> str:
	"""
	Returns the substring that is `prefix_length` columns long, starting from
	the beginning of string `s`.
	"""
	i = 0
	total_width = 0
	
	while i < prefix_length and i < len(s):
		char_width = wcwidth2(s[i])
		
		if total_width + char_width > prefix_length:
			return s[:i]
		
		total_width += char_width
		i += 1
	
	return s[:i]


def wcfind(s: str, c: str, start: int, end: int) -> int:
	"""
	Find `c` in `s`, in range `start` to `end`.
	
	`start` and `end` are offsets in string `s`. The return value of this function
	is also an offset in string `s`, or -1 if `c` cannot be found.
	
	This function is character width aware, meaning that it counts the total
	width of the characters encountered against `end`, rather than the total
	number of characters encountered, when determining whether `end` has been
	reached and thus whether the search should be terminated.
	
	wcfind("いろaは", "a", 0, 3) == -1, because "a" is outside the search range.
	
	wcfind("いろaは", "a", 0, 5) ==  3, because "a" is inside the search range,
	                                   and 3 is the character offset in the string of "a".
	"""
	
	total_width = 0
	
	for (i, v) in enumerate(s[start:]):
		total_width += wcwidth2(v)
		if start + total_width >= end:
			return -1
		if v == c:
			return start + i
	
	return -1


def wcoffset_to_column(s: str, o: int) -> int:
	"""
	Given offset `o` in string `s`, returns the column corresponding to
	that offset.
	"""
	return wcswidth2(s[:o + 1]) - 1


def wccolumn_to_offset(s: str, c: int) -> int:
	"""
	Given column `c` in string `s`, returns the offset corresponding to that
	column.
	"""
	total_width = 0
	
	for (i, v) in enumerate(s):
		char_width = wcwidth2(v)
		if total_width + char_width > c:
			return i
		else:
			total_width += char_width
	
	return i


def wccrop(s: str, length: int) -> str:
	"""
	Returns string `s` cropped to `length`. The last character in the returned
	string will be "…" if a crop took place.
	"""
	cropped = wcslice(s, length)
	
	# Did the label get cropped?
	if len(cropped) < len(s):
		# If there's one column of space at the end of the cropped label,
		# append the elision indicator to the end:
		if wcswidth2(cropped) == length - 1:
			cropped = cropped + "…"
		# Otherwise, change the last character to the elision indicator:
		else:
			cropped = cropped[:-1] + "…"
	
	return cropped


def wcchunks(s: str, column_width: int) -> Generator[str, None, None]:
	"""
	Returns substrings of `s` that are each `column_width` wide,
	except for the last line and in cases of non-perfect wrapping due to
	wide characters.
	"""
	i = 0
	while i < len(s):
		chunk = wcslice(s[i:], column_width)
		i += len(chunk)
		yield chunk


def inclusive_split(s: str, c: str):
	i = 0
	
	while i < len(s):
		nc = s.find(c, i)
		
		if nc == -1:
			yield s[i:]
			return
		else:
			yield s[i:nc + 1]
			i = nc + 1


def wcwrap(s: str, wrap_width: int) -> Generator[list[str], None, None]:
	if s[-1] != "\n":
		s = s + " "
	
	split = inclusive_split(s, "\n")
	
	for i in split:
		last = list(wcchunks(i, wrap_width))
		yield last
	
	if last[-1][-1] == "\n":
		yield [" "]
