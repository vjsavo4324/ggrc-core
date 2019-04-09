# Copyright (C) 2019 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Workflow smoke tests."""
# pylint: disable=no-self-use
# pylint: disable=unused-argument
# pylint: disable=redefined-outer-name
# pylint: disable=invalid-name
import datetime
import pytest
from nerodia.wait.wait import TimeoutError

from lib import base, users
from lib.app_entity_factory import (
    entity_factory_common, workflow_entity_factory)
from lib.constants import messages, roles, workflow_repeat_units
from lib.entities import cycle_entity_population, ui_dict_convert
from lib.page.widget import object_modal, object_page, workflow_tabs
from lib.rest_facades import (
    object_rest_facade, person_rest_facade, workflow_rest_facade)
from lib.rest_services import workflow_rest_service
from lib.ui import daily_emails_ui_facade, ui_facade, workflow_ui_facade
from lib.utils import date_utils, test_utils, ui_utils


@pytest.fixture(params=[roles.CREATOR, roles.READER])
def creator_or_reader(request):
  """Returns a Person with a global role."""
  return person_rest_facade.create_person_with_role(role_name=request.param)


@pytest.fixture()
def login_as_creator_or_reader(creator_or_reader):
  """Logs in as the creator or reader."""
  users.set_current_person(creator_or_reader)


class TestCreateWorkflow(base.Test):
  """Tests for checking results of workflow creation."""

  @pytest.fixture()
  def workflow(self):
    """Create workflow via UI."""
    workflow = workflow_entity_factory.WorkflowFactory().create()
    workflow_entity_factory.TaskGroupFactory().create(workflow=workflow)
    workflow_ui_facade.create_workflow(workflow)
    return workflow

  def test_setup_tab_is_opened_after_workflow_ui_creation(
      self, selenium, workflow
  ):
    """Test that creation of workflow via UI redirects to Setup tab."""
    # pylint: disable=invalid-name
    workflow_tabs.SetupTab().wait_to_be_init()
    assert ui_facade.active_tab_name() == "Setup (1)"

  def test_workflow_info_page_after_workflow_ui_creation(
      self, selenium, workflow
  ):
    """Test that creation of workflow via UI corrects a correct object."""
    # pylint: disable=invalid-name
    actual_workflow = ui_facade.get_obj(workflow)
    test_utils.set_unknown_attrs_to_none(actual_workflow)
    test_utils.obj_assert(actual_workflow, workflow)

  def test_task_group_created_after_workflow_ui_creation(
      self, selenium, workflow
  ):
    """Test that creation of workflow via UI creates a task group."""
    # pylint: disable=invalid-name
    actual_task_groups = workflow_ui_facade.task_group_objs(
        workflow)
    test_utils.list_obj_assert(actual_task_groups, workflow.task_groups)

  def test_create_repeate_on_workflow(
      self, login_as_creator_or_reader, selenium
  ):
    """Test creation repeat on workflow."""
    workflow = workflow_entity_factory.WorkflowFactory().create(
        repeat_every=1, repeat_unit=workflow_repeat_units.WEEKDAY)
    workflow_entity_factory.TaskGroupFactory().create(workflow=workflow)
    workflow_ui_facade.create_workflow(workflow)
    actual_workflow = ui_facade.get_obj(workflow)
    object_rest_facade.set_attrs_via_get(workflow, ["created_at"])
    object_rest_facade.set_attrs_via_get(workflow, ["updated_at"])
    test_utils.obj_assert(actual_workflow, workflow)


