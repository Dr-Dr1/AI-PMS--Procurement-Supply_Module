from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import BigInteger, DateTime, Enum as SAEnum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.core.enums import PackageStatus
# from app.models_v2.imports import XERImport

# ============================================================
# CORRIDOR
# Level-2 WBS (children of project root node) becomes Corridor
# ============================================================

class Corridor(Base):
    __tablename__ = "corridors"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    import_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("xer_imports.id")
    )

    proj_id: Mapped[int | None] = mapped_column(BigInteger)

    source_wbs_id: Mapped[int | None] = mapped_column(BigInteger)
    corridor_name: Mapped[str | None] = mapped_column(String(500))
    corridor_code: Mapped[str | None] = mapped_column(String(255))

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow
    )

    schedule_import: Mapped["XERImport"] = relationship(
        back_populates="corridors"
    )

    packages: Mapped[list["Package"]] = relationship(
        back_populates="corridor"
    )


# ============================================================
# PACKAGE
# Level-3 WBS → Package; Level-4+ WBS → Sub-Package (parent_package_id set)
# ============================================================

class Package(Base):
    __tablename__ = "packages"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    import_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("xer_imports.id")
    )

    proj_id: Mapped[int | None] = mapped_column(BigInteger)

    corridor_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("corridors.id"), nullable=True, index=True
    )

    contract_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("contracts.id"), nullable=True, index=True
    )

    source_wbs_id: Mapped[int | None] = mapped_column(BigInteger)
    parent_wbs_id: Mapped[int | None] = mapped_column(BigInteger)

    parent_package_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("packages.id"),
        nullable=True,
        index=True,
    )

    package_name: Mapped[str | None] = mapped_column(String(500))
    package_code: Mapped[str | None] = mapped_column(String(255))

    status: Mapped[str] = mapped_column(
        SAEnum(PackageStatus, name="package_status_enum", create_constraint=True),
        nullable=False,
        default=PackageStatus.ACTIVE,
    )

    contractor_name: Mapped[str | None] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow
    )

    schedule_import: Mapped["XERImport"] = relationship(
        back_populates="packages"
    )

    corridor: Mapped["Corridor | None"] = relationship(
        back_populates="packages"
    )
