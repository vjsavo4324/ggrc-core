# Copyright (C) 2019 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>

"""Integration tests for IssueTracker updates via import cases."""

# pylint: disable=invalid-name,too-many-public-methods

from collections import OrderedDict

import ddt
import mock

from ggrc import settings, models, db
from ggrc.models import all_models
from ggrc.converters import errors
from ggrc.converters.handlers import issue_tracker
from ggrc.integrations.constants import DEFAULT_ISSUETRACKER_VALUES as \
    default_values

from integration import ggrc
from integration.ggrc.models import factories
from integration.ggrc.api_helper import Api


@ddt.ddt
class TestIssueTrackedImport(ggrc.TestCase):
  """Test cases for IssueTracker integration via import."""

  def setUp(self):
    """setUp"""
    # pylint: disable=super-on-old-class
    super(TestIssueTrackedImport, self).setUp()
    self.api = Api()
    self.client.get("/login")

    self.patch_create_issue = mock.patch(
        'ggrc.integrations.issues.Client.create_issue')
    self.mock_create_issue = self.patch_create_issue.start()
    self.patch_update_issue = mock.patch(
        'ggrc.integrations.issues.Client.update_issue')
    self.mock_update_issue = self.patch_update_issue.start()

  def tearDown(self):
    """tearDown"""
    self.patch_update_issue.stop()
    self.patch_create_issue.stop()

  def _assert_integration_state(self, obj, value):
    """Make assertion to check Ticket Tracker Integration field."""
    expected_res = bool(value in
                        issue_tracker.IssueTrackerEnabledHandler.TRUE_VALUES)

    self.assertEqual(bool(obj.issue_tracker["enabled"]),
                     expected_res)

  def test_asmt_creation_detached(self):
    """Test assessment creation via import detached from IssueTracker hooks."""
    self.import_file("assessment_full_no_warnings.csv")
    self.mock_create_issue.assert_not_called()

  @mock.patch.object(settings, "ISSUE_TRACKER_ENABLED", True)
  def test_issue_creation_detached(self):
    """Test issue creation via import detached from IssueTracker hooks."""
    self.import_file("issue_for_import.csv")
    self.mock_create_issue.assert_not_called()

  @ddt.data(
      ("Issue", "Issue", "component_id", "Component ID", 123),
      ("Issue", "Issue", "hotlist_id", "Hotlist ID", 321),
      ("Issue", "Issue", "issue_priority", "Priority", "P1"),
      ("Issue", "Issue", "issue_severity", "Severity", "S1"),
      ("Issue", "Issue", "issue_type", "Issue Type", "PROCESS"),
      ("Issue", "Issue", "title", "Ticket Title", "iti_title"),
      ("Assessment", "Assessment", "component_id", "Component ID", 123),
      ("Assessment", "Assessment", "hotlist_id", "Hotlist ID", 321),
      ("Assessment", "Assessment", "issue_priority", "Priority", "P1"),
      ("Assessment", "Assessment", "issue_severity", "Severity", "S1"),
      ("Assessment", "Assessment", "issue_type", "Issue Type", "PROCESS"),
      ("Assessment", "Assessment", "title", "Ticket Title", "iti_title"),
      ("Audit", "Audit", "component_id", "Component ID", 123),
      ("Audit", "Audit", "hotlist_id", "Hotlist ID", 321),
      ("Audit", "Audit", "issue_priority", "Priority", "P1"),
      ("Audit", "Audit", "issue_severity", "Severity", "S1"),
      ("Audit", "Audit", "issue_type", "Issue Type", "PROCESS"),
      ("AssessmentTemplate", "Assessment Template", "component_id",
       "Component ID", 123),
      ("AssessmentTemplate", "Assessment Template", "hotlist_id",
       "Hotlist ID", 321),
      ("AssessmentTemplate", "Assessment Template", "issue_priority",
       "Priority", "P1"),
      ("AssessmentTemplate", "Assessment Template", "issue_severity",
       "Severity", "S1"),
      ("AssessmentTemplate", "Assessment Template", "issue_type",
       "Issue Type", "PROCESS"),
  )
  @ddt.unpack
  def test_import_update_succeed(self, model, model_name, field, alias, value):
    # pylint: disable=too-many-arguments
    """Test {0} {2} set correctly during update via import."""
    with factories.single_commit():
      factory = factories.get_model_factory(model)
      obj = factory()
      factories.IssueTrackerIssueFactory(
          issue_tracked_obj=obj,
      )

    response = self.import_data(OrderedDict([
        ("object_type", model_name),
        ("Code*", obj.slug),
        (alias, value),
    ]))

    obj = models.get_model(model).query.one()
    self._check_csv_response(response, {})
    self.assertEqual(str(obj.issue_tracker[field]), str(value))

  @ddt.data(
      ("Issue", "Issue", "on"),
      ("Issue", "Issue", "off"),
      ("Audit", "Audit", "on"),
      ("Audit", "Audit", "off"),
      ("AssessmentTemplate", "Assessment Template", "on"),
      ("AssessmentTemplate", "Assessment Template", "off"),
  )
  @ddt.unpack
  @mock.patch.object(settings, "ISSUE_TRACKER_ENABLED", True)
  def test_import_enabled_update_succeed(self, model, model_name, value):
    """Test {0} integration state={2} set correctly when updated via import."""
    with factories.single_commit():
      factory = factories.get_model_factory(model)
      obj = factory()
      factories.IssueTrackerIssueFactory(
          issue_tracked_obj=obj,
      )

    response = self.import_data(OrderedDict([
        ("object_type", model_name),
        ("Code*", obj.slug),
        ("Ticket Tracker Integration", value),
    ]))

    obj = models.get_model(model).query.one()
    self._check_csv_response(response, {})
    self._assert_integration_state(obj, value)

  @ddt.data("on", "off")
  @mock.patch.object(settings, "ISSUE_TRACKER_ENABLED", True)
  def test_assmt_import_enabled_update_succeed(self, value):
    """Test Assmt integr state={0} set correctly when updated via import."""
    with factories.single_commit():
      audit = factories.AuditFactory()
      factories.IssueTrackerIssueFactory(
          issue_tracked_obj=audit,
          enabled=True,
      )
      assmt = factories.AssessmentFactory(audit=audit)
      factories.IssueTrackerIssueFactory(
          issue_tracked_obj=assmt,
      )

    response = self.import_data(OrderedDict([
        ("object_type", "Assessment"),
        ("Code*", assmt.slug),
        ("Ticket Tracker Integration", value),
    ]))

    obj = all_models.Assessment.query.one()
    self._check_csv_response(response, {})
    self._assert_integration_state(obj, value)

  @ddt.data("on", "off")
  @mock.patch.object(settings, "ISSUE_TRACKER_ENABLED", True)
  def test_enabled_state_issue_create_succeed(self, value):
    """Test Issue integr state={0} set correctly during create via import."""
    response = self.import_data(OrderedDict([
        ("object_type", "Issue"),
        ("Code*", "OBJ-1"),
        ("Admin", "user@example.com"),
        ("Title", "Object Title"),
        ("Ticket Tracker Integration", value),
    ]))

    self._check_csv_response(response, {})
    obj = all_models.Issue.query.one()
    self._assert_integration_state(obj, value)

  @ddt.data("on", "off")
  @mock.patch.object(settings, "ISSUE_TRACKER_ENABLED", True)
  def test_enabled_state_assmt_create_succeed(self, value):
    """Test Assessment integration state={0} set correctly during create."""
    audit = factories.AuditFactory()
    factories.IssueTrackerIssueFactory(
        issue_tracked_obj=audit,
        enabled=True,
    )
    response = self.import_data(OrderedDict([
        ("object_type", "Assessment"),
        ("Code*", "OBJ-1"),
        ("Audit*", audit.slug),
        ("Assignees*", "user@example.com"),
        ("Creators", "user@example.com"),
        ("Title", "Object Title"),
        ("Ticket Tracker Integration", value),
    ]))

    self._check_csv_response(response, {})
    obj = all_models.Assessment.query.one()
    self._assert_integration_state(obj, value)
    self.mock_create_issue.assert_not_called()

  @ddt.data(
      (True, "off", "off"),
      (True, "on", "on"),
      (False, "off", "off"),
      (False, "on", "off"),
      (None, "off", "off"),
      (None, "on", "off"),
  )
  @ddt.unpack
  @mock.patch.object(settings, "ISSUE_TRACKER_ENABLED", True)
  def test_enabled_state_assmt_tmpl_create_succeed(self, audit_value,
                                                   tmpl_value, expected):
    """Test Template set integr state={2} if audit integr={0} and csv={1}"""
    audit = factories.AuditFactory()
    if audit_value is not None:
      factories.IssueTrackerIssueFactory(
          issue_tracked_obj=audit,
          enabled=audit_value
      )

    response = self.import_data(OrderedDict([
        ("object_type", "Assessment Template"),
        ("Code*", "OBJ-1"),
        ("Audit*", audit.slug),
        ("Default Assignees*", "user@example.com"),
        ("Object Under Assessment", "Control"),
        ("Title", "Object Title"),
        ("Ticket Tracker Integration", tmpl_value),
    ]))

    self._check_csv_response(response, {})
    obj = all_models.AssessmentTemplate.query.one()
    self._assert_integration_state(obj, expected)

  @ddt.data(
      ("Issue", "Issue"),
      ("Assessment", "Assessment"),
      ("Audit", "Audit"),
      ("AssessmentTemplate", "Assessment Template"),
  )
  @ddt.unpack
  @mock.patch.object(settings, "ISSUE_TRACKER_ENABLED", True)
  def test_enabled_state_default_value(self, model, model_name):
    """Test correct default value was set to {0} enabled during import."""
    factory = factories.get_model_factory(model)
    obj = factory()
    expected_warning = (
        errors.WRONG_VALUE_DEFAULT.format(
            line=3,
            column_name="Ticket Tracker Integration",
        )
    )

    expected_messages = {
        model_name: {
            "row_warnings": {expected_warning},
        }
    }
    response = self.import_data(OrderedDict([
        ("object_type", model_name),
        ("Code*", obj.slug),
        ("Ticket Tracker Integration", ""),
    ]))
    self._check_csv_response(response, expected_messages)
    obj = models.get_model(model).query.one()
    self.assertEqual(obj.issue_tracker["enabled"], False)

  @ddt.data(
      ("component_id", "Component ID", 123),
      ("hotlist_id", "Hotlist ID", 321),
      ("issue_priority", "Priority", "P1"),
      ("issue_severity", "Severity", "S1"),
      ("issue_type", "Issue Type", "PROCESS"),
      ("title", "Ticket Title", "iti_title"),
  )
  @ddt.unpack
  def test_issue_import_create_succeed(self, field, alias, value):
    """Test Issue {1} set correctly during create via import."""
    response = self.import_data(OrderedDict([
        ("object_type", "Issue"),
        ("Code*", "OBJ-1"),
        ("Admin", "user@example.com"),
        ("Title", "Object Title"),
        (alias, value),
    ]))

    self._check_csv_response(response, {})
    obj = all_models.Issue.query.one()
    self.assertEqual(str(obj.issue_tracker[field]), str(value))

  @ddt.data(
      ("component_id", "Component ID", 555),
      ("hotlist_id", "Hotlist ID", 444),
      ("issue_priority", "Priority", "P2"),
      ("issue_severity", "Severity", "S2"),
      ("issue_type", "Issue Type", "PROCESS"),
      ("title", "Ticket Title", "iti_title"),
  )
  @ddt.unpack
  def test_assmt_import_create_succeed(self, field, alias, value):
    """Test Assessment {1} set correctly during create via import."""
    audit = factories.AuditFactory()
    response = self.import_data(OrderedDict([
        ("object_type", "Assessment"),
        ("Code*", "OBJ-1"),
        ("Audit*", audit.slug),
        ("Assignees*", "user@example.com"),
        ("Creators", "user@example.com"),
        ("Title", "Object Title"),
        (alias, value),
    ]))

    self._check_csv_response(response, {})
    obj = all_models.Assessment.query.one()
    self.assertEqual(str(obj.issue_tracker[field]), str(value))

  @ddt.data(
      ("component_id", "Component ID", 555),
      ("hotlist_id", "Hotlist ID", 444),
      ("issue_priority", "Priority", "P2"),
      ("issue_severity", "Severity", "S2"),
      ("issue_type", "Issue Type", "PROCESS"),
  )
  @ddt.unpack
  def test_assmt_tmpl_import_create_succeed(self, field, alias, value):
    """Test Assessment Template {1} set correctly during create via import."""
    audit = factories.AuditFactory()

    response = self.import_data(OrderedDict([
        ("object_type", "Assessment Template"),
        ("Code*", "OBJ-1"),
        ("Audit*", audit.slug),
        ("Default Assignees*", "user@example.com"),
        ("Object Under Assessment", "Control"),
        ("Title", "Object Title"),
        (alias, value),
    ]))

    self._check_csv_response(response, {})
    obj = all_models.AssessmentTemplate.query.one()
    self.assertEqual(str(obj.issue_tracker[field]), str(value))

  @ddt.data(
      ("issue_priority", "Priority", ""),
      ("issue_priority", "Priority", "P6"),
      ("issue_severity", "Severity", ""),
      ("issue_severity", "Severity", "aa"),
      ("issue_type", "Issue Type", ""),
      ("issue_type", "Issue Type", "PARABOLA"),
      ("issue_type", "Issue Type", "BUG"),
  )
  @ddt.unpack
  def test_default_value_set_correctly(self, missed_field, alias, value):
    """Test correct default value was set if csv."{1}"={2!r} during import."""
    expected_warning = (
        errors.WRONG_VALUE_DEFAULT.format(line=3, column_name=alias)
    )
    expected_messages = {
        "Issue": {
            "row_warnings": {expected_warning},
        }
    }
    response = self.import_data(OrderedDict([
        ("object_type", "Issue"),
        ("Code*", "ISSUE-1"),
        ("Admin", "user@example.com"),
        ("Title", "Issue Title"),
        (alias, value),
    ]))
    self._check_csv_response(response, expected_messages)
    issue = all_models.Issue.query.one()
    self.assertEqual(str(issue.issue_tracker[missed_field]),
                     str(default_values[missed_field]))

  @ddt.data("", "aaa")
  def test_default_hotlist_for_issue(self, value):
    """Test correct default hotlist was set to Issue during import."""
    expected_warning = (
        errors.WRONG_VALUE_DEFAULT.format(line=3, column_name="Hotlist ID")
    )
    expected_messages = {
        "Issue": {
            "row_warnings": {expected_warning},
        }
    }
    response = self.import_data(OrderedDict([
        ("object_type", "Issue"),
        ("Code*", "ISSUE-1"),
        ("Admin", "user@example.com"),
        ("Title", "Issue Title"),
        ("Hotlist ID", value),
    ]))
    self._check_csv_response(response, expected_messages)
    issue = all_models.Issue.query.one()
    self.assertEqual(str(issue.issue_tracker["hotlist_id"]),
                     str(default_values["issue_hotlist_id"]))

  @ddt.data("", "aaa")
  def test_default_component_for_issue(self, value):
    """Test correct default component was set to Issue during import."""
    expected_warning = (
        errors.WRONG_VALUE_DEFAULT.format(line=3, column_name="Component ID")
    )
    expected_messages = {
        "Issue": {
            "row_warnings": {expected_warning},
        }
    }
    response = self.import_data(OrderedDict([
        ("object_type", "Issue"),
        ("Code*", "ISSUE-1"),
        ("Admin", "user@example.com"),
        ("Title", "Issue Title"),
        ("Component ID", value),
    ]))
    self._check_csv_response(response, expected_messages)
    issue = all_models.Issue.query.one()
    self.assertEqual(str(issue.issue_tracker["component_id"]),
                     str(default_values["issue_component_id"]))

  @ddt.data(
      ("component_id", "Component ID", ""),
      ("component_id", "Component ID", "sss"),
      ("hotlist_id", "Hotlist ID", ""),
      ("hotlist_id", "Hotlist ID", "aaa"),
      ("issue_priority", "Priority", ""),
      ("issue_priority", "Priority", "P6"),
      ("issue_severity", "Severity", ""),
      ("issue_severity", "Severity", "aa"),
      ("issue_type", "Issue Type", ""),
      ("issue_type", "Issue Type", "PARABOLA"),
  )
  @ddt.unpack
  def test_audit_default_value_set_correctly(self, missed_field, alias, value):
    """Test correct default value was set to Audit {1} during import"""
    program = factories.ProgramFactory()
    expected_warning = (
        errors.WRONG_VALUE_DEFAULT.format(line=3, column_name=alias)
    )
    expected_messages = {
        "Audit": {
            "row_warnings": {expected_warning},
        }
    }
    response = self.import_data(OrderedDict([
        ("object_type", "Audit"),
        ("Code*", "slug-1"),
        ("Program", program.slug),
        ("Title", "Audit Title"),
        ("State", "Planned"),
        ("Audit Captains", "user@example.com"),
        (alias, value),
    ]))
    self._check_csv_response(response, expected_messages)
    issue = all_models.Audit.query.one()
    self.assertEqual(str(issue.issue_tracker[missed_field]),
                     str(default_values[missed_field]))

  @ddt.data(
      ("component_id", "Component ID", 123),
      ("hotlist_id", "Hotlist ID", 321),
      ("issue_priority", "Priority", "P1"),
      ("issue_severity", "Severity", "S1"),
      ("issue_type", "Issue Type", "PROCESS"),
  )
  @ddt.unpack
  def test_audit_import_create_succeed(self, field, alias, value):
    """Test Audit "{0}"={2} set correctly during create via import."""
    program = factories.ProgramFactory()
    response = self.import_data(OrderedDict([
        ("object_type", "Audit"),
        ("Code*", "slug-1"),
        ("Program", program.slug),
        ("Title", "Audit Title"),
        ("State", "Planned"),
        ("Audit Captains", "user@example.com"),
        (alias, value),
    ]))

    self._check_csv_response(response, {})
    obj = all_models.Audit.query.one()
    self.assertEqual(str(obj.issue_tracker[field]), str(value))

  @ddt.data("on", "off")
  @mock.patch.object(settings, "ISSUE_TRACKER_ENABLED", True)
  def test_enabled_state_audit_create_succeed(self, value):
    """Test Audit integration={0} set correctly during create via import."""
    program = factories.ProgramFactory()
    response = self.import_data(OrderedDict([
        ("object_type", "Audit"),
        ("Code*", "slug-1"),
        ("Program", program.slug),
        ("Title", "Audit Title"),
        ("State", "Planned"),
        ("Audit Captains", "user@example.com"),
        ("Ticket Tracker Integration", value),
    ]))

    self._check_csv_response(response, {})
    obj = all_models.Audit.query.one()
    self._assert_integration_state(obj, value)

  @ddt.data("Issue", "Assessment")
  def test_default_value_title(self, model):
    """Test correct default value was set to {0} Ticket Title during import."""
    factory = factories.get_model_factory(model)
    obj = factory(title="Object Title")
    expected_warning = (
        errors.WRONG_VALUE_DEFAULT.format(line=3, column_name="Ticket Title")
    )
    expected_messages = {
        model: {
            "row_warnings": {expected_warning},
        }
    }
    response = self.import_data(OrderedDict([
        ("object_type", model),
        ("Code*", obj.slug),
        ("Ticket Title", ""),
    ]))
    self._check_csv_response(response, expected_messages)
    obj = models.get_model(model).query.one()
    self.assertEqual(obj.issue_tracker["title"], obj.title)

  @mock.patch.object(settings, "ISSUE_TRACKER_ENABLED", True)
  def test_bulk_create_from_import(self):
    """Test data was imported and tickets were updated using bulk mechanism."""
    response = self.import_file("issuetracker_no_warnings.csv")
    self._check_csv_response(response, {})
    iti = all_models.IssuetrackerIssue
    assmt_iti = iti.query.filter(iti.object_type == "Assessment").one()
    assmt_iti.enabled = True
    assmt_iti.title = ''
    issue_iti = iti.query.filter(iti.object_type == "Issue").one()
    issue_iti.enabled = True
    issue_iti.issue_id = 123
    db.session.commit()

    with mock.patch("ggrc.notifications.common.send_email") as send_mock:
      self.import_data(OrderedDict([
          ("object_type", "Assessment"),
          ("code", "ASSESSMENT-1"),
          ("title", "Title1"),
      ]))
    send_mock.assert_called_once()
    self.mock_create_issue.assert_called_once()
    with mock.patch(
        "ggrc.integrations.issues.Client.update_issue"
    ) as update_mock:
      with mock.patch("ggrc.notifications.common.send_email") as send_mock:
        self.import_data(OrderedDict([
            ("object_type", "Issue"),
            ("code", "ISSUE-1"),
            ("priority", "P1"),
        ]))
    send_mock.assert_called_once()
    update_mock.assert_called_once()

  @ddt.data(
      ("component_id", "Component ID", "", 123),
      ("component_id", "Component ID", "sss", 456),
      ("hotlist_id", "Hotlist ID", "", 789),
      ("hotlist_id", "Hotlist ID", "aaa", 589),
      ("issue_priority", "Priority", "", "P4"),
      ("issue_priority", "Priority", "P6", "P0"),
      ("issue_severity", "Severity", "", "S1"),
      ("issue_severity", "Severity", "aa", "S3"),
      ("issue_type", "Issue Type", "", "PROCESS"),
      ("issue_type", "Issue Type", "PARABOLA", "PROCESS"),
  )
  @ddt.unpack
  def test_assmt_default_values_from_audit(self,
                                           missed_field,
                                           alias,
                                           value,
                                           audit_value):
    """Test correct default value was set from audit to {0}"""
    expected_warning = (
        errors.WRONG_VALUE_DEFAULT.format(line=3, column_name=alias)
    )
    expected_messages = {
        "Assessment": {
            "row_warnings": {expected_warning},
        }
    }

    with factories.single_commit():
      audit = factories.AuditFactory()
      iti = factories.IssueTrackerIssueFactory(issue_tracked_obj=audit)
      setattr(iti, missed_field, audit_value)

    response = self.import_data(OrderedDict([
        ("object_type", "Assessment"),
        ("Code*", "OBJ-1"),
        ("Audit*", audit.slug),
        ("Assignees*", "user@example.com"),
        ("Creators", "user@example.com"),
        ("Title", "Object Title"),
        (alias, value),
    ]))

    self._check_csv_response(response, expected_messages)
    obj = all_models.Assessment.query.one()
    self.assertEqual(str(obj.issue_tracker[missed_field]),
                     str(audit_value))

  @ddt.data(
      ("component_id", "Component ID", ""),
      ("component_id", "Component ID", "sss"),
      ("hotlist_id", "Hotlist ID", ""),
      ("hotlist_id", "Hotlist ID", "aaa"),
      ("issue_priority", "Priority", ""),
      ("issue_priority", "Priority", "P6"),
      ("issue_severity", "Severity", ""),
      ("issue_severity", "Severity", "aa"),
      ("issue_type", "Issue Type", ""),
      ("issue_type", "Issue Type", "PARABOLA"),
  )
  @ddt.unpack
  def test_assmt_default_values_from_default(self,
                                             missed_field,
                                             alias,
                                             value):
    """Test correct default value was set to {0} if audit doesn't have one"""
    expected_warning = (
        errors.WRONG_VALUE_DEFAULT.format(line=3, column_name=alias)
    )

    expected_messages = {
        "Assessment": {
            "row_warnings": {expected_warning},
        }
    }

    with factories.single_commit():
      audit = factories.AuditFactory()
      factories.IssueTrackerIssueFactory(issue_tracked_obj=audit)

    response = self.import_data(OrderedDict([
        ("object_type", "Assessment"),
        ("Code*", "OBJ-1"),
        ("Audit*", audit.slug),
        ("Assignees*", "user@example.com"),
        ("Creators", "user@example.com"),
        ("Title", "Object Title"),
        (alias, value),
    ]))

    self._check_csv_response(response, expected_messages)
    obj = all_models.Assessment.query.one()
    self.assertEqual(str(obj.issue_tracker[missed_field]),
                     str(default_values[missed_field]))

  @ddt.data(
      ("component_id", "Component ID", "", 123),
      ("component_id", "Component ID", "sss", 456),
      ("hotlist_id", "Hotlist ID", "", 789),
      ("hotlist_id", "Hotlist ID", "aaa", 589),
      ("issue_priority", "Priority", "", "P4"),
      ("issue_priority", "Priority", "P6", "P0"),
      ("issue_severity", "Severity", "", "S1"),
      ("issue_severity", "Severity", "aa", "S3"),
      ("issue_type", "Issue Type", "", "PROCESS"),
      ("issue_type", "Issue Type", "PARABOLA", "PROCESS"),
  )
  @ddt.unpack
  def test_assmt_tmpl_default_values_from_audit(self,
                                                missed_field,
                                                alias,
                                                value,
                                                audit_value):
    """Test default value was set from audit to {0} for Assesment Template"""
    expected_warning = (
        errors.WRONG_VALUE_DEFAULT.format(line=3, column_name=alias)
    )
    expected_messages = {
        "Assessment Template": {
            "row_warnings": {expected_warning},
        }
    }

    with factories.single_commit():
      audit = factories.AuditFactory()
      iti = factories.IssueTrackerIssueFactory(issue_tracked_obj=audit)
      setattr(iti, missed_field, audit_value)

    response = self.import_data(OrderedDict([
        ("object_type", "Assessment Template"),
        ("Code*", "OBJ-1"),
        ("Audit*", audit.slug),
        ("Default Assignees*", "user@example.com"),
        ("Object Under Assessment", "Control"),
        ("Title", "Object Title"),
        (alias, value),
    ]))
    self._check_csv_response(response, expected_messages)
    obj = all_models.AssessmentTemplate.query.one()
    self.assertEqual(str(obj.issue_tracker[missed_field]),
                     str(audit_value))

  @ddt.data(
      ("component_id", "Component ID", ""),
      ("component_id", "Component ID", "sss"),
      ("hotlist_id", "Hotlist ID", ""),
      ("hotlist_id", "Hotlist ID", "aaa"),
      ("issue_priority", "Priority", ""),
      ("issue_priority", "Priority", "P6"),
      ("issue_severity", "Severity", ""),
      ("issue_severity", "Severity", "aa"),
      ("issue_type", "Issue Type", ""),
      ("issue_type", "Issue Type", "PARABOLA"),
  )
  @ddt.unpack
  def test_assmt_tmpl_default_values_from_default(self,
                                                  missed_field,
                                                  alias,
                                                  value):
    """Test default value was set to Assessment Template {0}"""
    expected_warning = (
        errors.WRONG_VALUE_DEFAULT.format(line=3, column_name=alias)
    )

    expected_messages = {
        "Assessment Template": {
            "row_warnings": {expected_warning},
        }
    }

    with factories.single_commit():
      audit = factories.AuditFactory()
      factories.IssueTrackerIssueFactory(issue_tracked_obj=audit)

    response = self.import_data(OrderedDict([
        ("object_type", "Assessment Template"),
        ("Code*", "OBJ-1"),
        ("Audit*", audit.slug),
        ("Default Assignees*", "user@example.com"),
        ("Object Under Assessment", "Control"),
        ("Title", "Object Title"),
        (alias, value),
    ]))

    self._check_csv_response(response, expected_messages)
    obj = all_models.AssessmentTemplate.query.one()
    self.assertEqual(str(obj.issue_tracker[missed_field]),
                     str(default_values[missed_field]))

  @ddt.data("Fixed", "Fixed and Verified", "Deprecated")
  @mock.patch.object(settings, "ISSUE_TRACKER_ENABLED", True)
  def test_ticket_generation_disallowed_on_create(self, status):
    """Test ticket generation disallowed for Issue in {} status on create"""
    expected_warning = (
        errors.WRONG_TICKET_STATUS.format(
            line=3,
            column_name="Ticket Tracker Integration",
        )
    )
    expected_messages = {
        "Issue": {
            "row_warnings": {expected_warning},
        }
    }
    response = self.import_data(OrderedDict([
        ("object_type", "Issue"),
        ("Code*", "OBJ-1"),
        ("Admin", "user@example.com"),
        ("Title", "Object Title"),
        ("State", status),
        ("Ticket Tracker Integration", "On"),
    ]))
    self._check_csv_response(response, expected_messages)
    obj = all_models.Issue.query.one()
    self.assertFalse(obj.issue_tracker["enabled"])

  @ddt.data("Fixed", "Fixed and Verified", "Deprecated")
  @mock.patch.object(settings, "ISSUE_TRACKER_ENABLED", True)
  def test_ticket_generation_disallowed_on_update(self, status):
    """Test ticket generation disallowed for Issue in {} status on update"""
    with factories.single_commit():
      obj = factories.IssueFactory(status=status)
      factories.IssueTrackerIssueFactory(
          issue_tracked_obj=obj,
          enabled=False,
          issue_id=None,
      )
    expected_warning = (
        errors.WRONG_TICKET_STATUS.format(
            line=3,
            column_name="Ticket Tracker Integration",
        )
    )
    expected_messages = {
        "Issue": {
            "row_warnings": {expected_warning},
        }
    }
    response = self.import_data(OrderedDict([
        ("object_type", "Issue"),
        ("Code*", obj.slug),
        ("Ticket Tracker Integration", "On"),
    ]))
    self._check_csv_response(response, expected_messages)
    obj = all_models.Issue.query.one()
    self.assertFalse(obj.issue_tracker["enabled"])

  @ddt.data("Draft", "Active")
  @mock.patch.object(settings, "ISSUE_TRACKER_ENABLED", True)
  def test_generation_allowed_on_create(self, status):
    """Test ticket generation allowed for Issue in status={0} on create"""
    response = self.import_data(OrderedDict([
        ("object_type", "Issue"),
        ("Code*", "OBJ-1"),
        ("Admin", "user@example.com"),
        ("State", status),
        ("Title", "Object Title"),
        ("Ticket Tracker Integration", "On"),
    ]))
    self._check_csv_response(response, {})
    obj = all_models.Issue.query.one()
    self.assertTrue(obj.issue_tracker["enabled"])
    self.mock_create_issue.assert_called_once()

  @ddt.data("Draft", "Active")
  @mock.patch.object(settings, "ISSUE_TRACKER_ENABLED", True)
  def test_generation_allowed_on_update(self, status):
    """Test ticket generation allowed for Issue in {} status on update"""
    with factories.single_commit():
      obj = factories.IssueFactory(status=status)
      factories.IssueTrackerIssueFactory(
          issue_tracked_obj=obj,
          enabled=False,
          issue_id=None,
      )
    response = self.import_data(OrderedDict([
        ("object_type", "Issue"),
        ("Code*", obj.slug),
        ("Ticket Tracker Integration", "On"),
    ]))
    self._check_csv_response(response, {})
    obj = all_models.Issue.query.one()
    self.assertTrue(obj.issue_tracker["enabled"])
    self.mock_create_issue.assert_called_once()

  @ddt.data(*all_models.Assessment.VALID_STATES)
  @mock.patch.object(settings, "ISSUE_TRACKER_ENABLED", True)
  def test_generation_allowed_for_assmts(self, status):
    """Test ticket generation allowed for Assessment in {} status"""
    with factories.single_commit():
      audit = factories.AuditFactory()
      factories.IssueTrackerIssueFactory(
          issue_tracked_obj=audit,
          enabled=True,
      )
      assmt = factories.AssessmentFactory(status=status, audit=audit)
      person = factories.PersonFactory()
      factories.AccessControlPersonFactory(
          ac_list=assmt.acr_name_acl_map["Verifiers"],
          person=person,
      )
      factories.IssueTrackerIssueFactory(
          issue_tracked_obj=assmt,
          enabled=False,
          issue_id=None,
      )
    response = self.import_data(OrderedDict([
        ("object_type", "Assessment"),
        ("Code*", assmt.slug),
        ("Ticket Tracker Integration", "On"),
    ]))
    self._check_csv_response(response, {})
    assmt = all_models.Assessment.query.one()
    self.assertTrue(assmt.issue_tracker["enabled"])
    self.mock_create_issue.assert_called_once()

  @mock.patch.object(settings, "ISSUE_TRACKER_ENABLED", True)
  def test_assmt_generation_disallowed_wo_audit(self):
    """Test we can't turn integration On for Assessment w/o audit"""
    with factories.single_commit():
      audit = factories.AuditFactory()
      factories.IssueTrackerIssueFactory(
          issue_tracked_obj=audit,
          enabled=False,
          issue_id=None,
      )
    response = self.import_data(OrderedDict([
        ("object_type", "Assessment"),
        ("Code*", ""),
        ("Audit", audit.slug),
        ("Assignees*", "user@example.com"),
        ("Creators", "user@example.com"),
        ("Title", "Object Title"),
        ("Ticket Tracker Integration", "On"),
    ]))
    self._check_csv_response(response, {})
    assmt = all_models.Assessment.query.one()
    self.assertFalse(assmt.issue_tracker["enabled"])

  @ddt.data(
      ("component_id", "Component ID", "", 123),
      ("component_id", "Component ID", "sss", 123),
      ("component_id", "Component ID", None, 123),
      ("hotlist_id", "Hotlist ID", "", 123),
      ("hotlist_id", "Hotlist ID", "aaa", 123),
      ("hotlist_id", "Hotlist ID", None, 123),
      ("issue_priority", "Priority", "", "P4"),
      ("issue_priority", "Priority", "P6", "P0"),
      ("issue_priority", "Priority", None, "P0"),
      ("issue_severity", "Severity", "", "S1"),
      ("issue_severity", "Severity", "aa", "S3"),
      ("issue_severity", "Severity", None, "S3"),
      ("issue_type", "Issue Type", "", "PROCESS"),
      ("issue_type", "Issue Type", "PARABOLA", "PROCESS"),
      ("issue_type", "Issue Type", None, "PROCESS"),
      ("enabled", "Ticket Tracker Integration", "", True),
      ("enabled", "Ticket Tracker Integration", "aa", True),
      ("enabled", "Ticket Tracker Integration", None, True),
      ("enabled", "Ticket Tracker Integration", "", False),
      ("enabled", "Ticket Tracker Integration", "aa", False),
      ("enabled", "Ticket Tracker Integration", None, False),
  )
  @ddt.unpack
  @mock.patch.object(settings, "ISSUE_TRACKER_ENABLED", True)
  def test_asmt_default_values_from_tmpl(self, field, alias, value,
                                         tmpl_value):
    """Test set tmpl.{0}={3!r} if csv.{1!r}={2!r} and audit/app integr on"""

    with factories.single_commit():
      audit = factories.AuditFactory()
      factories.IssueTrackerIssueFactory(
          issue_tracked_obj=audit, enabled=True)
      tmpl = factories.AssessmentTemplateFactory(audit=audit)
      factories.IssueTrackerIssueFactory(
          issue_tracked_obj=tmpl, **{field: tmpl_value})

    fields = OrderedDict([
        ("object_type", "Assessment"),
        ("Code*", "OBJ-1"),
        ("Audit*", audit.slug),
        ("Assignees*", "user@example.com"),
        ("Creators", "user@example.com"),
        ("Template", tmpl.slug),
        ("Title", "Object Title"),
    ])
    if value is not None:
      fields[alias] = value
    response = self.import_data(fields)

    if value is not None:
      # ensure that warning is returned
      expected_warning = (
          errors.WRONG_VALUE_DEFAULT.format(line=3, column_name=alias)
      )
      expected_messages = {"Assessment": {"row_warnings": {expected_warning}}}
      self._check_csv_response(response, expected_messages)

    obj = all_models.Assessment.query.one()
    self.assertEqual(str(obj.issue_tracker[field]),
                     str(tmpl_value))
    self.mock_create_issue.assert_not_called()
