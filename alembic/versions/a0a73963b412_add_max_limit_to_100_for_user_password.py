"""add max limit to 100 for user password

Revision ID: a0a73963b412
Revises: 028cb9174d75
Create Date: 2025-10-22 11:30:10.749298

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a0a73963b412'
down_revision = '028cb9174d75'
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