class TestWorkflowInfoPage(base.Test):
  """Test workflow Info page."""

  def test_read_workflow_as_member(self, creator_or_reader, selenium):
    """Test opening workflow as workflow member."""
    workflow = workflow_rest_facade.create_workflow(
        wf_members=[creator_or_reader])
    object_rest_facade.set_attrs_via_get(workflow.modified_by, ["email"])
    users.set_current_person(creator_or_reader)
    actual_workflow = ui_facade.get_obj(workflow)
    test_utils.obj_assert(actual_workflow, workflow)

  def test_edit_workflow(
      self, login_as_creator_or_reader, app_workflow, selenium
  ):
    """Test editing workflow."""
    new_title = "[EDITED]" + app_workflow.title
    ui_facade.edit_obj(app_workflow, title=new_title)
    app_workflow.title = new_title
    actual_workflow = ui_facade.get_obj(app_workflow)
    object_rest_facade.set_attrs_via_get(app_workflow, ["updated_at"])
    test_utils.obj_assert(actual_workflow, app_workflow)

  def test_delete_workflow(
      self, login_as_creator_or_reader, app_workflow, selenium
  ):
    """Test deletion of workflow."""
    ui_facade.delete_obj(app_workflow)
    ui_facade.open_obj(app_workflow)
    assert ui_utils.is_error_404()

  def test_destructive_archive_workflow(
      self, login_as_creator_or_reader, activated_repeat_on_workflow, selenium
  ):
    """Test archiving of workflow.
    This test is marked as destructive as different users can't edit different
    objects in parallel (GGRC-6305).
    """
    # pylint: disable=invalid-name
    workflow_ui_facade.archive_workflow(activated_repeat_on_workflow)
    actual_workflow = ui_facade.get_obj(activated_repeat_on_workflow)
    object_rest_facade.set_attrs_via_get(
        activated_repeat_on_workflow, ["updated_at"])
    test_utils.obj_assert(actual_workflow, activated_repeat_on_workflow)


class TestWorkflowSetupTab(base.Test):
  """Test actions available on workflow Setup tab."""

  def test_default_values_in_create_task_popup(
      self, app_workflow, app_task_group, selenium
  ):
    """Test expected default values in Create Task popup."""
    # pylint: disable=invalid-name
    workflow_ui_facade.open_create_task_group_task_popup(app_task_group)
    task_modal = object_modal.get_modal_obj("task_group_task")
    actual_start_date = ui_dict_convert.str_to_date(
        task_modal.get_start_date())
    actual_due_date = ui_dict_convert.str_to_date(
        task_modal.get_due_date())
    assert actual_start_date == date_utils.first_not_weekend_day(
        datetime.date.today())
    assert actual_due_date == actual_start_date + datetime.timedelta(days=7)

  def test_create_task_group_task(
      self, app_workflow, app_task_group, app_person, selenium
  ):
    """Test creation of Task Group Task."""
    task = workflow_entity_factory.TaskGroupTaskFactory().create(
        task_group=app_task_group, assignees=[app_person])
    workflow_ui_facade.create_task_group_task(task)
    actual_tasks = workflow_ui_facade.get_task_group_tasks_objs()
    test_utils.list_obj_assert(actual_tasks, [task])

  @pytest.mark.xfail(raises=AssertionError)
  def test_add_obj_to_task_group(
      self, app_workflow, app_task_group, app_control, selenium
  ):
    """Test mapping of object to a task group."""
    workflow_ui_facade.add_obj_to_task_group(
        obj=app_control, task_group=app_task_group)
    selenium.refresh()  # reload page to check mapping is saved
    objs = workflow_ui_facade.get_objs_added_to_task_group(app_task_group)
    test_utils.list_obj_assert(objs, [app_control])

  def test_delete_task_group(self, app_workflow, app_task_group, selenium):
    """Test deletion of task group."""
    workflow_ui_facade.delete_task_group(app_task_group)
    assert not workflow_ui_facade.task_group_objs(app_workflow)
    assert ui_facade.active_tab_name() == "Setup (0)"

  def test_add_task_group(self, app_workflow, selenium):
    """Test creation of task group."""
    task_group = workflow_entity_factory.TaskGroupFactory().create()
    workflow_ui_facade.add_task_group(app_workflow, task_group)
    assert workflow_ui_facade.task_group_objs(app_workflow)
    assert ui_facade.active_tab_name() == "Setup (1)"


