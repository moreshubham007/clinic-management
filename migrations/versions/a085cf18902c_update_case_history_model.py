"""Update case history model

Revision ID: a085cf18902c
Revises: c2913c704657
Create Date: 2025-01-25 11:41:10.095908

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'a085cf18902c'
down_revision = 'c2913c704657'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('cases')
    op.drop_table('case_transfer_logs')
    with op.batch_alter_table('case', schema=None) as batch_op:
        batch_op.drop_column('closing_notes')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('case', schema=None) as batch_op:
        batch_op.add_column(sa.Column('closing_notes', mysql.TEXT(), nullable=True))

    op.create_table('case_transfer_logs',
    sa.Column('id', mysql.INTEGER(display_width=11), autoincrement=True, nullable=False),
    sa.Column('case_id', mysql.INTEGER(display_width=11), autoincrement=False, nullable=False),
    sa.Column('from_doctor_id', mysql.INTEGER(display_width=11), autoincrement=False, nullable=False),
    sa.Column('to_doctor_id', mysql.INTEGER(display_width=11), autoincrement=False, nullable=False),
    sa.Column('notes', mysql.TEXT(), nullable=True),
    sa.Column('created_at', mysql.DATETIME(), nullable=True),
    sa.ForeignKeyConstraint(['case_id'], ['cases.id'], name='case_transfer_logs_ibfk_1'),
    sa.ForeignKeyConstraint(['from_doctor_id'], ['doctor.id'], name='case_transfer_logs_ibfk_2'),
    sa.ForeignKeyConstraint(['to_doctor_id'], ['doctor.id'], name='case_transfer_logs_ibfk_3'),
    sa.PrimaryKeyConstraint('id'),
    mysql_collate='utf8mb4_uca1400_ai_ci',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    op.create_table('cases',
    sa.Column('id', mysql.INTEGER(display_width=11), autoincrement=True, nullable=False),
    sa.Column('patient_id', mysql.INTEGER(display_width=11), autoincrement=False, nullable=False),
    sa.Column('doctor_id', mysql.INTEGER(display_width=11), autoincrement=False, nullable=False),
    sa.Column('diagnosis', mysql.TEXT(), nullable=True),
    sa.Column('treatment', mysql.TEXT(), nullable=True),
    sa.Column('created_at', mysql.DATETIME(), nullable=True),
    sa.Column('updated_at', mysql.DATETIME(), nullable=True),
    sa.Column('show_to_patient', mysql.TINYINT(display_width=1), autoincrement=False, nullable=True),
    sa.Column('status', mysql.VARCHAR(length=20), nullable=True),
    sa.Column('closing_notes', mysql.TEXT(), nullable=True),
    sa.ForeignKeyConstraint(['doctor_id'], ['doctor.id'], name='cases_ibfk_1'),
    sa.ForeignKeyConstraint(['patient_id'], ['user.id'], name='cases_ibfk_2'),
    sa.PrimaryKeyConstraint('id'),
    mysql_collate='utf8mb4_uca1400_ai_ci',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    # ### end Alembic commands ###
