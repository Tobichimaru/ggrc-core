# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>

"""
Remove custom attributes with invalid definitions

Create Date: 2019-01-14 13:21:22.259581
"""
# disable Invalid constant name pylint warning for mandatory Alembic variables.
# pylint: disable=invalid-name

from alembic import op

# revision identifiers, used by Alembic.
revision = '7f582a98f108'
down_revision = 'dd2a3a987de5'


def upgrade():
  """Upgrade database schema and/or data, creating a new revision."""
  delete_values = (
      "DELETE cav "
      "FROM custom_attribute_values AS cav "
      "JOIN custom_attribute_definitions AS cad "
      "ON cav.custom_attribute_id = cad.id "
      "WHERE cad.definition_type = ''"
  )
  op.execute(delete_values)
  delete_definitions = (
      "DELETE FROM custom_attribute_definitions "
      "WHERE definition_type = ''"
  )
  op.execute(delete_definitions)


def downgrade():
  """Downgrade database schema and/or data back to the previous revision."""
