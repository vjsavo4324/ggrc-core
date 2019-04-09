# Copyright (C) 2019 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Create object tests."""
# pylint: disable=no-self-use
# pylint: disable=unused-argument
# pylint: disable=redefined-outer-name


import pytest

from lib import base
from lib import users
from lib.constants import roles
from lib.constants import objects
from lib.rest_facades import person_rest_facade
from lib.service import webui_facade
from lib.ui import ui_facade


@pytest.fixture(params=[roles.ADMINISTRATOR, roles.CREATOR,
                        roles.READER, roles.EDITOR])
def person_with_role(request):
  """Returns a Person with a global role."""
  return person_rest_facade.create_person_with_role(role_name=request.param)


@pytest.fixture()
def login_as_person_with_role(person_with_role):
  """Logs in as person with role."""
  users.set_current_person(person_with_role)


@pytest.mark.create_object
class TestCreateObject(base.Test):
  """Tests for checking create object process."""

  def test_create_control_no_modal(self, selenium,
                                   login_as_person_with_role):
    """Test to check that no modal present
    after starting create object control."""
    if users.current_user().system_wide_role == roles.ADMINISTRATOR:
      pytest.xfail(reason="GGRC-6934 Create object is not present.")
    obj_modal = webui_facade.open_create_obj_modal(
        obj_type=objects.get_singular(objects.CONTROLS, title=True))
    ui_facade.verify_modal_obj_not_present_in_all_windows(obj_modal)
