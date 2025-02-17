"""Add state city pincode to User model

Revision ID: 694c2ddb6092
Revises: d6ef9f69b376
Create Date: 2025-01-26 01:17:02.393206

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '694c2ddb6092'
down_revision = 'd6ef9f69b376'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('state', sa.String(length=50), nullable=True))
        batch_op.add_column(sa.Column('city', sa.String(length=50), nullable=True))
        batch_op.add_column(sa.Column('pin_code', sa.String(length=6), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_column('pin_code')
        batch_op.drop_column('city')
        batch_op.drop_column('state')

    # ### end Alembic commands ###
