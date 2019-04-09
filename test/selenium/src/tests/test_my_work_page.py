# Copyright (C) 2019 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""My Work page smoke tests."""
# pylint: disable=no-self-use
# pylint: disable=invalid-name
# pylint: disable=protected-access
# pylint: disable=too-few-public-methods
# pylint: disable=unused-argument
import re

import pytest  # pylint: disable=import-error

from lib import base, url
from lib.constants import objects
from lib.page import dashboard, lhn
from lib.page.widget import generic_widget, object_modal
from lib.service import webui_facade
from lib.ui import ui_facade
from lib.utils import selenium_utils


class TestMyWorkPage(base.Test):
  """Tests My Work page, part of smoke tests, section 2."""

  @pytest.mark.smoke_tests
  def test_destructive_horizontal_nav_bar_tabs(
      self, objectives_mapped_to_program, my_work_dashboard, selenium
  ):
    """Tests that several objects in widget can be deleted sequentially.
    Preconditions:
    - Controls created via REST API.
    """
    objectives_tab = my_work_dashboard.select_objectives()
    for _ in xrange(objectives_tab.member_count):
      counter = objectives_tab.get_items_count()
      (objectives_tab.select_member_by_num(0).
       three_bbs.select_delete().confirm_delete())
      objectives_tab.wait_member_deleted(counter)
    objectives_generic_widget = generic_widget.Objectives(
        selenium, objects.OBJECTIVES)
    expected_widget_members = []
    actual_widget_members = objectives_generic_widget.members_listed
    assert expected_widget_members == actual_widget_members

  @pytest.mark.smoke_tests
  def test_redirect(self, header_dashboard, selenium):
    """Tests if user is redirected to My Work page after clicking on
    the my work button in user dropdown."""
    header_dashboard.select_my_work()
    expected_url = url.Urls().dashboard + url.Widget.INFO
    actual_url = selenium.current_url
    assert expected_url == actual_url

  @pytest.mark.smoke_tests
  def test_lhn_stays_expanded(self, header_dashboard, selenium):
    """Tests if, after opening LHN, it slides out and stays expanded."""
    lhn_menu = header_dashboard.open_lhn_menu()
    initial_position = lhn_menu.my_objects.element.location
    selenium_utils.wait_until_stops_moving(lhn_menu.my_objects.element)
    selenium_utils.hover_over_element(
        selenium, dashboard.Header(selenium).button_my_tasks.element)
    expected_el_position = initial_position
    actual_el_position = lhn.Menu(selenium).my_objects.element.location
    assert expected_el_position == actual_el_position

  @pytest.mark.smoke_tests
  def test_lhn_remembers_tab_state(self, header_dashboard, selenium):
    """Tests if LHN remembers which tab is selected (my or all objects) after
    closing it."""
    lhn_menu = header_dashboard.open_lhn_menu()
    # check if all objects tab is selected by default
    assert selenium_utils.is_value_in_attr(
        lhn_menu.all_objects.element) is True
    for tab in ['my_objects', 'all_objects']:
      getattr(header_dashboard.open_lhn_menu(), 'select_{0}'.format(tab))()
      header_dashboard.close_lhn_menu()
      selenium.refresh()
      new_lhn_menu = dashboard.Header(selenium).open_lhn_menu()
      # check if selected tab saves state
      assert selenium_utils.is_value_in_attr(
          getattr(new_lhn_menu, tab).element) is True

  @pytest.mark.smoke_tests
  def test_lhn_pin(self, header_dashboard):
    """Tests if pin is present and if it's default state is off."""
    lhn_menu = header_dashboard.open_lhn_menu()
    assert lhn_menu.pin.is_activated is False

  @pytest.mark.smoke_tests
  def test_user_menu_checkbox(self, header_dashboard):
    """Tests user menu checkbox. With that also user menu itself is
    tested since model initializes all elements (and throws and
    exception if they're not present."""
    user_list = header_dashboard.open_user_list()
    user_list.checkbox_daily_digest.click()
    user_list.checkbox_daily_digest.element.get_attribute('disabled')
    # restore previous state
    user_list.checkbox_daily_digest.click()

  @pytest.mark.smoke_tests
  def test_lhn_objects_numbers(self, header_dashboard):
    """Tests LHN menu objects.
    Check LHN contains the list of the objects with number in brackets."""
    lhn_menu = header_dashboard.open_lhn_menu().select_all_objects()
    webui_facade.check_base_objects_have_numbers(lhn_menu)
    webui_facade.check_objects_have_numbers(lhn_menu)

  @pytest.mark.smoke_tests
  @pytest.mark.skip(reason="Will be fixed.")
  def test_lhn_objects_expand_collapse(self, header_dashboard):
    """Tests LHN menu objects.
    Check expand/collapse objects"""
    lhn_menu = header_dashboard.open_lhn_menu().select_all_objects()
    webui_facade.can_base_objects_expand(lhn_menu)
    webui_facade.can_objects_expand(lhn_menu)

  @pytest.mark.smoke_tests
  def test_user_menu_buttons(self, header_dashboard):
    """Tests user menu buttons and their icons (styles for icons)."""
    user_menu = header_dashboard.open_user_list()
    webui_facade.check_user_menu_has_icons(user_menu)

  @pytest.mark.smoke_tests
  def test_lhn_info_popup(self, header_dashboard, program):
    """Tests LHN item info popup."""
    programs = (header_dashboard.open_lhn_menu().select_all_objects().
                select_programs())
    program_title = programs.members_loaded[0].text
    assert program_title == programs.hover_over_visible_member(
        program_title).title.text

  @pytest.mark.smoke_tests
  @pytest.mark.skip(reason="Will be fixed.")
  def test_info_panel_close_button(self, my_work_dashboard, program):
    """Tests My Work Info panel close button."""
    info_panel = (my_work_dashboard.select_programs().tree_view.
                  select_member_by_title(program.title).panel)
    info_panel.button_close.js_click()
    selenium_utils.wait_for_doc_is_ready(my_work_dashboard._driver)
    assert info_panel.is_opened is False

  @pytest.mark.smoke_tests
  @pytest.mark.skip(reason="Will be fixed.")
  def test_info_panel_minimize_button(self, my_work_dashboard, program):
    """Tests My Work Info panel minimize button."""
    program_info_panel = (my_work_dashboard.select_programs().tree_view.
                          select_member_by_title(program.title).panel)
    btn_minimize = program_info_panel.button_minimize
    btn_minimize.js_click()
    assert program_info_panel.is_minimized is True

  @pytest.mark.smoke_tests
  def test_info_panel_maximize_button(self, my_work_dashboard, program):
    """Tests My Work Info panel maximize button."""
    program_info_panel = (my_work_dashboard.select_programs().tree_view.
                          select_member_by_title(program.title).panel)
    program_info_panel.button_minimize.js_click()
    btn_maximize = program_info_panel.button_maximize
    btn_maximize.js_click()
    assert program_info_panel.is_maximized is True

  @pytest.mark.smoke_tests
  @pytest.mark.skip(reason="Will be fixed.")
  def test_info_panel_content(self, my_work_dashboard, program):
    """Tests My Work Info panel content."""
    assert program.title == (
        my_work_dashboard.select_programs().tree_view.
        select_member_by_title(program.title).panel.title)

  @pytest.mark.smoke_tests
  @pytest.mark.skip(reason="Will be fixed.")
  def test_info_panel_3bbs(self, my_work_dashboard, program):
    """Tests My Work Info panel."""
    panel_three_bbs = (my_work_dashboard.select_programs().tree_view.
                       select_member_by_title(program.title).
                       three_bbs)
    assert panel_three_bbs.exists is True

  @pytest.mark.smoke_tests
  def test_navbar_tabs(self, my_work_dashboard):
    """Tests Nav bar on My Work page."""
    tabs = my_work_dashboard.get_visible_tabs
    # At least Info tab should be present
    assert tabs
    for tab in tabs:
      # Check name for each tab
      assert re.match(r'Info|(.*) \((\d*)\)', tab.name) is not None
      # Check icon for each tab
      assert tab.tab_icon.exists is True

  @pytest.mark.smoke_tests
  def test_navbar_add_tab(self, my_work_dashboard):
    """Tests Nav bar Add tab doesn't exist on My Work page."""
    my_work_dashboard.wait_to_be_init()
    assert my_work_dashboard.is_add_tab_present is False

  @pytest.mark.smoke_tests
  @pytest.mark.skip(reason="Will be fixed.")
  def test_all_objects(self, my_work_dashboard):
    """Tests number of objects in LHN and in All Objects."""
    lhn_objects = (my_work_dashboard.open_lhn_menu().select_all_objects().
                   get_all_lhn_objects_as_set)
    hnb_objects = set(
        [tab.name for tab in my_work_dashboard.
         select_all_objects().get_visible_tabs])
    if hnb_objects.issubset(lhn_objects) is False:
      pytest.xfail(
          reason="\nGGRC-2756 Numbers in brackets in LHN are not correspond "
                 "with numbers in tabs on on All objects page:\n" +
                 str(lhn_objects) + "\n" +
                 str(hnb_objects)
      )
    assert hnb_objects.issubset(lhn_objects) is True

  def test_user_cannot_create_control_from_lhn(self, lhn_menu):
    """Tests that `New Control` modal object cannot be opened from lhn."""
    lhn_menu.select_controls_or_objectives().select_controls().create_new()
    ui_facade.verify_modal_obj_not_present_in_all_windows(
        object_modal.ControlModal())
