"""Add lexemes to passport

Revision ID: 1a0d8c340722
Revises: 13bd7a21c62
Create Date: 2015-07-17 20:24:25.156660

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy_utils.types.ts_vector import TSVectorType
from sqlalchemy_searchable import sync_trigger


# revision identifiers, used by Alembic.
revision = '1a0d8c340722'
down_revision = '13bd7a21c62'

conn = op.get_bind()


def upgrade():
    op.add_column('passport',
                  sa.Column('lexemes', TSVectorType(), nullable=False))
    sync_trigger(conn, 'passport', 'lexemes', ['surname', 'name'])


def downgrade():
    sync_trigger(conn, 'passport', 'lexemes', ['surname', 'name'])
    op.drop_column('passport', 'lexemes')
