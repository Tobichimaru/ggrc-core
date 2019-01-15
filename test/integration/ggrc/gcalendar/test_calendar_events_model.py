# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>

"""Tests calendar event model."""

from datetime import date

from ggrc import utils
from integration.ggrc.gcalendar import BaseCalendarEventTest


# pylint: disable=protected-access
class TestCalendarEventModel(BaseCalendarEventTest):
  """Test calendar event model."""

  def setUp(self):
    """Set up test with mocks."""
    super(TestCalendarEventModel, self).setUp()
    self.client.get("/login")

  def test_stub_creation(self):
    """Test creation of event."""
    _, _, event = self.setup_person_task_event(date(2015, 1, 5))
    self.assertEquals(utils.create_stub(event), {
        'context_id': None,
        'href': '/api/calendar_events/{}'.format(event.id),
        'id': event.id,
        'type': 'CalendarEvent'
    })
