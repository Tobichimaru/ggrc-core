# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>

"""A module with Comment object creation hooks"""

from ggrc import db
from ggrc import login
from ggrc.models import all_models
from ggrc.access_control import role
from ggrc.services import signals
from ggrc.utils.log_event import log_event
from blinker import ANY


def init_hook():
  """Initialize all hooks"""
  # pylint: disable=unused-variable
  @signals.Restful.collection_posted.connect_via(all_models.Comment)
  def handle_comment_post(mapper, objects, **kwargs):
    """Save information on which user created the Comment object.

    Comments have their users set in a hook, because we must ensure that it is
    always set to the current user, and that is why the info is not sent from
    the front-end through access_control_list property.
    """
    # pylint: disable=unused-argument
    comment_roles = role.get_ac_roles_for(all_models.Comment.__name__)
    comment_admin = comment_roles["Admin"]
    user = login.get_current_user()
    for comment in objects:
      all_models.AccessControlList(
          ac_role=comment_admin,
          person=user,
          object=comment,
      )

  @signals.Restful.model_deleted.connect_via(sender=ANY)
  def handle_del_comment_mapping(sender, obj=None, **kwargs):
    """Handle delete of commentable objects. """
    # pylint: disable=unused-argument
    if not getattr(obj, "related_destinations", None):
      return
    user = login.get_current_user()
    for rel in obj.related_destinations:
      comment = None
      if rel.source_type == "Comment":
        comment = rel.source
      elif rel.destination_type == "Comment":
        comment = rel.destination
      if comment:
        db.session.delete(comment)
        log_event(db.session, comment, flush=False, current_user_id=user.id)
