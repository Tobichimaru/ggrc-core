# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>

"""
Make Calendar contextable

Create Date: 2019-01-15 09:16:15.288644
"""
# disable Invalid constant name pylint warning for mandatory Alembic variables.
# pylint: disable=invalid-name

import sqlalchemy as sa

from alembic import op


# revision identifiers, used by Alembic.
revision = 'b2ee3f36eccf'
down_revision = '44f601715634'


def upgrade():
  """Upgrade database schema and/or data, creating a new revision."""
  op.add_column(
      'calendar_events',
      sa.Column('context_id', sa.Integer(), nullable=True),
  )
  op.create_foreign_key('fk_calendar_events_contexts',
                        'calendar_events', 'contexts',
                        ['context_id'], ['id'])
  op.create_index('ix_calendar_events_contexts', 'calendar_events',
                  ['context_id'], unique=False)


def downgrade():
  """Downgrade database schema and/or data back to the previous revision."""
  op.drop_constraint('fk_calendar_events_contexts', 'calendar_events',
                     type_='foreignkey')
  op.drop_index('ix_calendar_events_contexts', table_name='calendar_events')
  op.drop_column('calendar_events', 'context_id')
