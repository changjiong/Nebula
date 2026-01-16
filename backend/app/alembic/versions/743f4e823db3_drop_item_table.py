"""drop_item_table

Revision ID: 743f4e823db3
Revises: 234842999eeb
Create Date: 2026-01-16 11:00:19.842474

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes


# revision identifiers, used by Alembic.
revision = '743f4e823db3'
down_revision = '234842999eeb'
branch_labels = None
depends_on = None


def upgrade():
    # Drop the deprecated item table if it exists
    op.execute("DROP TABLE IF EXISTS item CASCADE")


def downgrade():
    # Recreate item table if rolling back
    op.create_table(
        'item',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.String(length=255), nullable=True),
        sa.Column('owner_id', sa.UUID(), nullable=False),
        sa.ForeignKeyConstraint(['owner_id'], ['user.id'], name='item_owner_id_fkey', ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id', name='item_pkey')
    )
