# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>

"""Tests if error handling is done correctly"""

import ddt
from freezegun import freeze_time

from ggrc.models import all_models
from ggrc.utils import detached_objects

from integration.ggrc import TestCase
from integration.ggrc.api_helper import Api
from integration.ggrc.models import factories


@ddt.ddt
class TestDetachedObjects(TestCase):
  """Test cases for detached objects."""

  def setUp(self):
    super(TestDetachedObjects, self).setUp()
    self.client.get("/login")
    self.api = Api()

  @ddt.data(factories.AssessmentFactory,
            factories.AssessmentFactory,
            factories.ProcessFactory,
            factories.ProgramFactory,
            factories.AuditFactory,
            factories.ControlFactory,
            factories.DocumentFactory,
            factories.SystemFactory,
            factories.IssueFactory,
            factories.ClauseFactory)
  def test_comments_delete(self, object_factory):
    """Test if assessment deleted along with comments."""
    with freeze_time("2018-07-01"):
      obj = object_factory()
      comments = [factories.CommentFactory(), factories.CommentFactory()]
      comment_ids = [comment.id for comment in comments]
      relationships = [
          factories.RelationshipFactory(source=comments[0], destination=obj),
          factories.RelationshipFactory(source=obj, destination=comments[1])
      ]
      rel_ids = [rel.id for rel in relationships]

      result = self.api.delete(obj)
      self.assertEqual(result.status_code, 200)

      for rel_id in rel_ids:
        relationship = all_models.Relationship.query.get(rel_id)
        self.assertEqual(relationship, None)

    with freeze_time("2018-07-02"):
      detached_objects.delete_detached_comments()

      for comment_id in comment_ids:
        comment = all_models.Comment.query.get(comment_id)
        self.assertEqual(comment, None)

        delete_revision = all_models.Revision.query.filter(
            all_models.Revision.resource_id == comment_id,
            all_models.Revision.resource_type == "Comment",
            all_models.Revision.action == "deleted"
        ).first()
        self.assertNotEqual(delete_revision, None)
