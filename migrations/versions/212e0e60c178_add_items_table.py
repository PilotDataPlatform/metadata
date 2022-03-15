"""Add items table.

Revision ID: 212e0e60c178
Revises:
Create Date: 2022-03-14 15:17:34.248801
"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy import Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy_utils import LtreeType

# revision identifiers, used by Alembic.
revision = '212e0e60c178'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'items',
        sa.Column('id', UUID(), nullable=False),
        sa.Column('parent', UUID(), nullable=False),
        sa.Column('path', LtreeType(), nullable=False),
        sa.Column('type', Enum('file', 'folder', name='type_enum', create_type=False), nullable=False),
        sa.Column('zone', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('size', sa.Integer()),
        sa.Column('owner', sa.String()),
        sa.Column('container', UUID()),
        sa.Column(
            'container_type', Enum('project', 'dataset', name='container_enum', create_type=False), nullable=False
        ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('id'),
        schema='metadata',
    )


def downgrade():
    op.drop_table('items', schema='metadata')
