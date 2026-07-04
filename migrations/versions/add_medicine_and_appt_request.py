"""Add medicine_order and appointment_request tables

Revision ID: add_medicine_and_appt_request
Revises: ef6a9dbf7d9a
Create Date: 2026-07-03 23:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = 'add_medicine_and_appt_request'
down_revision = 'ef6a9dbf7d9a'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('medicine_order',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('order_number', sa.String(length=20), nullable=False),
        sa.Column('mobile_number', sa.String(length=15), nullable=False),
        sa.Column('patient_id', sa.Integer(), nullable=True),
        sa.Column('patient_number', sa.String(length=11), nullable=True),
        sa.Column('duration_days', sa.Integer(), nullable=False),
        sa.Column('delivery_type', sa.String(length=20), nullable=False),
        sa.Column('pickup_date', sa.Date(), nullable=True),
        sa.Column('delivery_address', sa.Text(), nullable=True),
        sa.Column('additional_notes', sa.Text(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['patient_id'], ['user.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('order_number')
    )

    op.create_table('appointment_request',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('request_number', sa.String(length=20), nullable=False),
        sa.Column('patient_type', sa.String(length=20), nullable=False),
        sa.Column('mobile_number', sa.String(length=15), nullable=False),
        sa.Column('preferred_date', sa.Date(), nullable=True),
        sa.Column('preferred_time', sa.String(length=10), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('patient_name', sa.String(length=100), nullable=True),
        sa.Column('patient_email', sa.String(length=120), nullable=True),
        sa.Column('patient_gender', sa.String(length=10), nullable=True),
        sa.Column('patient_id', sa.Integer(), nullable=True),
        sa.Column('patient_number', sa.String(length=11), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['patient_id'], ['user.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('request_number')
    )


def downgrade():
    op.drop_table('appointment_request')
    op.drop_table('medicine_order')
