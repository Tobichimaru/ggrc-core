# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>

"""
Make GCA not mandatory

Create Date: 2018-07-20 10:54:41.750164
"""
# disable Invalid constant name pylint warning for mandatory Alembic variables.
# pylint: disable=invalid-name

from alembic import op

# revision identifiers, used by Alembic.
revision = 'd01e4c8d8234'
down_revision = '0e385718442a'


def upgrade():
  """Upgrade database schema and/or data, creating a new revision."""
  sql = """
      UPDATE custom_attribute_definitions as cad
         SET cad.mandatory = 0
       WHERE cad.definition_id is NULL AND cad.mandatory = 1
      """
  op.execute(sql)


def downgrade():
  """Downgrade database schema and/or data back to the previous revision."""
  pass
