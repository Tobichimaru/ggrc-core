# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>

"""Test suite for DELETE requests."""
import mock
from sqlalchemy import func

from integration.ggrc import TestCase
from integration.ggrc.query_helper import WithQueryApi
from integration.ggrc.models import factories
from integration.ggrc.api_helper import Api

from ggrc import db, views
from ggrc.models import all_models


class TestDelete(TestCase, WithQueryApi):
  """Test objects deletion."""

  def setUp(self):
    super(TestDelete, self).setUp()
    self.client.get("/login")
    self.api = Api()

  def test_delete(self):
    """Deletion is synchronous and triggers compute_attributes."""
    control = factories.ControlFactory()

    with mock.patch(
        "ggrc.models.background_task.create_task",
    ) as create_task:
      result = self.api.delete(control)
      controls = db.session.query(all_models.Control).all()
      event_id = db.session.query(func.max(all_models.Event.id)).first()[0]

      self.assert200(result)
      self.assertEqual(len(controls), 0)
      self.assertEqual(db.session.query(all_models.BackgroundTask).count(), 0)
      create_task.assert_called_once_with(
          name="compute_attributes",
          url="/_background_tasks/compute_attributes",
          parameters={"revision_ids": None, "event_id": event_id},
          method="POST",
          queued_callback=views.compute_attributes
      )

  def test_delete_http400(self):
    """Deletion returns HTTP400 if BadRequest is raised."""
    with factories.single_commit():
      audit = factories.AuditFactory()
      factories.AssessmentFactory(audit=audit)

    result = self.api.delete(audit)

    self.assert400(result)
    self.assertEqual(result.json["message"],
                     "This request will break a mandatory relationship from "
                     "assessments to audits.")
