```haskell
      :~^:.             :YJ?!                            .Y&J?^                 
      %@@P!     :GG&!   ~@@&:   .PGP?                     B@&~.                 
      !@@%      :&@J    ^@@?    .#@B.                     G@#            ^!.    
      !@@%  !^  :&@?    ^@@?     #@G     :%~~~~~~~~~~~~~~^B@#~^~~~~~~~~~Y@@#Y^  
 ~?!!!J@@Y~Y&&P^.&@&~!!!?&@&!!!!!&@B     :!!~~~~~~~~~~~~~~B@&~~~~~~~~~~~~~~~!^  
 :~^:^::::%Y?%~.:@@J::::::::::::^PBY                      G@#                   
  :&      &@@?:.:%%: ..     .... ^PG?:                    G@#         .?~       
   PG     B@&  JJ%%%%%%?B#G?%%%%%J&&&J:     ^?!!~~~~~~~~~~B@&!~~~~~~~%B@@B%.    
   ~@P   :@&:          %@B^                 .!~^^^^^^^^^P@@@&G!^^^^^^^^^^^~.    
   .#@?  ?@J   :&?^:::^#&:.:..::::JP?^                :G@G#@#~P%                
    P@G  G#.   .&@P!!%#@Y!!Y&#%!!%@@&%              .Y@&? G@# :PB!              
    Y@! ^&~  ::.#@J  .&@%  !@&.   #@%             .J&&J.  G@#.  %##J:           
    ..  YB%??!..#@J  .#@%  %@&.  .#@%           ^Y#B%.    G@#.   .?#@G?^.       
  .^!?&GGJ!:   .#@J  .#@%  %@&.  .#@%        .%PBY^       B@#.     .%G@@#PJ!~^. 
.P&&#&%^       .&@J  .&@%  %@&:   #@%     .~J&J~          B@#.        ^JB@@@#J^ 
 ~#!           :&@J  .&@?  ?@@^~!%&@%    ^?!^            .#@&.           :!J^   
               :#&?   ?J^  ^J?..:P#P!                     B@#:                  
 ^GGGGGG^   %P~ ..  %P!  ?P^   ?Y~   .Y&:     ?P^   ?GGGGGG:. ^YPPJ^   .&Y  %P~ 
 .~!@@%~:  .&@G     B@@~ P@!   G@L:  Y@@~    :@@P   ^~&G&~^  !@B~!&@^  :B&. &B% 
    #&.    J@%@~    B@@#.&@!   G@@A /@@@~    Y@@%.   Y@%    !@G^. ^/   :B#. &B% 
   .#&:   .&!^&G    B@Y&.P@!   G@#B@&PG@~   :@<^G%    Y@%     \&BBG%   :B#. &B% 
   .#&:   J@! #@~   B@!!@@@!   G@^\J@^G@~   Y@! &@:   Y@%    .:  .B@~  :B#  &B% 
   .&@:  .&&%%?@G   B@% J@@!   G@~ ^/ G@~  :@#%^J@%   Y@%    %@P~~J@^  .#B%~B@~ 
   .PP.  !B?   &G:  ?B~  &G~   YG^    YG^  %B%   &P.  !B?     %PBG&~    :YGBP!  
```

# About

Declarative TUI (Terminal User Interface) library, with layout features modelled after modern web components.

Widget objects can be created by defining a class that inherits from the desired widget class.

For example, a CSS flexbox-style widget that contains a text box and a button can be created declaratively, like so:

```python
class NiceFlexBox(widgets.FlexBox):
    text_box = widgets.TextBox(text="Hello World!")
    button   = widgets.Button(label="Button 2", callback=None)
    
    class Meta:
        border_label = "Nice FlexBox"

nice_flex_box = NiceFlexBox()

```

or imperatively, like so:

```python
children = {
    'text_box': widgets.TextBox(text="Hello World!"),
    'button':   widgets.Button(label="Button 2", callback=None)
}

nice_flex_box = widgets.FlexBox(children=children, border_label="Nice FlexBox")

```

Tanmatsu supports either style. The declarative syntax should be familiar with anyone who's used Django models before.

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

# Installation

`pip install tanmatsu`

# Documentation

https://tanmatsu.readthedocs.io/en/latest/

# Requirements

* Python >=3.11
* GNU/Linux
* Full-featured terminal emulator (e.g., Gnome VTE)
* A font with unicode symbols (e.g., [Noto](https://fonts.google.com/noto))

# Dependencies

* tri.declarative
* parsy
* wcwidth

Development dependancies:

* sphinx

# Development

## Installing

1. If not running python 3.11, install [pyenv](https://github.com/pyenv/pyenv).
2. Install [poetry](https://python-poetry.org/docs/).
3. Run `poetry install` from the repository directory to set up a virtual environment with the necessary python version and packages

## Running

`poetry run python3 main.py`

## Testing

`poetry run python3 -m unittest`

# Changelog

See [CHANGELOG.md](../master/CHANGELOG.md).

# License

MIT. For more information, see [LICENSE.md](../master/LICENSE.md).