class TestActivateWorkflow(base.Test):
  """Test workflow activation and actions available after activation."""
  _data = None

  @pytest.fixture()
  def activate_workflow(
      self, app_workflow, app_task_group, app_task_group_task, selenium
  ):
    """Activates workflow."""
    workflow_ui_facade.activate_workflow(app_workflow)

  @pytest.fixture()
  def test_data(self):
    """Creates an activated workflow with close due date."""
    if not TestActivateWorkflow._data:
      app_workflow = workflow_rest_facade.create_workflow()
      task_group = workflow_rest_facade.create_task_group(
          workflow=app_workflow)
      assignee = person_rest_facade.create_person_with_role(roles.CREATOR)
      due_date = date_utils.first_working_day_after_today(
          datetime.date.today())
      workflow_rest_facade.create_task_group_task(
          task_group=task_group, assignees=[assignee], due_date=due_date)
      workflow_rest_service.WorkflowRestService().activate(app_workflow)
      # handle GGRC-6527 only
      try:
        emails = daily_emails_ui_facade.get_emails_by_user_names(
            [users.current_user().name, assignee.name])
      except TimeoutError as err:
        if "digest" in err.message:
          pytest.xfail("GGRC-6527: Digest is not opened")
        else:
          raise err
      TestActivateWorkflow._data = {
          "wf": app_workflow,
          "wf_creator_email": emails[users.current_user().name],
          "assignee_email": emails[assignee.name]}
    return TestActivateWorkflow._data

  def test_active_cycles_tab_after_workflow_activation(
      self, activate_workflow
  ):
    """Test Active Cycles tab after activation of workflow."""
    # pylint: disable=invalid-name
    assert ui_facade.active_tab_name() == "Active Cycles (1)"

  def test_destructive_assigned_task_notification(
      self, selenium, test_data
  ):
    """Test cycle task assignee has notification about assigned tasks."""
    assert (test_data["wf"].task_groups[0].task_group_tasks[0].title in
            test_data["assignee_email"].assigned_tasks)

  def xfail_if_time_delta_more_2d(self, start_date, due_date):
    """Xfail test when time delta is bigger than 2 days, because
    notification section with due very soon tasks will not have cycle
    task.
    """
    if due_date - start_date > datetime.timedelta(days=2):
      pytest.xfail(
          reason="\nTime difference between start date and due date is more "
                 "than 2 days.\nStart date: {0}\nDue date: {1}\nSection with "
                 "due very soon tasks will not have this cycle "
                 "task.\n".format(start_date, due_date))

  def test_destructive_due_soon_task_notification(
      self, selenium, test_data
  ):
    """Test cycle task assignee has notification about due very soon tasks."""
    self.xfail_if_time_delta_more_2d(
        test_data["wf"].task_groups[0].task_group_tasks[0].start_date,
        test_data["wf"].task_groups[0].task_group_tasks[0].due_date)
    assert (test_data["wf"].task_groups[0].task_group_tasks[0].title in
            test_data["assignee_email"].due_soon_tasks)

  def test_destructive_new_wf_cycle_notification(
      self, selenium, test_data
  ):
    """Test cycle task creator has notification about new wf started."""
    assert (test_data["wf"].title in
            test_data["wf_creator_email"].new_wf_cycles)

  def test_history_tab_after_workflow_activation(self, activate_workflow):
    """Test History tab after activation of workflow."""
    # pylint: disable=invalid-name
    assert "History (0)" in object_page.ObjectPage().top_tabs.tab_names

  def test_active_cycles_task_tree(self, activate_workflow, app_workflow):
    """Test active cycles tree."""
    workflow_cycles = workflow_ui_facade.get_workflow_cycles(
        app_workflow)
    expected_workflow_cycle = cycle_entity_population.create_workflow_cycle(
        app_workflow)
    test_utils.list_obj_assert(workflow_cycles, [expected_workflow_cycle])

  @classmethod
  def check_ggrc_6490(cls, actual_due_date, expected_due_date):
    """Particular check if issue in app exist or not according to GGRC-6490."""
    if actual_due_date != expected_due_date:
      pytest.xfail(
          reason="\nGGRC-6490 Workflow actual and expected due dates are not "
                 "equal:\n" +
                 messages.AssertionMessages.format_err_msg_equal(
                     actual_due_date, expected_due_date))

  @classmethod
  def check_ggrc_6491(cls, actual_wf_cycles, expected_wf_cycles):
    """Particular check if issue in app exist or not according to GGRC-6491.
    This issue is about 2 wf cycles created with the same titles instead of 1.
    """
    cls.check_ggrc_6490(
        actual_wf_cycles[0].due_date, expected_wf_cycles[0].due_date)
    if (
        len(actual_wf_cycles) > len(expected_wf_cycles) and
        datetime.datetime.utcnow().hour in range(0, 9)
    ):
      pytest.xfail(
          reason="\nGGRC-6491 There are more than 1 equal workflows:\n")
    elif len(actual_wf_cycles) != len(expected_wf_cycles):
      pytest.fail(msg="\nThere are different workflow count:\n" +
                      len(actual_wf_cycles))

  def test_destructive_activate_repeat_on_workflow(
      self, app_repeat_on_workflow, selenium
  ):
    """Test activation of repeat on workflow.
    It should be checked separately as different requests are sent when
    repeat off and repeat on workflows are activated.
    """
    task_group = workflow_rest_facade.create_task_group(
        workflow=app_repeat_on_workflow)
    workflow_rest_facade.create_task_group_task(task_group=task_group)
    workflow_ui_facade.activate_workflow(app_repeat_on_workflow)
    workflow_cycles = workflow_ui_facade.get_workflow_cycles(
        app_repeat_on_workflow)
    expected_workflow_cycle = cycle_entity_population.create_workflow_cycle(
        app_repeat_on_workflow)
    self.check_ggrc_6491(workflow_cycles, [expected_workflow_cycle])
    test_utils.list_obj_assert(workflow_cycles, [expected_workflow_cycle])


