# About

Declarative TUI (Terminal User Interface) library, with layout features modelled after modern web components.

The syntax will be familiar with anyone who's used Django models before. Widget objects can be created declaratively by creating a class that inherits from the desired widget class.

A CSS flexbox-style widget that contains a text box and a button can be created declaratively, like so:

```python
class NiceFlexBox(widgets.FlexBox):
	text_box = widgets.TextBox(text="Hello World!")
	button = widgets.Button(label="Button 2", callback=None)
	
	class Meta:
		border_label = "Nice FlexBox"

nice_flex_box = NiceFlexBox()

```

or imperatively, like so:

```python
children = {
	'text_box': widgets.TextBox(text="Hello World!"),
	'button': widgets.Button(label="Button 2", callback=None)
}

nice_flex_box = widgets.FlexBox(children=children, border_label="Nice FlexBox")

```

# Example

![tanmatsu example screenshot](/screenshots/main.png)

which is given by the code:

```python
from tanmatsu import Tanmatsu, widgets


class ButtonList(widgets.List):
	class Meta:
		border_label = "List"
		children = [
			widgets.Button(label="Button 1", callback=None),
			widgets.Button(label="Button 2", callback=None),
			widgets.Button(label="Button 3", callback=None),
		]
		item_height = 5


class VertSplit(widgets.FlexBox):
	text_box = widgets.TextBox(border_label="Text Box", text="Hello World!")
	text_log = widgets.TextLog(border_label="Text Log")
	button_list = ButtonList()
	
	class Meta:
		flex_direction = widgets.FlexBox.HORIZONTAL


with Tanmatsu(title="Tanmatsu!") as t:
	rw = VertSplit()
	t.set_root_widget(rw)
	
	for (i, v) in enumerate(rw.button_list.children):
		v.callback = lambda i=i: rw.text_log.append_line(f"Button {i + 1} pressed")
	
	t.loop()
```

# Documentation

https://tanmatsu.readthedocs.io/en/latest/

# Requirements

* Python >=3.11
* GNU/Linux
* Full-featured terminal emulator (e.g., Gnome VTE)

# Dependencies

* tri.declarative
* parsy
* sphinx
* wcwidth

# Development

## Installing

1. Install [pyenv](https://github.com/pyenv/pyenv) (intructions in the `README.md`)
2. Install [pipenv](https://github.com/pypa/pipenv) with `pip3 install pipenv`
3. Run `pipenv install` from the repository directory to set up a virtual environment with the necessary python version and packages

## Running

`pipenv run python3 main.py`

## Testing

`pipenv run python3 -m unittest`

# License

MIT. For more information, see `LICENSE.md`
