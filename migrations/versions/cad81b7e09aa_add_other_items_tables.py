"""Add other items tables.

Revision ID: cad81b7e09aa
Revises: 5df5e2987093
Create Date: 2022-03-15 16:13:11.424561
"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import UUID

# revision identifiers, used by Alembic.
revision = 'cad81b7e09aa'
down_revision = '5df5e2987093'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'extended',
        sa.Column('id', UUID(), nullable=False),
        sa.Column('item_id', UUID(), nullable=False),
        sa.Column('extra', sa.JSON()),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('id'),
        schema='metadata',
    )
    op.create_table(
        'storage',
        sa.Column('id', UUID(), nullable=False),
        sa.Column('item_id', UUID(), nullable=False),
        sa.Column('location_uri', sa.String(), nullable=False),
        sa.Column('version', sa.String(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('id'),
        schema='metadata',
    )


def downgrade():
    op.drop_table('extended', schema='metadata')
    op.drop_table('storage', schema='metadata')
