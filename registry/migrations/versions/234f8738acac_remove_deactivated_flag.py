"""Remove deactivated flag

Revision ID: 234f8738acac
Revises: 503ad9403152
Create Date: 2015-06-28 22:58:31.279849

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '234f8738acac'
down_revision = '503ad9403152'


def upgrade():
    op.drop_column('passport', 'deactivated')


def downgrade():
    op.add_column('passport', sa.Column('deactivated', sa.BOOLEAN(),
                                        autoincrement=False, nullable=True))
