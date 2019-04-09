# coding=utf-8
# Copyright (C) 2019 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Widgets other than Info widget."""

import re
from selenium.common import exceptions

from lib import base, factory
from lib.constants import locator, regex, element, counters, messages, objects
from lib.page.modal import unified_mapper
from lib.utils import selenium_utils


class Widget(base.Widget):
  """All widgets with Tree View and Filters."""
  # pylint: disable=too-many-instance-attributes
  def __init__(self, driver, obj_name, is_versions_widget=False):
    self.obj_name = obj_name
    self._locators_filter = locator.BaseWidgetGeneric
    self._locators_widget = factory.get_locator_widget(
        self.obj_name.upper())
    if is_versions_widget:
      locator_parts = self._locators_widget[1].split("\"")
      locator_parts[1] += "_version"
      self._locators_widget = (self._locators_widget[0], "\"".join(
          locator_parts))
      objects.get_singular(self.obj_name) + "_version".upper()
    self.info_widget_cls = factory.get_cls_widget(
        object_name=obj_name, is_info=True)
    # Filter
    self.button_help = base.Button(driver, self._locators_filter.HELP_BTN_CSS)
    self.filter = base.FilterCommon(
        driver, text_box_locator=self._locators_filter.TXTFIELD_TO_FILTER_CSS,
        bt_submit_locator=self._locators_filter.FILTER_BTN_CSS)
    if self.obj_name not in objects.ALL_OBJS_WO_STATE_FILTERING:
      self.dropdown_states = base.DropdownStatic(
          driver, self._locators_filter.DD_CSS)
    super(Widget, self).__init__(driver)
    # Tree View
    self.tree_view = TreeView(driver, self.info_widget_cls, self.obj_name)
    # Tab count
    self.members_listed = None
    self.member_count = None
    self._set_members_listed()

  def _set_member_count(self):
    """Parses widget name and number of items from widget tab title."""
    widget_label = selenium_utils.get_when_visible(
        self._driver, self._locators_widget).text
    # The widget label has 2 forms: "widget_name_plural (number_of_items)"
    # and "number_of_items" and they change depending on how many widgets
    # are open. In order to handle both forms, we first try to parse the
    # first form and only then the second one.
    parsed_label = re.match(regex.WIDGET_TITLE_AND_COUNT, widget_label)
    item_count = (
        widget_label if parsed_label is None else parsed_label.group(2))
    self.member_count = int(item_count)

  def _set_members_listed(self):
    """Wait for listed members to loaded and add them to local container."""
    self._set_member_count()
    if self.member_count:
      # wait until the elements are loaded
      selenium_utils.get_when_invisible(
          self._driver, locator.ObjectWidget.LOADING)
      self.members_listed = self._driver.find_elements(
          *locator.ObjectWidget.MEMBERS_TITLE_LIST)
    else:
      self.members_listed = []

  def wait_and_get_pagination_controllers(self):
    """Wait for pagination controllers on filter panel and footer to be
    visible. First element have to belong filter panel, second - to footer.
    """
    # pylint: disable=invalid-name
    exp_pagination_count = counters.PAGINATION_CTRLS_COUNT
    pagination_elements = selenium_utils.get_when_all_visible(
        self._driver, self._locators_filter.PAGINATION_CONTROLLERS_CSS)
    if pagination_elements:
      if len(pagination_elements) == exp_pagination_count:
        return pagination_elements
      else:
        raise ValueError(messages.ExceptionsMessages.
                         err_pagination_count.format(exp_pagination_count))
    else:
      raise exceptions.NoSuchElementException(
          messages.ExceptionsMessages.err_pagination_elements.format(",".join(
              ["".join(pag_el.text.splitlines())
               for pag_el in pagination_elements])))

  def verify_counter_not_loaded(self):
    """Check that in case of empty table, counter not loaded on filter panel.
    """
    selenium_utils.wait_for_element_text(
        self._driver, locator.TreeView.NO_RESULTS_MSG_CSS,
        element.GenericWidget.NO_FILTER_RESULTS)

  def get_items_count(self):
    """Get elements' count from pagination controller on filter panel."""
    selenium_utils.wait_for_js_to_load(self._driver)
    return self.wait_and_get_pagination_controllers()[0].text.split("of ")[1]

  def wait_member_deleted(self, count):
    """Wait until elements' counter on filter panel refreshed with new value.
    Args: count (str)
    """
    selenium_utils.wait_for_js_to_load(self._driver)
    if count != '1':
      new_count = ' {}'.format(int(count) - 1)
      selenium_utils.wait_for_element_text(
          self._driver, self._locators_filter.PAGINATION_CONTROLLERS_CSS,
          new_count)
    else:
      self.verify_counter_not_loaded()

  def select_member_by_num(self, num):
    """Select member from list of members by number (start from 0).
    Args: num (int)
    Return: lib.page.widget.info.Widget
    """
    # pylint: disable=not-callable
    selenium_utils.wait_for_js_to_load(self._driver)
    self._set_members_listed()
    # need "try-except" block due to issue GGRC-1675
    try:
      member = self.members_listed[num]
      # wait for the listed items animation to stop
      selenium_utils.wait_until_stops_moving(member)
      selenium_utils.click_via_js(self._driver, member)
      # wait for the info pane animation to stop
      info_panel = selenium_utils.get_when_clickable(
          self._driver, locator.ObjectWidget.INFO_PANE)
      selenium_utils.wait_until_stops_moving(info_panel)
    except exceptions.StaleElementReferenceException:
      self.members_listed = self._driver.find_elements(
          *locator.ObjectWidget.MEMBERS_TITLE_LIST)
      return self.select_member_by_num(num)
    except exceptions.TimeoutException:
      # sometimes the click to the listed member results in hover
      return self.select_member_by_num(num)
    return self.info_widget_cls(self._driver)


