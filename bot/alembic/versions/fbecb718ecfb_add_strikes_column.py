"""add_strikes_column

Revision ID: fbecb718ecfb
Revises: ae6d3ecfe75b
Create Date: 2025-10-17 11:42:05.355751

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fbecb718ecfb'
down_revision: Union[str, Sequence[str], None] = 'ae6d3ecfe75b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add strikes column with default 0
    op.add_column('users', sa.Column('strikes', sa.Integer(), nullable=True))
    
    # Set default value for existing users
    op.execute('UPDATE users SET strikes = 0 WHERE strikes IS NULL')
    
    # Make it NOT NULL
    op.alter_column('users', 'strikes', nullable=False)
    
    # Add index for faster filtering
    op.create_index('idx_users_strikes', 'users', ['strikes'])

def downgrade() -> None:
    op.drop_index('idx_users_strikes', table_name='users')
    op.drop_column('users', 'strikes')