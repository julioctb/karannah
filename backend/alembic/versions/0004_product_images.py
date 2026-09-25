"""Add provider-neutral product image keys.

Revision ID: 0004_product_images
Revises: 0003_phase3
Create Date: 2026-09-18
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0004_product_images"
down_revision: str | None = "0003_phase3"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("products", sa.Column("image_key", sa.String(length=255), nullable=True))


def downgrade() -> None:
    op.drop_column("products", "image_key")
