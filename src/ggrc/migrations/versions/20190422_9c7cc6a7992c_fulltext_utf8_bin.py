# Copyright (C) 2019 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>

"""
fulltext utf8_bin

Create Date: 2019-04-22 06:27:25.663821
"""

# disable Invalid constant name pylint warning for mandatory Alembic variables.
# pylint: disable=invalid-name

from alembic import op

# revision identifiers, used by Alembic.
revision = '9c7cc6a7992c'
down_revision = 'adf7bdb8996e'


def upgrade():
  """Upgrade database schema and/or data, creating a new revision."""
  op.execute(
      "ALTER TABLE fulltext_record_properties "
      "CONVERT TO CHARACTER SET utf8 COLLATE utf8_bin"
  )


def downgrade():
  """Downgrade database schema and/or data back to the previous revision."""
  raise NotImplementedError("Downgrade is not supported")
