"""Add flags storage

Revision ID: 27927c7fc551
Revises: 234f8738acac
Create Date: 2015-06-28 23:10:39.389450

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '27927c7fc551'
down_revision = '234f8738acac'


def upgrade():
    op.add_column('passport', sa.Column('flags', postgresql.JSONB(),
                                        nullable=True))


def downgrade():
    op.drop_column('passport', 'flags')
