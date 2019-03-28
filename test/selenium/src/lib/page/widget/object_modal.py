# Copyright (C) 2019 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Modals for creating / making changes to objects:
* New object
* Edit object
* Proposal for object
"""
from lib import base
from lib.constants import objects
from lib.element import page_elements
from lib.entities import entity
from lib.page.error_popup import ErrorPopup
from lib.page.modal import unified_mapper, delete_object
from lib.page.modal.repeat_workflow_modal import RepeatWorkflowModal
from lib.utils import ui_utils


def get_modal_obj(obj_type, _selenium=None):
  """Gets modal obj for `obj_type`."""
  mapping = {
      "assessment": AssessmentModal,
      "control": ControlModal,
      "risk": RiskModal,
      "workflow": WorkflowModal,
      "task_group_task": TaskGroupTaskModal,
      "task_group": TaskGroupModal
  }
  return mapping.get(obj_type.lower(), BaseObjectModal)()


_FIELD_METHOD_MAPPING = {
    "title": "set_title",
    "description": "set_description",
    "status": "set_state",
    "slug": "set_code",
    "assertions": "select_assertions",
    "mapped_objects": "map_objects",
    "task_groups": "set_first_task_group_title",  # workflow,
    "assignees": "set_assignees",  # task
    "start_date": "set_start_date",  # task
    "due_date": "set_due_date",  # task
    "risk_type": "set_risk_type",
    "repeat_unit": "set_repeat_workflow"
}


class BaseObjectModal(base.WithBrowser):
  """Represents object modal."""

  def __init__(self, _driver=None):
    super(BaseObjectModal, self).__init__()
    self._root = self._browser.element(css=".modal[style*='display: block']")
    self.title_field = self._root.text_field(name="title")
    self.description_field = self._root.div(
        data_placeholder="Enter Description")
    self.state_select = self._root.select(can_value="instance.status")
    self.code_field = self._root.text_field(name="slug")
    self._fields = ["title", "description", "status", "slug"]
    self.close_btn = self._root.element(class_name="modal-dismiss")

  def submit_obj(self, obj):
    """Submits form with `obj`."""
    obj_dict = obj.__dict__
    fields_dict = {k: obj_dict[k] for k in self._fields}
    self.fill_form(**fields_dict)
    self.save_and_close()

  def fill_form(self, **fields_dict):
    """Fills form with values from `fields_dict`."""
    for key, value in fields_dict.iteritems():
      if value is not None:
        getattr(self, _FIELD_METHOD_MAPPING[key])(value)

  def save_and_close(self):
    """Clicks Save & Close button and waits for changes to happen."""
    self._root.link(data_toggle="modal-submit", text="Save & Close").click()
    self._wait_for_submit_changes()

  def click_save_btn_causes_error_alert(self):
    """Clicks Save & Close button and wait until error popup appears."""
    # pylint: disable=invalid-name
    self._root.link(data_toggle="modal-submit", text="Save & Close").click()
    ErrorPopup().close_popup()

  def close_and_discard(self):
    """Clicks close button, discards changes on Discard Changes Modal and
    waits until first modal is closed."""
    self.close_btn.wait_until(lambda e: e.exists).click()
    DiscardChangesModal().discard_and_close()
    self._wait_for_submit_changes()

  def delete(self):
    """Clicks Delete button, confirms deletion in new popup
    and waits for changes to happen.
    """
    self._root.link(text="Delete").click()
    delete_object.DeleteObjectModal().confirm_delete()
    self._wait_for_submit_changes()

  def _wait_for_submit_changes(self):
    """Waits for changes after submit."""
    self._root.wait_until(lambda modal: not modal.exists)
    # Spinner sometimes appears for loading content after modal is closed.
    # Though it's not a responsibility of modal to wait for it, it looks
    # to be safe as long as implementation is general.
    ui_utils.wait_for_spinner_to_disappear()

  def set_title(self, title):
    """Sets title."""
    self.title_field.set(title)

  def set_description(self, description):
    """Sets description."""
    self.description_field.clear()
    self.description_field.send_keys(description)

  def set_state(self, state):
    """Sets value in state dropdown."""
    self.state_select.wait_until(lambda e: e.exists).select(state)

  def set_code(self, code):
    """Sets code."""
    self.code_field.set(code)

  def click_propose(self):
    """Click propose button."""
    self._root.link(text="Propose").click()
    self._wait_for_submit_changes()

  @property
  def is_present(self):
    """Checks presence of modal element."""
    return self._root.exist


class DiscardChangesModal(BaseObjectModal):
  """Represents discard changes modal."""

  def __init__(self, _driver=None):
    super(DiscardChangesModal, self).__init__()
    self._root = self._browser.element(
        text="Discard Changes").parent(class_name="undefined")

  def wait_until_present(self):
    """Wait until modal is present."""
    self._root.wait_until(lambda e: e.present)

  def discard_and_close(self):
    """Clicks Discard button and wait for modal is closed."""
    self.wait_until_present()
    self._root.link(text="Discard").click()
    self._wait_for_submit_changes()


class ControlModal(BaseObjectModal):
  """Represents control object modal."""

  def __init__(self, _driver=None):
    super(ControlModal, self).__init__()
    self._root = self._browser.element(
        class_name="modal-header", text="New {}".format(
            objects.get_singular(objects.CONTROLS, title=True))).parent(
                class_name="modal-wide")
    self._fields = ["title", "description", "status", "slug", "assertions"]

  def select_assertions(self, assertions):
    """Selects assertions."""
    multi_select_root = self._root.element(data_id="assertions_dd")
    # Chromedriver's `click` isn't able to work with these elements
    multi_select_root.element(
        class_name="multiselect-dropdown__input").js_click()
    for assertion in assertions:
      multi_select_root.checkbox(id=str(assertion["id"])).js_click()


class RiskModal(BaseObjectModal):
  """Represents risk object modal."""

  def __init__(self, _driver=None):
    super(RiskModal, self).__init__()
    self._fields = ["title", "description", "status", "slug", "risk_type"]

  def set_risk_type(self, risk_type):
    """Set risk type."""
    risk_type_field = self._root.div(data_placeholder="Enter Risk Type")
    risk_type_field.send_keys(risk_type)


class AssessmentModal(BaseObjectModal):
  """Represents assessment object modal."""

  def __init__(self, _driver=None):
    super(AssessmentModal, self).__init__()
    self._fields = ["title", "description", "slug", "mapped_objects"]

  def map_objects(self, objs):
    """Maps objects using `Map Objects` button."""
    objs = [entity.Representation.repr_dict_to_obj(obj)
            if isinstance(obj, dict) else obj for obj in objs]
    # Ordinary `click()` doesn't work in headless Chrome in this case
    self._root.element(class_name="assessment-map-btn").js_click()
    mapper = unified_mapper.AssessmentCreationMapperModal(
        self._driver, "assessments")
    mapper.map_dest_objs(
        dest_objs_type=objs[0].type,
        dest_objs_titles=[obj.title for obj in objs])

  def get_mapped_snapshots_titles(self):
    """Gets titles of mapped snapshots."""
    els = self._root.elements(class_name="modal-mapped-objects-item")
    return [el.element(class_name="title").text for el in els]


class WorkflowModal(BaseObjectModal):
  """Represents workflow object modal."""

  def __init__(self):
    super(WorkflowModal, self).__init__()
    self._fields = ["title", "task_groups", "repeat_unit"]

  def set_first_task_group_title(self, task_groups):
    """Sets First task group's title field."""
    label_el = self._root.element(
        class_name="ggrc-form-item__label", text="First task group's title")
    text_field = label_el.following_sibling(
        class_name="input-block-level").to_subtype()
    text_field.set(task_groups[0].title)

  def set_repeat_workflow(self, repeat_unit=None):
    """Set repeat workflow."""
    if repeat_unit:
      self._root.element(tag_name="repeat-on-button").element(
          tag_name="a").to_subtype().click()
      repeat_modal = RepeatWorkflowModal()
      repeat_modal.set_repeat_checkbox()
      repeat_modal.set_repeats_select(repeat_unit)
      repeat_modal.click_save_and_close_btn()


