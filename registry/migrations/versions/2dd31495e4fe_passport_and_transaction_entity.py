"""Passport and Transaction entity

Revision ID: 2dd31495e4fe
Revises: None
Create Date: 2015-06-12 23:59:53.009428

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '2dd31495e4fe'
down_revision = None


def upgrade():
    op.create_table('passport',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('name', sa.String(length=128), nullable=False),
                    sa.Column(
                        'surname', sa.String(length=128), nullable=False),
                    sa.Column('deactivated', sa.Boolean(), nullable=True),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_table('transaction',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('passport_id', sa.Integer(), nullable=True),
                    sa.Column('timestamp', sa.DateTime(), nullable=True),
                    sa.Column('action',
                              postgresql.ENUM('IN', 'OUT',
                                              name='transaction_action'),
                              nullable=True),
                    sa.ForeignKeyConstraint(
                        ['passport_id'], ['passport.id'], ),
                    sa.PrimaryKeyConstraint('id')
                    )


def downgrade():
    op.drop_table('transaction')
    op.drop_table('passport')
