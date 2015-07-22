"""Passport data changes

Revision ID: 23dcbdfd33b5
Revises: 8a00d265ee2
Create Date: 2015-07-13 21:58:26.843809

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '23dcbdfd33b5'
down_revision = '8a00d265ee2'


def upgrade():
    op.add_column('passport', sa.Column('age', sa.Integer(), nullable=False))


def downgrade():
    op.drop_column('passport', 'age')
