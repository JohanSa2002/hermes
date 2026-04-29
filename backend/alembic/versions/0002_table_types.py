"""table types for restaurants

Revision ID: 0002
Revises: 0001
Create Date: 2026-04-29
"""

from alembic import op
import sqlalchemy as sa

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "table_types",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "business_id",
            sa.Integer(),
            sa.ForeignKey("businesses.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("capacity", sa.Integer(), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("label", sa.String(), nullable=True),
    )
    op.create_index("ix_table_types_id", "table_types", ["id"])
    op.create_index("ix_table_types_business_id", "table_types", ["business_id"])

    op.add_column(
        "reservations",
        sa.Column(
            "table_type_id",
            sa.Integer(),
            sa.ForeignKey("table_types.id", ondelete="SET NULL"),
            nullable=True,
        ),
    )


def downgrade() -> None:
    op.drop_column("reservations", "table_type_id")
    op.drop_table("table_types")
