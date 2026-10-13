"""Bootstrap metadata schema. Never delete data on downgrade.

Revision ID: 0001_initial
Revises:
"""
from alembic import op
from sqlalchemy import inspect
from cmpe.db import Base
revision="0001_initial"
down_revision=None
branch_labels=None
depends_on=None

def upgrade():
    bind=op.get_bind()
    existing=set(inspect(bind).get_table_names())
    for table in Base.metadata.sorted_tables:
        if table.name in existing:
            actual={col["name"] for col in inspect(bind).get_columns(table.name)}
            wanted={col.name for col in table.columns}
            if not wanted.issubset(actual):
                raise RuntimeError(f"Incompatible legacy table {table.name}: missing {wanted-actual}")
        else:
            table.create(bind=bind,checkfirst=True)

def downgrade():
    raise RuntimeError("Refusing automatic deletion of economic planning data; restore a verified backup to revert")
