from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean, DateTime, Enum as SAEnum,
    ForeignKey, JSON, String, Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.core.enums import OrgType, RBACTier, AIAccessLevel


class Organization(Base):
    __tablename__ = "organizations"

    org_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    org_type: Mapped[str] = mapped_column(
        SAEnum(OrgType, name="org_type_enum", create_constraint=False),
        nullable=False,
    )
    org_name: Mapped[str] = mapped_column(String(300), nullable=False)
    packages: Mapped[list | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False,
    )


class Role(Base):
    __tablename__ = "roles"

    role_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    role_code: Mapped[str] = mapped_column(String(50), nullable=False, unique=True, index=True)
    role_name: Mapped[str] = mapped_column(String(150), nullable=False)
    rbac_tier: Mapped[str] = mapped_column(
        SAEnum(RBACTier, name="rbac_tier_enum", create_constraint=False),
        nullable=False,
    )
    ai_access_level: Mapped[str] = mapped_column(
        SAEnum(AIAccessLevel, name="ai_access_level_enum", create_constraint=False),
        nullable=False,
    )
    description: Mapped[str | None] = mapped_column(Text, nullable=True)


class Person(Base):
    __tablename__ = "persons"

    person_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    org_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.org_id"), nullable=False,
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    email: Mapped[str | None] = mapped_column(String(200), nullable=True, unique=False)
    role_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("roles.role_id"), nullable=False, index=True,
    )
    rbac_tier: Mapped[str] = mapped_column(
        SAEnum(RBACTier, name="rbac_tier_enum", create_constraint=False),
        nullable=False,
    )
    packages: Mapped[list | None] = mapped_column(JSON, nullable=True)
    ai_access_level: Mapped[str] = mapped_column(
        SAEnum(AIAccessLevel, name="ai_access_level_enum", create_constraint=False),
        nullable=False,
    )
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False,
    )
