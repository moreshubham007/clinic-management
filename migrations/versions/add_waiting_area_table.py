"""Add waiting area table

Revision ID: add_waiting_area_table
Revises: update_case_transfer_fields
Create Date: 2025-01-14 13:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime

# revision identifiers, used by Alembic.
revision = 'add_waiting_area_table'
down_revision = 'update_case_transfer_fields'
branch_labels = None
depends_on = None

def upgrade():
    # Create waiting_area table
    op.create_table('waiting_area',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('appointment_id', sa.Integer(), nullable=False),
        sa.Column('patient_id', sa.Integer(), nullable=False),
        sa.Column('doctor_id', sa.Integer(), nullable=False),
        sa.Column('check_in_time', sa.DateTime(), nullable=True),
        sa.Column('expected_appointment_time', sa.DateTime(), nullable=False),
        sa.Column('actual_start_time', sa.DateTime(), nullable=True),
        sa.Column('completion_time', sa.DateTime(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=True),
        sa.Column('priority', sa.String(length=10), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('doctor_notes', sa.Text(), nullable=True),
        sa.Column('wait_time_minutes', sa.Integer(), nullable=True),
        sa.Column('added_by_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['added_by_id'], ['user.id'], ),
        sa.ForeignKeyConstraint(['appointment_id'], ['appointment.id'], ),
        sa.ForeignKeyConstraint(['doctor_id'], ['doctor.id'], ),
        sa.ForeignKeyConstraint(['patient_id'], ['user.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for better performance
    op.create_index(op.f('ix_waiting_area_check_in_time'), 'waiting_area', ['check_in_time'], unique=False)
    op.create_index(op.f('ix_waiting_area_status'), 'waiting_area', ['status'], unique=False)
    op.create_index(op.f('ix_waiting_area_doctor_id'), 'waiting_area', ['doctor_id'], unique=False)

def downgrade():
    # Drop indexes
    op.drop_index(op.f('ix_waiting_area_doctor_id'), table_name='waiting_area')
    op.drop_index(op.f('ix_waiting_area_status'), table_name='waiting_area')
    op.drop_index(op.f('ix_waiting_area_check_in_time'), table_name='waiting_area')
    
    # Drop table
    op.drop_table('waiting_area') 