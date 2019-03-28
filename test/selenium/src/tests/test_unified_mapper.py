# Copyright (C) 2019 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Unified mapper tests."""
# pylint: disable=no-self-use
# pylint: disable=invalid-name
# pylint: disable=redefined-outer-name
# pylint: disable=unused-argument

import pytest

from lib import base, users
from lib.constants import objects
from lib.entities.entity import Representation
from lib.service import webui_service, rest_facade


class TestProgramPage(base.Test):
  """Tests of unified mapper."""

  @pytest.mark.smoke_tests
  @pytest.mark.skip(reason="Will be fixed.")
  def test_destructive_mapping_controls_to_program_via_unified_mapper(
      self, program, controls, selenium
  ):
    """Check if Controls can be mapped to Program from Controls widget under
    Program page via unified mapper.
    Preconditions:
    - Program, Controls created via REST API.
    """
    expected_controls = [
        expected_control.repr_ui() for expected_control
        in controls]
    controls_ui_service = webui_service.ControlsService(selenium)
    controls_ui_service.map_objs_via_tree_view(
        src_obj=program, dest_objs=expected_controls)
    actual_controls_tab_count = controls_ui_service.get_count_objs_from_tab(
        src_obj=program)
    assert len(expected_controls) == actual_controls_tab_count
    actual_controls = controls_ui_service.get_list_objs_from_tree_view(
        src_obj=program)
    # 'actual_controls': created_at, updated_at, custom_attributes (None)
    self.general_equal_assert(
        sorted(expected_controls), sorted(actual_controls),
        *Representation.tree_view_attrs_to_exclude)

  @pytest.mark.smoke_tests
  @pytest.mark.skip(reason="Controls can be created only via rest.")
  def test_create_and_map_control(
      self, set_external_user_as_current_user, program, selenium
  ):
    """Test that control can be created and mapped using Unified mapper."""
    # pylint: disable=unused-argument
    from lib.service import webui_facade
    control = webui_facade.create_control_in_program_scope(selenium, program)
    controls_service = webui_service.ControlsService(selenium)
    tree_view_control = controls_service.get_list_objs_from_tree_view(
        program)[0]
    actual_control = controls_service.get_obj_from_info_page(tree_view_control)
    rest_control = rest_facade.get_obj(actual_control)
    control.update_attrs(
        created_at=rest_control.created_at,
        updated_at=rest_control.updated_at,
        modified_by=users.current_user(),
        slug=rest_control.slug).repr_ui()
    self.general_equal_assert(control, actual_control, "custom_attributes")

  def test_no_modal_for_program_control(self, login_as_creator, program,
                                        selenium):
    """Tests that 'New Control' modal is not opened
    when creator adds control to a program."""
    programs_service = webui_service.ProgramsService(selenium)
    programs_service.open_info_page_of_obj(program)
    obj_modal = programs_service.add_and_map_obj_widget(objects.CONTROLS)
    assert not obj_modal.is_present, ("'New Control' modal "
                                      "should not be present.")
