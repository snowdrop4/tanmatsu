input
=====

Enums holding values representing mouse button and keyboard key events.

Mouse
-----

In order to define custom mouse events for a widget,
one can override the :meth:`tanmatsu.widgets.Widget.event_event` method:

.. code-block:: python
   
   import tanmatsu.input as ti
   import tanmatsu.geometry as tg
   
   class ExampleWidgetXYZ(ExampleWidgetABC):
       def mouse_event(
           self,
           button: ti.Mouse_button,
           modifier: ti.Mouse_modifier,
           state: ti.Mouse_state,
           position: tg.Point
       ) -> bool:
           # Call super() to check if any parent classes
           # want to consume the event.
           if super().mouse_event(button, modifier, state, position):
               return True
           
           if self.scrollable() is False:
               return False
           
           match button, modifier:
               # Mouse wheel
               case ti.Mouse_button.SCROLL_UP,    ti.Mouse_modifier.NONE:
                   self.scroll(delta_y=-1)
               case ti.Mouse_button.SCROLL_DOWN,  ti.Mouse_modifier.NONE:
                   self.scroll(delta_y=+1)
               # Mouse wheel + shift
               case ti.Mouse_button.SCROLL_UP,    ti.Mouse_modifier.SHIFT:
                   self.scroll(delta_x=-1)
               case ti.Mouse_button.SCROLL_DOWN,  ti.Mouse_modifier.SHIFT:
                   self.scroll(delta_x=+1)
               # return False if the button isn't one we're
               # interested in
               case _:
                   return False
           
           # return True if we didn't hit the fallthrough case,
           # meaning we did find a button we were interested in.
           return True

Mouse Button
^^^^^^^^^^^^

.. autoclass:: tanmatsu.input.Mouse_button
   :members:
   :undoc-members:

Mouse Button Modifiers
^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: tanmatsu.input.Mouse_modifier
   :members:
   :undoc-members:

Mouse State
^^^^^^^^^^^

.. autoclass:: tanmatsu.input.Mouse_state
   :members:
   :undoc-members:

Keyboard
--------

In order to define custom key events for a widget,
one can override the :meth:`tanmatsu.widgets.Widget.keyboard_event` method:

.. code-block:: python
   
   import tanmatsu.input as ti
   
   class ExampleWidgetXYZ(ExampleWidgetABC):
       def keyboard_event(
           self,
           key: ti.Keyboard_key | str,
           modifier: ti.Keyboard_modifier
       ) -> bool:
           # Call super() to check if any parent classes
           # want to consume the event.
           if super().keyboard_event(key, modifier):
               return True
           
           match key:
               case ti.Keyboard_key.ENTER:
                   self.enter_key()
               case 'a':
                   self.latin_a_key()
               case 'あ':
                   self.hiragana_a_key()
               case c if not isinstance(c, ti.Keyboard_key):
                   self.any_character(c)
               case _:
                   # return False if the key isn't one we're
                   # interested in
                   return False
           
           # return True if we didn't hit the fallthrough case,
           # meaning we did find a key we were interested in.
           return True

Keyboard Keys
^^^^^^^^^^^^^

.. autoclass:: tanmatsu.input.Keyboard_key
   :members:
   :undoc-members:

Keyboard Key Modifiers
^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: tanmatsu.input.Keyboard_modifier
   :members:
   :undoc-members:
