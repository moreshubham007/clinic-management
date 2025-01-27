"""Merge multiple heads

Revision ID: 1da1d476518e
Revises: 0b35830e0d7a, add_patient_to_case_transfer
Create Date: 2025-01-25 21:25:14.273776

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1da1d476518e'
down_revision = ('0b35830e0d7a', 'add_patient_to_case_transfer')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
