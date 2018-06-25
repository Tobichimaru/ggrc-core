# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>

"""Test acl role propagation on assessments."""

from threading import Thread

from ggrc import db
from ggrc_workflows.models import all_models
from integration.ggrc import TestCase
from integration.ggrc.models import factories
from integration.ggrc.generator import ObjectGenerator


class TestAssessmentAclPropagation(TestCase):
  """Test acl role propagation on assessments."""

  def setUp(self):
    super(TestAssessmentAclPropagation, self).setUp()
    with factories.single_commit():
      self.people_ids = [
          factories.PersonFactory(
              name="user {}".format(i),
              email="user{}@example.com".format(i),
          ).id
          for i in range(10)
      ]
    self.generator = ObjectGenerator()

    acr = all_models.AccessControlRole
    self.acr_name_map = dict(db.session.query(
        acr.name,
        acr.id,
    ).filter(
        acr.object_type == all_models.Assessment.__name__,
    ))

  def test_async_acr_propagation(self):
    """Test asynchronous acl propagations."""
    number_of_threads = 10

    def add_coment(assessment, ca_def_id, ca_val_id):
      """Change workflow assignees."""
      self.generator.api.put(assessment, {
          "custom_attribute_values": [{
              "id": ca_val_id,
              "custom_attribute_id": ca_def_id,
              "attribute_value": "yes",
              "type": "CustomAttributeValue",
          }],
          "actions": {"add_related": [{
              "id": None,
              "type": "Comment",
              "description": "comment_{}_{}".format(ca_def_id, ca_val_id),
              "custom_attribute_definition_id": ca_def_id,
          }]}
      })

    assessment = factories.AssessmentFactory()
    threads = []

    for i in range(number_of_threads):
      ca_def_title = "def_{}".format(i)
      with factories.single_commit():
        ca_def = factories.CustomAttributeDefinitionFactory(
            title=ca_def_title,
            definition_type="assessment",
            definition_id=assessment.id,
            attribute_type="Dropdown",
            multi_choice_options="no,yes",
            multi_choice_mandatory="1,2"
        )
        ca_val = factories.CustomAttributeValueFactory(
            custom_attribute=ca_def,
            attributable=assessment,
            attribute_value="no"
        )
      threads.append(Thread(target=add_coment,
                            args=(assessment, ca_def.id, ca_val.id)))

    for thread in threads:
      thread.start()
    for thread in threads:
      thread.join()

    acl = all_models.AccessControlList

    assessment_acl_count = acl.query.filter(
        acl.object_type == all_models.Assessment.__name__
    ).count()

    propagated_acl_count = acl.query.filter(
        acl.parent_id.isnot(None)
    ).count()
    number_of_objects = 9

    self.assertEqual(
        assessment_acl_count * number_of_objects,
        propagated_acl_count
    )
