# Copyright (C) 2019 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""General UI facade."""
from lib import users, browsers
from lib.entities import entity_operations
from lib.page.widget import object_page, object_modal
from lib.ui import internal_ui_operations
from lib.utils import selenium_utils


def open_obj(obj):
  """Opens the url of obj."""
  selenium_utils.open_url(entity_operations.obj_url(obj))


def get_obj(obj):
  """Opens the url of `app_obj`, builds the object from the page and
  returns it.
  """
  open_obj(obj)
  return internal_ui_operations.build_obj(obj)


def edit_obj(obj, **changes):
  """Updates object."""
  open_obj(obj)
  internal_ui_operations.info_widget_page(obj).edit_obj(**changes)
  obj.modified_by = users.current_person()


def delete_obj(obj):
  """Deletes object."""
  open_obj(obj)
  internal_ui_operations.info_widget_page(obj).delete_obj()


def active_tab_name():
  """Returns a tab name of the active tab."""
  return object_page.ObjectPage().top_tabs.active_tab.name


def verify_modal_obj_not_present_in_all_windows(modal_obj):
  """Verifies that object is not present in any window."""
  assert issubclass(modal_obj.__class__,
                    object_modal.BaseObjectModal), ("Object should be derived "
                                                    "from BaseObjectModal.")
  for window in browsers.get_browser().windows():
    window.use()
    assert not modal_obj.is_present, ("Modal object {} should not be "
                                      "present.".format(modal_obj.__class__))
