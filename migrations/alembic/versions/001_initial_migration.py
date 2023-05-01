"""Initial migration.

Revision ID: 001
Revises:
Create Date: 2023-05-01 18:51:00.000000
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'user',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('username', sa.String(), nullable=False),
        sa.Column('password', sa.String(), nullable=True),
        sa.Column('email', sa.String(), nullable=True),
        sa.Column('default_model', sa.String(), nullable=False),
        sa.Column('created_time', sa.DateTime(), nullable=False),
        sa.Column('last_login_time', sa.DateTime(), nullable=True),
        sa.Column('preferences', sa.JSON(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('username'),
        sa.UniqueConstraint('email'),
        sa.Index('user_username_idx', 'username'),
        sa.Index('user_email_idx', 'email'),
        sa.Index('user_created_time_idx', 'created_time'),
        sa.Index('user_last_login_time', 'last_login_time'),
    )

    op.create_table(
        'conversation',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(), nullable=True),
        sa.Column('model', sa.String(), nullable=False),
        sa.Column('created_time', sa.DateTime(), nullable=False),
        sa.Column('updated_time', sa.DateTime(), nullable=False),
        sa.Column('hidden', sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='CASCADE'),
        sa.Index('conversation_user_id_idx', 'user_id'),
        sa.Index('conversation_created_time_idx', 'created_time'),
        sa.Index('conversation_updated_time_idx', 'updated_time'),
        sa.Index('conversation_hidden_idx', 'hidden'),
    )

    op.create_table(
        'message',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('conversation_id', sa.Integer(), nullable=False),
        sa.Column('role', sa.String(), nullable=False),
        sa.Column('message', sa.String(), nullable=False),
        sa.Column('created_time', sa.DateTime(), nullable=False),
        sa.Column('prompt_tokens', sa.Integer(), nullable=False),
        sa.Column('completion_tokens', sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['conversation_id'], ['conversation.id'], ondelete='CASCADE'),
        sa.Index('message_conversation_id_idx', 'conversation_id'),
        sa.Index('message_created_time_idx', 'created_time'),
    )


def downgrade():
    op.drop_table('message')
    op.drop_table('conversation')
    op.drop_table('user')
