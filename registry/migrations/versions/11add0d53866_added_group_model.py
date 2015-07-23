"""Added group model

Revision ID: 11add0d53866
Revises: 1a0d8c340722
Create Date: 2015-07-22 19:11:42.205854

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '11add0d53866'
down_revision = '1a0d8c340722'


def upgrade():
    op.create_table(
        'group',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=128), nullable=False),
        sa.Column('flags', postgresql.JSONB(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name'))
    op.add_column(u'passport', sa.Column('group_id',
                  postgresql.UUID(as_uuid=True), nullable=True))
    op.create_foreign_key('fk_passport_group',
                          'passport', 'group',
                          ['group_id'], ['id'])


def downgrade():
    op.drop_constraint('fk_passport_group', 'passport', type_='foreignkey')
    op.drop_column(u'passport', 'group_id')
    op.drop_table('group')