class TreeView(base.TreeView):
  """Genetic Tree Views."""
  # pylint: disable=too-many-instance-attributes
  _locators = locator.TreeView

  def __init__(self, driver, info_widget_cls, obj_name):
    super(TreeView, self).__init__(driver, obj_name)
    self.info_widget_cls = info_widget_cls
    self.obj_name = obj_name
    self.dropdown_settings_cls = factory.get_cls_3bbs_dropdown_settings(
        object_name=obj_name)
    self.dropdown_tree_view_item_cls = factory.get_cls_dropdown_tree_view_item(
        object_name=obj_name)
    self.fields_to_set = factory.get_fields_to_set(object_name=obj_name)
    self.locator_set_visible_fields = self._locators.SHOW_FIELDS_BTN_CSS
    selenium_utils.wait_until_not_present(
        self._driver, locator.Common.SPINNER_CSS)

  def open_create(self):
    """Clicks on Create button on Tree View to open new object creation modal.
    """
    self._browser.element(class_name="tree-action").link(text="Create").click()
    if self.obj_name == objects.ASSESSMENT_TEMPLATES:
      unified_mapper.CloneOrCreateAssessmentTemplatesModal(
          self._driver, self.obj_name).create_asmt_tmpl_btn.click()

  def open_map(self):
    """Click to Map button on Tree View to open unified mapper modal.

    Return: lib.page.modal.unified_mapper.MapObjectsModal
    """
    self._browser.link(text="Map").click()
    return unified_mapper.MapObjectsModal(self._driver, self.obj_name)

  def open_3bbs(self):
    """Click to 3BBS button on Tree View to open tree view 3BBS modal.

    Return: lib.element.tree_view."obj_name"DropdownSettings
    """
    base.Button(self._driver, self._locators.BTN_3BBS_CSS).click()
    return self.dropdown_settings_cls(self._driver, self.obj_name)

  def select_member_by_title(self, title):
    """Select member on Tree View by title.
    Return: lib.page.widget.info_widget."obj_name"
    """
    item_num = self._get_item_num_by_title(title)
    return (Widget(self._driver, self.obj_name).
            select_member_by_num(item_num))

  def _get_item_num_by_title(self, title):
    """Return number of item by title"""
    list_items = [item.text.splitlines() for item in
                  self.tree_view_items()]
    item_num = next(num for num, item in enumerate(list_items)
                    if title in item)
    return item_num

  def find_row(self, obj_str):
    """Find row. Raise exception if more than 1 row were found.

    Return: lib.base.TreeViewItem
    """
    search_field = self._browser.element(class_name="tree-filter__input")
    search_field.send_keys(obj_str)
    search_button = self._browser.element(text="Search")
    search_button.click()
    if len(self.tree_view_items()) > 1:
      raise ValueError("More than 1 row were found.")
    return self.tree_view_items()[0]

  def open_tree_actions_dropdown_by_title(self, title):
    """Open dropdown of obj on Tree View by title. Hover mouse on dropdown
    button.

    Return: lib.element.tree_view."dropdown_obj"
    """
    # pylint: disable=invalid-name
    obj = self.find_row(title)
    item_dropdown_button = obj.item_btn
    selenium_utils.hover_over_element(
        self._driver, obj.element)
    selenium_utils.hover_over_element(
        self._driver, item_dropdown_button)
    item_dropdown_button.click()
    dropdown_menu_element = item_dropdown_button.find_element(
        *self._locators.ITEM_DD_MENU_CSS)
    return self.dropdown_tree_view_item_cls(self._driver, self.obj_name,
                                            dropdown_menu_element)

  def get_obj_url_from_tree_view_by_title(self, obj_title):
    """Get url of obj from Tree View by title."""
    # pylint: disable=invalid-name
    self.open_tree_actions_dropdown_by_title(obj_title)
    link = self._browser.link(text="Open in a new tab")
    return link.attribute_value("href")


class Audits(Widget):
  """Model for Audits generic widgets."""


class AssessmentTemplates(Widget):
  """Model for Assessment Templates generic widgets."""


class Assessments(Widget):
  """Model for Assessments generic widgets."""
  _locators = locator.Assessments

  def show_generated_results(self):
    """Wait for Assessments generated successfully message.
    Click on link to show them.
    """
    base.Element(self._driver,
                 self._locators.SHOW_GENERATED_ASSESSMENTS).click()


class Controls(Widget):
  """Model for Controls generic widgets."""


class Objectives(Widget):
  """Model for Objectives generic widgets."""


class Risks(Widget):
  """Model for Risks generic widgets."""


class OrgGroups(Widget):
  """Model for Org Groups generic widgets."""


class Issues(Widget):
  """Model for Issues generic widgets"""


class Programs(Widget):
  """Model for Programs generic widgets"""


class Processes(Widget):
  """Model for Process generic widgets."""


class DataAssets(Widget):
  """Model for Data Assets generic widgets."""


class Systems(Widget):
  """Model for Systems generic widgets."""


class Products(Widget):
  """Model for Products generic widgets."""


class Projects(Widget):
  """Model for Projects generic widgets."""


class Proposals(Widget):
  """Model for Proposals generic widgets."""
