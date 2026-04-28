"""initial schema

Revision ID: 0001
Revises:
Create Date: 2026-04-27
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # --- Enums ---
    business_status = postgresql.ENUM("trial", "active", "suspended", name="business_status")
    business_plan = postgresql.ENUM("free", "basic", "pro", name="business_plan")
    user_role = postgresql.ENUM("owner", "admin", name="user_role")
    assistant_tone = postgresql.ENUM("formal", "casual", name="assistant_tone")
    reservation_status = postgresql.ENUM(
        "pending", "confirmed", "cancelled", "no_show", name="reservation_status"
    )
    reservation_source = postgresql.ENUM("whatsapp", "manual", name="reservation_source")

    for enum in [business_status, business_plan, user_role, assistant_tone,
                 reservation_status, reservation_source]:
        enum.create(op.get_bind(), checkfirst=True)

    # --- businesses ---
    op.create_table(
        "businesses",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("type", sa.String(), nullable=False),
        sa.Column("timezone", sa.String(), nullable=False, server_default="UTC"),
        sa.Column(
            "status",
            sa.Enum("trial", "active", "suspended", name="business_status"),
            nullable=False,
            server_default="trial",
        ),
        sa.Column(
            "plan",
            sa.Enum("free", "basic", "pro", name="business_plan"),
            nullable=False,
            server_default="free",
        ),
        sa.Column("meta_business_id", sa.String(), nullable=True),
        sa.Column("whatsapp_phone_number_id", sa.String(), nullable=True, unique=True),
        sa.Column("whatsapp_access_token", sa.String(), nullable=True),
        sa.Column("created_at", sa.Date(), server_default=sa.func.current_date()),
    )
    op.create_index("ix_businesses_id", "businesses", ["id"])

    # --- users ---
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "business_id",
            sa.Integer(),
            sa.ForeignKey("businesses.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("email", sa.String(), nullable=False, unique=True),
        sa.Column("hashed_password", sa.String(), nullable=True),
        sa.Column("meta_user_id", sa.String(), nullable=True, unique=True),
        sa.Column(
            "role",
            sa.Enum("owner", "admin", name="user_role"),
            nullable=False,
            server_default="owner",
        ),
    )
    op.create_index("ix_users_id", "users", ["id"])
    op.create_index("ix_users_email", "users", ["email"])

    # --- business_configs ---
    op.create_table(
        "business_configs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "business_id",
            sa.Integer(),
            sa.ForeignKey("businesses.id", ondelete="CASCADE"),
            nullable=False,
            unique=True,
        ),
        sa.Column("open_days", postgresql.ARRAY(sa.Integer()), nullable=False, server_default="{}"),
        sa.Column("open_time", sa.Time(), nullable=False, server_default="09:00"),
        sa.Column("close_time", sa.Time(), nullable=False, server_default="18:00"),
        sa.Column("slot_duration", sa.Integer(), nullable=False, server_default="60"),
        sa.Column("max_per_slot", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("blocked_dates", postgresql.ARRAY(sa.Date()), nullable=False, server_default="{}"),
        sa.Column("assistant_name", sa.String(), nullable=False, server_default="Hermes"),
        sa.Column(
            "tone",
            sa.Enum("formal", "casual", name="assistant_tone"),
            nullable=False,
            server_default="formal",
        ),
        sa.Column("welcome_message", sa.String(), nullable=True),
    )
    op.create_index("ix_business_configs_id", "business_configs", ["id"])

    # --- reservations ---
    op.create_table(
        "reservations",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "business_id",
            sa.Integer(),
            sa.ForeignKey("businesses.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("client_name", sa.String(), nullable=False),
        sa.Column("client_phone", sa.String(), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("time_start", sa.Time(), nullable=False),
        sa.Column("time_end", sa.Time(), nullable=False),
        sa.Column("party_size", sa.Integer(), nullable=False, server_default="1"),
        sa.Column(
            "status",
            sa.Enum("pending", "confirmed", "cancelled", "no_show", name="reservation_status"),
            nullable=False,
            server_default="pending",
        ),
        sa.Column(
            "source",
            sa.Enum("whatsapp", "manual", name="reservation_source"),
            nullable=False,
            server_default="manual",
        ),
        sa.Column("notes", sa.String(), nullable=True),
        sa.Column("created_at", sa.Date(), server_default=sa.func.current_date()),
    )
    op.create_index("ix_reservations_id", "reservations", ["id"])
    op.create_index("ix_reservations_date", "reservations", ["date"])


def downgrade() -> None:
    op.drop_table("reservations")
    op.drop_table("business_configs")
    op.drop_table("users")
    op.drop_table("businesses")

    for name in [
        "reservation_source", "reservation_status", "assistant_tone",
        "user_role", "business_plan", "business_status",
    ]:
        postgresql.ENUM(name=name).drop(op.get_bind(), checkfirst=True)
