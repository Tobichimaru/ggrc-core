# Copyright (C) 2019 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>

"""
Migrate html to markdown for controls

Create Date: 2019-02-27 08:09:37.653576
"""
# disable Invalid constant name pylint warning for mandatory Alembic variables.
# pylint: disable=invalid-name

import datetime

import sqlalchemy as sa

from alembic import op

from ggrc.migrations import utils
from ggrc.migrations.utils import html_markdown_parser

# revision identifiers, used by Alembic.
revision = '7769fdc16fef'
down_revision = '3b6acfd18e5c'


REGEX_HTML = r' "(<[a-zA-Z]+>)+|(<\/[a-zA-Z]+>)+"'


def parse_html(value):
  """Parse html to markdown."""
  parser = html_markdown_parser.HTML2MarkdownParser()
  parser.feed(value)
  return parser.get_data()


def update_comments(connection):
  """Parse external comments from html to markdown."""
  comments_data = connection.execute("""
      select id, description
      from external_comments
      where description REGEXP
  """ + REGEX_HTML).fetchall()
  comments_ids = [c_id for c_id, _ in comments_data]
  comments_table = sa.sql.table(
      'external_comments',
      sa.Column('id', sa.Integer()),
      sa.Column('description', sa.Text, nullable=True),
      sa.Column('updated_at', sa.DateTime, nullable=False),
  )
  for comment_id, description in comments_data:
    op.execute(comments_table.update().values(
        description=parse_html(description),
        updated_at=datetime.datetime.utcnow(),
    ).where(comments_table.c.id == comment_id))
  utils.add_to_objects_without_revisions_bulk(
      connection, comments_ids, "ExternalComment", "modified",
  )


def update_control_cavs(connection):
  """Parse cavs from html to markdown."""
  cavs_data = connection.execute("""
      select cav.id, cav.attribute_value, cav.attributable_id
      from custom_attribute_values cav
      join custom_attribute_definitions cad
        on cad.id = cav.custom_attribute_id
      where cad.definition_type = "control"
        and attribute_value REGEXP
  """ + REGEX_HTML).fetchall()
  controls_ids = {data[2] for data in cavs_data}
  cavs_table = sa.sql.table(
      'custom_attribute_values',
      sa.Column('id', sa.Integer()),
      sa.Column('attribute_value', sa.Text, nullable=False),
      sa.Column('updated_at', sa.DateTime, nullable=False),
  )
  for cav_id, attribute_value, _ in cavs_data:
    op.execute(cavs_table.update().values(
        attribute_value=parse_html(attribute_value),
        updated_at=datetime.datetime.utcnow(),
    ).where(cavs_table.c.id == cav_id))

  return controls_ids


def update_control_attr(connection):
  """Parse Control attributes from html to markdown."""
  controls_data = connection.execute(
      u"SELECT id, title, description, test_plan, notes"
      u" FROM controls"
      u" WHERE title REGEXP " + REGEX_HTML +
      u" OR description REGEXP " + REGEX_HTML +
      u" OR test_plan REGEXP " + REGEX_HTML +
      u" OR notes REGEXP " + REGEX_HTML
  ).fetchall()
  controls_ids = {data[0] for data in controls_data}

  controls_table = sa.sql.table(
      'controls',
      sa.Column('id', sa.Integer()),
      sa.Column('title', sa.String(250), nullable=False),
      sa.Column('description', sa.Text, nullable=False),
      sa.Column('test_plan', sa.Text, nullable=False),
      sa.Column('notes', sa.Text, nullable=False),
      sa.Column('updated_at', sa.DateTime, nullable=False),
  )
  for c_id, title, description, test_plan, notes in controls_data:
    op.execute(controls_table.update().values(
        title=parse_html(title),
        description=parse_html(description),
        test_plan=parse_html(test_plan),
        notes=parse_html(notes),
        updated_at=datetime.datetime.utcnow(),
    ).where(controls_table.c.id == c_id))
  return controls_ids


def upgrade():
  """Upgrade database schema and/or data, creating a new revision."""
  connection = op.get_bind()
  update_comments(connection)
  controls_ids = update_control_cavs(connection)
  controls_ids.union(update_control_attr(connection))
  if controls_ids:
    utils.add_to_objects_without_revisions_bulk(
        connection, controls_ids, "Control", "modified",
    )


def downgrade():
  """Downgrade database schema and/or data back to the previous revision."""
