"""fix_id_column_to_bigint

Revision ID: fix_bigint_ids
Revises: ed2c4bd96b0c
Create Date: 2025-10-17
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = 'fix_bigint_ids'
down_revision = 'ed2c4bd96b0c'
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Alter id column in users table from Integer to BigInteger
    op.execute('ALTER TABLE users ALTER COLUMN id TYPE BIGINT')
    
    # Alter date column to BigInteger (it stores Unix timestamps)
    op.execute('ALTER TABLE users ALTER COLUMN date TYPE BIGINT')

def downgrade() -> None:
    # Downgrade back to Integer (will fail if data exceeds Integer range)
    op.execute('ALTER TABLE users ALTER COLUMN id TYPE INTEGER')
    op.execute('ALTER TABLE users ALTER COLUMN date TYPE INTEGER')