"""Add signed institutional aggregate reporting and independent reviews.

Revision ID: 0002_signed_reports
Revises: 0001_initial
"""
from alembic import op
from sqlalchemy import inspect
from cmpe.db import SignedReport, ReportReview
revision="0002_signed_reports"
down_revision="0001_initial"
branch_labels=None
depends_on=None

def upgrade():
    bind=op.get_bind()
    existing=set(inspect(bind).get_table_names())
    for table in (SignedReport.__table__,ReportReview.__table__):
        if table.name not in existing:table.create(bind=bind,checkfirst=True)
        else:
            columns={c["name"] for c in inspect(bind).get_columns(table.name)}
            if not {c.name for c in table.columns}.issubset(columns):
                raise RuntimeError("Existing signed report schema incompatible: "+table.name)

def downgrade():
    raise RuntimeError("Data-preserving policy forbids silent downgrade of signed evidence")