class TestActiveCyclesTab(base.Test):
  """Test Active Cycles tab."""

  @pytest.mark.xfail(raises=AttributeError)
  def test_map_obj_to_cycle_task(
      self, activated_workflow, app_control, selenium
  ):
    """Test mapping of obj to a cycle task."""
    cycle_task = cycle_entity_population.create_workflow_cycle(
        activated_workflow).cycle_task_groups[0].cycle_tasks[0]
    workflow_ui_facade.map_obj_to_cycle_task(
        obj=app_control, cycle_task=cycle_task)
    selenium.refresh()  # reload page to check mapping is saved
    objs = workflow_ui_facade.get_objs_mapped_to_cycle_task(cycle_task)
    test_utils.list_obj_assert(objs, [app_control])

  def test_move_cycle_task_to_another_state(
      self, login_as_creator_or_reader, activated_workflow, selenium
  ):
    """Test starting a cycle task."""
    # pylint: disable=invalid-name
    workflow_cycle = cycle_entity_population.create_workflow_cycle(
        activated_workflow)
    cycle_task = workflow_cycle.cycle_task_groups[0].cycle_tasks[0]
    workflow_ui_facade.start_cycle_task(cycle_task)
    selenium.refresh()  # reload page to check state is changed
    actual_workflow_cycles = workflow_ui_facade.get_workflow_cycles(
        activated_workflow)
    test_utils.list_obj_assert(actual_workflow_cycles, [workflow_cycle])

  @pytest.fixture()
  def some_creator(self):
    """Creates some global creator."""
    return person_rest_facade.create_person_with_role(roles.CREATOR)

  def test_add_cycle_task_assignee(
      self, some_creator, login_as_creator_or_reader, activated_workflow,
      selenium
  ):
    """Test adding a cycle task assignee."""
    cycle_task = cycle_entity_population.create_workflow_cycle(
        activated_workflow).cycle_task_groups[0].cycle_tasks[0]
    workflow_ui_facade.add_assignee_to_cycle_task(
        assignee=some_creator, cycle_task=cycle_task)
    selenium.refresh()  # reload page to check change is saved
    actual_cycle_task = workflow_ui_facade.get_cycle_task(cycle_task)
    test_utils.obj_assert(actual_cycle_task, cycle_task)

  def test_add_comment_to_cycle_task(
      self, login_as_creator_or_reader, activated_workflow, selenium
  ):
    """Test adding a comment to the cycle task."""
    cycle_task = cycle_entity_population.create_workflow_cycle(
        activated_workflow).cycle_task_groups[0].cycle_tasks[0]
    comment = entity_factory_common.CommentFactory().create(
        description="comment")
    workflow_ui_facade.add_comment_to_cycle_task(
        comment=comment, cycle_task=cycle_task)
    selenium.refresh()  # reload page to check change is saved
    actual_cycle_task = workflow_ui_facade.get_cycle_task(cycle_task)
    test_utils.set_unknown_attrs_to_none(actual_cycle_task.comments[0])
    test_utils.obj_assert(actual_cycle_task, cycle_task)