class TaskGroupTaskModal(BaseObjectModal):
  """Represents task group task object modal."""

  def __init__(self):
    super(TaskGroupTaskModal, self).__init__()
    self._fields = ["title", "assignees", "start_date", "due_date"]
    self._start_date_picker = page_elements.Datepicker(
        self._root.element(date="instance.start_date"))
    self._due_date_picker = page_elements.Datepicker(
        self._root.element(date="instance.end_date"))

  def set_assignees(self, people):
    """Adds assignees to the list of assignees."""
    for person in people:
      related_people_el = page_elements.RelatedPeopleList(
          self._root, "Task Assignees", with_inline_edit=False)
      related_people_el.add_person(person)

  def get_start_date(self):
    """Returns a displayed start date."""
    return self._start_date_picker.get_value()

  def set_start_date(self, date):
    """Sets a date in the start date datepicker."""
    self._start_date_picker.set_value(date)

  def get_due_date(self):
    """Returns a displayed due date."""
    return self._due_date_picker.get_value()

  def set_due_date(self, date):
    """Sets a date in the due date datepicker."""
    self._due_date_picker.set_value(date)


class TaskGroupModal(BaseObjectModal):
  """Represents task group object modal."""

  def __init__(self):
    super(TaskGroupModal, self).__init__()
    self._fields = ["title"]
