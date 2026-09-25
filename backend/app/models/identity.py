from __future__ import annotations

import enum
import uuid

from sqlalchemy import Boolean, CheckConstraint, Enum, ForeignKey, String, UniqueConstraint, true
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class Role(str, enum.Enum):
    ADMIN = "admin"
    ENCARGADO = "encargado"
    VENDEDOR = "vendedor"


# Nota: SQLAlchemy 2.0 mapea uuid.UUID nativamente (UUID en Postgres, CHAR(32)
# en SQLite para tests unitarios) sin necesidad de tipos por-dialecto.


class Branch(Base):
    __tablename__ = "branches"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    code: Mapped[str] = mapped_column(String(10), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(120))
    active: Mapped[bool] = mapped_column(
        Boolean, default=True, server_default=true(), nullable=False
    )


class UserProfile(Base):
    """Perfil local vinculado 1:1 con auth.users de Supabase (misma id)."""

    __tablename__ = "user_profiles"
    __table_args__ = (
        CheckConstraint("email = lower(email)", name="ck_user_profiles_email_lowercase"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    full_name: Mapped[str] = mapped_column(String(160), default="", server_default="")
    role: Mapped[Role] = mapped_column(
        Enum(Role, name="user_role", values_callable=lambda r: [e.value for e in r])
    )
    active: Mapped[bool] = mapped_column(
        Boolean, default=True, server_default=true(), nullable=False
    )


class UserBranchAssignment(Base):
    """Sucursales asignadas a un usuario (admin = todas, sin asignaciones)."""

    __tablename__ = "user_branch_assignments"
    __table_args__ = (UniqueConstraint("user_id", "branch_id", name="uq_user_branch"),)

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("user_profiles.id", ondelete="CASCADE"), index=True
    )
    branch_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("branches.id", ondelete="CASCADE"), index=True
    )
