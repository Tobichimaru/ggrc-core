# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>

""" This module contains methods for cron jobs
    connected to detached objects deletion."""

from ggrc import db
from ggrc.models import all_models
from ggrc.utils import benchmark
from ggrc.utils.log_event import log_event


def delete_detached_comments():
  """ Deletes Comments that are not referenced to any object."""
  with benchmark("Contributed cron job delete_detached_comments"):
    with benchmark("Collect detached comments"):
      destinations = all_models.Relationship.query.with_entities(
          all_models.Relationship.destination_id
      ).filter(
          all_models.Relationship.source_type == "Comment",
      )
      sources = all_models.Relationship.query.with_entities(
          all_models.Relationship.destination_id
      ).filter(
          all_models.Relationship.destination_type == "Comment",
      )
      comments = all_models.Comment.query.filter(
          all_models.Comment.id.notin_(
              destinations.union(sources)
          )
      ).all()

    with benchmark("Delete detached comments"):
      for comment in comments:
        db.session.delete(comment)

    with benchmark("Log event"):
      log_event(db.session, None)
      db.session.commit()
