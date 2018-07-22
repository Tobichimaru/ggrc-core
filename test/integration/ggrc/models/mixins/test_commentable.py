# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>

"""Integration tests for Commentable mixin."""

import ddt

from ggrc.models import all_models

from integration.ggrc import TestCase
from integration.ggrc.api_helper import Api
from integration.ggrc.models import factories


@ddt.ddt
class TestCommentableMixin(TestCase):
  """Test cases for Commentable mixin."""

  def setUp(self):
    super(TestCommentableMixin, self).setUp()
    self.client.get("/login")
    self.api = Api()

  def test_asmnt_comments(self):
    """Test if assessment has proper comments."""
    # This test check bug which is reproduced when ids of Audit, Assessment
    # and Comment are the same
    with factories.single_commit():
      audit = factories.AuditFactory()
      for i in range(3):
        assessment = factories.AssessmentFactory(id=audit.id + i, audit=audit)
        factories.RelationshipFactory(source=assessment, destination=audit)
        comment = factories.CommentFactory(
            id=audit.id + i,
            description="test{0}".format(i)
        )
        factories.RelationshipFactory(source=assessment, destination=comment)

    asmnt_comments = all_models.Assessment.query.first().comments

    self.assertEquals(1, len(asmnt_comments))
    self.assertEquals("test0", "".join(c.description for c in asmnt_comments))

  @ddt.data([factories.AssessmentFactory, True],
            [factories.AssessmentFactory, False],
            [factories.ProcessFactory, False],
            [factories.ProgramFactory, False],
            [factories.AuditFactory, True],
            [factories.ControlFactory, False],
            [factories.DocumentFactory, True],
            [factories.SystemFactory, False],
            [factories.IssueFactory, False],
            [factories.ClauseFactory, False])
  @ddt.unpack
  def test_asmnt_comments_delete(self, object_factory, inverse_rel):
    """Test if assessment deleted along with comments."""
    obj = object_factory()
    comment = factories.CommentFactory()
    comment_id = comment.id
    if inverse_rel:
      relationship = factories.RelationshipFactory(source=comment,
                                                   destination=obj)
    else:
      relationship = factories.RelationshipFactory(source=obj,
                                                   destination=comment)
    relationship_id = relationship.id

    result = self.api.delete(obj)
    self.assertEqual(result.status_code, 200)

    comment = all_models.Comment.query.get(comment_id)
    self.assertEqual(comment, None)

    relationship = all_models.Relationship.query.get(relationship_id)
    self.assertEqual(relationship, None)

    delete_revision = all_models.Revision.query.filter(
        all_models.Revision.resource_id == comment_id,
        all_models.Revision.resource_type == "Comment",
        all_models.Revision.action == "deleted"
    ).first()
    self.assertNotEqual(delete_revision, None)
