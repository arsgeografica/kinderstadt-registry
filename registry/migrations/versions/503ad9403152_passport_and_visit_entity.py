"""Passport and Visit entity

Revision ID: 503ad9403152
Revises: None
Create Date: 2015-06-14 21:36:29.185951

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '503ad9403152'
down_revision = None


def upgrade():
    op.create_table(
        'passport',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('pass_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=128), nullable=False),
        sa.Column('surname', sa.String(length=128), nullable=False),
        sa.Column('deactivated', sa.Boolean(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('pass_id')
    )

    op.create_table(
        'visit',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('passport_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('check_in', sa.DateTime(), nullable=True),
        sa.Column('check_out', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['passport_id'], ['passport.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_visit_check_in'), 'visit', ['check_in'],
                    unique=False)
    op.create_index(op.f('ix_visit_check_out'), 'visit', ['check_out'],
                    unique=False)
    op.create_index(op.f('ix_visit_passport_id'), 'visit', ['passport_id'],
                    unique=False)


def downgrade():
    op.drop_index(op.f('ix_visit_passport_id'), table_name='visit')
    op.drop_index(op.f('ix_visit_check_out'), table_name='visit')
    op.drop_index(op.f('ix_visit_check_in'), table_name='visit')
    op.drop_table('visit')
    op.drop_table('passport')
