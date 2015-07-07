"""Add passport fields

Revision ID: 8a00d265ee2
Revises: 3ac4d0af1d85
Create Date: 2015-07-07 23:06:14.737224

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8a00d265ee2'
down_revision = '3ac4d0af1d85'


def upgrade():
    op.add_column(
        'passport', sa.Column('address', sa.Text(), nullable=False))
    op.add_column(
        'passport', sa.Column('email', sa.String(length=128), nullable=True))
    op.add_column(
        'passport', sa.Column('notes', sa.Text(), nullable=True))
    op.add_column(
        'passport', sa.Column('phone', sa.String(length=128), nullable=False))


def downgrade():
    op.drop_column('passport', 'phone')
    op.drop_column('passport', 'notes')
    op.drop_column('passport', 'email')
    op.drop_column('passport', 'address')
