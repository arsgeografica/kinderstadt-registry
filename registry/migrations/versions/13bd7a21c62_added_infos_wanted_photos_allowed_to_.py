"""Added infos_wanted, photos_allowed to Passport

Revision ID: 13bd7a21c62
Revises: 23dcbdfd33b5
Create Date: 2015-07-13 22:56:10.183722

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '13bd7a21c62'
down_revision = '23dcbdfd33b5'


def upgrade():
    op.add_column(
        'passport',
        sa.Column('infos_wanted', sa.Boolean(), nullable=True))
    op.add_column(
        'passport',
        sa.Column('photos_allowed', sa.Boolean(), nullable=True))


def downgrade():
    op.drop_column('passport', 'photos_allowed')
    op.drop_column('passport', 'infos_wanted')
