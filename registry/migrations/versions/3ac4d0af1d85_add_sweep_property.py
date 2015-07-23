"""Add sweep property

Revision ID: 3ac4d0af1d85
Revises: 27927c7fc551
Create Date: 2015-07-07 20:36:02.339991

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3ac4d0af1d85'
down_revision = '27927c7fc551'


def upgrade():
    op.add_column('visit', sa.Column('sweeped', sa.Boolean(), nullable=True))


def downgrade():
    op.drop_column('visit', 'sweeped')
