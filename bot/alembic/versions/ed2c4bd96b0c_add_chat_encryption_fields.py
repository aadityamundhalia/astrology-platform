"""add_chat_encryption_fields

Revision ID: ed2c4bd96b0c
Revises: fbecb718ecfb
Create Date: 2025-10-17 14:02:30.443303

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ed2c4bd96b0c'
down_revision: Union[str, Sequence[str], None] = 'fbecb718ecfb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add encrypt_chats column to users table
    op.add_column('users', sa.Column('encrypt_chats', sa.Boolean(), nullable=True))
    
    # Set default value for existing users (False = no encryption)
    op.execute('UPDATE users SET encrypt_chats = false WHERE encrypt_chats IS NULL')
    
    # Make it NOT NULL
    op.alter_column('users', 'encrypt_chats', nullable=False)
    
    # Add is_encrypted column to chat_history table
    op.add_column('chat_history', sa.Column('is_encrypted', sa.Boolean(), nullable=True, server_default='false'))
    
    # Set default value for existing chats
    op.execute('UPDATE chat_history SET is_encrypted = false WHERE is_encrypted IS NULL')
    
    # Make it NOT NULL
    op.alter_column('chat_history', 'is_encrypted', nullable=False)
    
    # Add indexes
    op.create_index('idx_users_encrypt_chats', 'users', ['encrypt_chats'])
    op.create_index('idx_chat_history_is_encrypted', 'chat_history', ['is_encrypted'])

def downgrade() -> None:
    op.drop_index('idx_chat_history_is_encrypted', table_name='chat_history')
    op.drop_index('idx_users_encrypt_chats', table_name='users')
    op.drop_column('chat_history', 'is_encrypted')
    op.drop_column('users', 'encrypt_chats')
