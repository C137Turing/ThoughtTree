"""Initial database schema — sessions, messages, session_tree, user_config.

Revision ID: 001
Revises: None
Create Date: 2026-08-14
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # sessions table
    op.create_table(
        "sessions",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("parent_id", sa.String(36), nullable=True),
        sa.Column("root_id", sa.String(36), nullable=False),
        sa.Column(
            "status",
            sa.Enum("open", "closed", "minimized", name="session_status"),
            default="open",
            nullable=False,
        ),
        sa.Column("position_x", sa.Float, default=0.0),
        sa.Column("position_y", sa.Float, default=0.0),
        sa.Column("width", sa.Float, default=600.0),
        sa.Column("height", sa.Float, default=400.0),
        sa.Column(
            "created_at",
            sa.TIMESTAMP,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column(
            "updated_at",
            sa.TIMESTAMP,
            server_default=sa.text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"),
        ),
    )

    # Add foreign keys for sessions (self-referencing)
    op.create_foreign_key(
        "fk_sessions_parent_id",
        "sessions", "sessions",
        ["parent_id"], ["id"],
        ondelete="SET NULL",
    )
    op.create_foreign_key(
        "fk_sessions_root_id",
        "sessions", "sessions",
        ["root_id"], ["id"],
        ondelete="CASCADE",
    )

    # messages table
    op.create_table(
        "messages",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("session_id", sa.String(36), nullable=False),
        sa.Column(
            "role",
            sa.Enum("user", "assistant", "system", name="message_role"),
            nullable=False,
        ),
        sa.Column("content", sa.Text, nullable=False),
        sa.Column("is_quote", sa.Boolean, default=False),
        sa.Column(
            "created_at",
            sa.TIMESTAMP,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
    )
    op.create_foreign_key(
        "fk_messages_session_id",
        "messages", "sessions",
        ["session_id"], ["id"],
        ondelete="CASCADE",
    )

    # session_tree closure table
    op.create_table(
        "session_tree",
        sa.Column("ancestor_id", sa.String(36), nullable=False),
        sa.Column("descendant_id", sa.String(36), nullable=False),
        sa.Column("depth", sa.Integer, nullable=False, default=0),
        sa.PrimaryKeyConstraint("ancestor_id", "descendant_id"),
    )
    op.create_foreign_key(
        "fk_session_tree_ancestor",
        "session_tree", "sessions",
        ["ancestor_id"], ["id"],
        ondelete="CASCADE",
    )
    op.create_foreign_key(
        "fk_session_tree_descendant",
        "session_tree", "sessions",
        ["descendant_id"], ["id"],
        ondelete="CASCADE",
    )

    # user_config table (single-row)
    op.create_table(
        "user_config",
        sa.Column("id", sa.Integer, primary_key=True, default=1),
        sa.Column("api_key_encrypted", sa.Text, nullable=True),
        sa.Column("active_model", sa.String(50), default="deepseek"),
        sa.Column("ears_enabled", sa.Boolean, default=False),
        sa.Column(
            "numbering_style",
            sa.Enum("standard", "chinese", name="numbering_style"),
            default="standard",
        ),
        sa.Column("sdd_mapping_rules", sa.JSON, nullable=True),
        sa.Column(
            "created_at",
            sa.TIMESTAMP,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column(
            "updated_at",
            sa.TIMESTAMP,
            server_default=sa.text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"),
        ),
    )

    # Insert default row for user_config
    op.execute(
        "INSERT INTO user_config (id) VALUES (1) "
        "ON DUPLICATE KEY UPDATE id=id"
    )


def downgrade() -> None:
    op.drop_table("user_config")
    op.drop_table("session_tree")
    op.drop_table("messages")
    op.drop_table("sessions")

    # Drop ENUM types
    op.execute("DROP TYPE IF EXISTS numbering_style")
    op.execute("DROP TYPE IF EXISTS message_role")
    op.execute("DROP TYPE IF EXISTS session_status")
