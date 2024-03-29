# 0.2.0

## Features

* `widgets.FlexBox`: add `justify_content` layout option

# Changes

* `widgets.FlexBox`: rename possible values for `flex_direction` to `column` and `row`, to 100% match CSS.
* `size`: change behaviour and rename the classes used for specifying widget size to be more robust

# 0.1.1

## Bugfixes

* Fix scrolling

# 0.1.0

## Features

* `widgets.Container`: added `add_child`, `del_child_by_name`, and `del_child_by_widget` methods, and updated methods for deleting and adding tabs in `widgets.TabBox` to be consistent.
* `widgets.Box`: added `border` and `border_label` properties.
* `widgets.Scrollable`: switched `scrollable` and `get/set_scroll_direction` methods over to properties.
* `widgets.List`: switched `active_child` method over to property

## Bugfixes

* Fix crash on user input in 0.0.1 due to wrong parsy version.

# 0.0.1

Initial release.
