# Copyright (C) 2019 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>

"""Tests sync of calendar events."""

from datetime import date
from freezegun import freeze_time
import mock

from ggrc.gcalendar import calendar_event_sync
from integration.ggrc.models import factories
from integration.ggrc.gcalendar import BaseCalendarEventTest


# pylint: disable=protected-access
class TestCalendarEventSync(BaseCalendarEventTest):
  """Test calendar event sync."""

  def setUp(self):
    """Set up test with mocks."""
    super(TestCalendarEventSync, self).setUp()
    self.client.get("/login")
    with mock.patch("ggrc.gcalendar.calendar_api_service"
                    ".CalendarApiService.calendar_auth"):
      self.sync = calendar_event_sync.CalendarEventsSync()

  @mock.patch("ggrc.gcalendar.calendar_api_service"
              ".CalendarApiService.create_event",
              return_value={
                  "id": "external_event_id"
              })
  def test_create_event(self, create_event_mock):
    """Test creation of event."""
    person, _, event = self.setup_person_task_event(date(2015, 1, 15))
    with freeze_time("2015-01-1 12:00:00"):
      self.sync._create_event(event)
    create_event_mock.assert_called_with(
        calendar_id="primary",
        summary=event.title,
        description=event.description,
        start="2015-01-15",
        end="2015-01-16",
        timezone="UTC",
        attendees=[person.email],
        send_notifications=False
    )
    self.assertEquals(event.external_event_id, "external_event_id")
    self.assertEquals(event.last_synced_at.date(), date(2015, 1, 1))

  @mock.patch("ggrc.gcalendar.calendar_api_service"
              ".CalendarApiService.get_event",
              return_value={
                  "description": "old description",
                  "summary": "summary",
                  "eventId": "eventId",
              })
  @mock.patch("ggrc.gcalendar.calendar_api_service"
              ".CalendarApiService.update_event")
  def test_update_event(self, update_event_mock, get_event_mock):
    """Test update of event."""
    with factories.single_commit():
      person = factories.PersonFactory()
      event = factories.CalendarEventFactory(
          due_date=date(2015, 1, 15),
          attendee_id=person.id,
          description="new description",
          title="summary",
          external_event_id="eventId"
      )
    with freeze_time("2015-01-1 12:00:00"):
      self.sync._update_event(event)
    get_event_mock.assert_called_with(
        calendar_id="primary",
        event_id="eventId",
    )
    update_event_mock.assert_called_with(
        event_id="eventId",
        calendar_id="primary",
        description="new description",
        summary="summary",
        start="2015-01-15",
        end="2015-01-16",
        timezone="UTC",
        attendees=[person.email],
    )
    self.assertEquals(event.last_synced_at.date(), date(2015, 1, 1))

  @mock.patch("ggrc.gcalendar.calendar_api_service"
              ".CalendarApiService.delete_event")
  def test_delete_not_synced_event(self, delete_event_mock):
    """Test delete of unsynced event."""
    with factories.single_commit():
      person = factories.PersonFactory()
      event = factories.CalendarEventFactory(
          due_date=date(2015, 1, 15),
          attendee_id=person.id,
          description="description",
          title="summary"
      )
    with freeze_time("2015-01-1 12:00:00"):
      self.sync.sync_cycle_tasks_events()
    db_event = self.get_event(person.id, event.due_date)
    self.assertIsNone(db_event)
    self.assertEqual(delete_event_mock.call_count, 0)

  @mock.patch("ggrc.gcalendar.calendar_api_service"
              ".CalendarApiService.create_event",
              side_effect=Exception("test"))
  def test_fail_to_sync_event(self, create_event_mock):
    """Test that sync job tried to sync the second event after a failure."""
    self.setup_person_task_event(date(2015, 1, 5))
    self.setup_person_task_event(date(2015, 1, 6))
    with freeze_time("2015-01-1 12:00:00"):
      self.sync.sync_cycle_tasks_events()
    self.assertEqual(create_event_mock.call_count, 2)
