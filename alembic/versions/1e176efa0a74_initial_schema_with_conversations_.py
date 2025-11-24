"""Initial schema with conversations, messages, and transactions.

This migration creates the complete database schema for the AI transactional
agent including:
- conversations: Chat session data with LangGraph state
- messages: Individual conversation messages
- transactions: Payment transaction records

All tables use UUID primary keys and include proper indexes for performance.

Revision ID: 1e176efa0a74
Revises:
Create Date: 2025-11-24 01:45:20.908589

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "1e176efa0a74"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema to initial version.

    Creates:
    - conversations table
    - messages table
    - transactions table
    - All necessary indexes
    - Foreign key constraints
    """
    # Create conversations table
    op.create_table(
        "conversations",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("user_id", sa.String(length=255), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column(
            "started_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column("ended_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("agent_state", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    # Create indexes for conversations
    op.create_index(
        "idx_conversations_user_created",
        "conversations",
        ["user_id", "created_at"],
    )
    op.create_index(
        "idx_conversations_user_status",
        "conversations",
        ["user_id", "status"],
    )
    op.create_index(op.f("ix_conversations_created_at"), "conversations", ["created_at"])
    op.create_index(op.f("ix_conversations_status"), "conversations", ["status"])
    op.create_index(op.f("ix_conversations_user_id"), "conversations", ["user_id"])

    # Create messages table
    op.create_table(
        "messages",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "conversation_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column("role", sa.String(length=20), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("metadata", sa.Text(), nullable=True),
        sa.Column(
            "timestamp",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.ForeignKeyConstraint(
            ["conversation_id"],
            ["conversations.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    # Create indexes for messages
    op.create_index(
        "idx_messages_conversation_role",
        "messages",
        ["conversation_id", "role"],
    )
    op.create_index(
        "idx_messages_conversation_timestamp",
        "messages",
        ["conversation_id", "timestamp"],
    )
    op.create_index(op.f("ix_messages_conversation_id"), "messages", ["conversation_id"])
    op.create_index(op.f("ix_messages_role"), "messages", ["role"])
    op.create_index(op.f("ix_messages_timestamp"), "messages", ["timestamp"])

    # Create transactions table
    op.create_table(
        "transactions",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "conversation_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column("external_transaction_id", sa.String(length=255), nullable=True),
        sa.Column("user_id", sa.String(length=255), nullable=False),
        sa.Column("recipient_phone", sa.String(length=20), nullable=False),
        sa.Column("amount", sa.Float(), nullable=False),
        sa.Column("currency", sa.String(length=3), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("validation_id", sa.String(length=255), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.ForeignKeyConstraint(
            ["conversation_id"],
            ["conversations.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("external_transaction_id"),
    )
    # Create indexes for transactions
    op.create_index(
        "idx_transactions_status_created",
        "transactions",
        ["status", "created_at"],
    )
    op.create_index(
        "idx_transactions_user_created",
        "transactions",
        ["user_id", "created_at"],
    )
    op.create_index(
        "idx_transactions_user_status",
        "transactions",
        ["user_id", "status"],
    )
    op.create_index(op.f("ix_transactions_conversation_id"), "transactions", ["conversation_id"])
    op.create_index(op.f("ix_transactions_created_at"), "transactions", ["created_at"])
    op.create_index(
        op.f("ix_transactions_external_transaction_id"),
        "transactions",
        ["external_transaction_id"],
    )
    op.create_index(op.f("ix_transactions_recipient_phone"), "transactions", ["recipient_phone"])
    op.create_index(op.f("ix_transactions_status"), "transactions", ["status"])
    op.create_index(op.f("ix_transactions_user_id"), "transactions", ["user_id"])


def downgrade() -> None:
    """Downgrade schema by dropping all tables.

    WARNING: This will delete all data!
    """
    op.drop_table("transactions")
    op.drop_table("messages")
    op.drop_table("conversations")
