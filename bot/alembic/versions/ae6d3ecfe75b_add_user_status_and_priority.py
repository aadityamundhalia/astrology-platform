"""add_user_status_and_priority

Revision ID: ae6d3ecfe75b
Revises: 3fa111ee7626
Create Date: 2025-10-17
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = 'ae6d3ecfe75b'
down_revision = '3fa111ee7626'
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Step 1: Add columns as NULLABLE first
    op.add_column('users', sa.Column('is_active', sa.Boolean(), nullable=True))
    op.add_column('users', sa.Column('priority', sa.Integer(), nullable=True))
    
    # Step 2: Set default values for existing rows
    op.execute('UPDATE users SET is_active = true WHERE is_active IS NULL')
    op.execute('UPDATE users SET priority = 5 WHERE priority IS NULL')
    
    # Step 3: Now make them NOT NULL
    op.alter_column('users', 'is_active', nullable=False)
    op.alter_column('users', 'priority', nullable=False)
    
    # Step 4: Add indexes
    op.create_index('idx_users_priority', 'users', ['priority'])
    op.create_index('idx_users_is_active', 'users', ['is_active'])

def downgrade() -> None:
    op.drop_index('idx_users_is_active', table_name='users')
    op.drop_index('idx_users_priority', table_name='users')
    op.drop_column('users', 'priority')
    op.drop_column('users', 'is_active')