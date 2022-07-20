"""Change items size to bigint

Revision ID: 644ba6b47222
Revises: e9ee5505b100
Create Date: 2022-07-20 00:07:29.948685

"""
from alembic import op
import sqlalchemy as sa

from app.config import ConfigClass


# revision identifiers, used by Alembic.
revision = '644ba6b47222'
down_revision = 'e9ee5505b100'
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column('items', 'size', existing_type=sa.Integer(), type_=sa.BIGINT(), schema=ConfigClass.METADATA_SCHEMA)


def downgrade():
    op.alter_column('items', 'size', existing_type=sa.BIGINT(), type_=sa.Integer(), schema=ConfigClass.METADATA_SCHEMA)
