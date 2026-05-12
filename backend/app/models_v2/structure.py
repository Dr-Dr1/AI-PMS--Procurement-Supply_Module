from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class ScheduleV2Corridor(Base):
    __tablename__ = "schedule_v2_corridors"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    import_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("schedule_v2_imports.id"))
    proj_id: Mapped[int | None] = mapped_column(BigInteger)
    source_wbs_id: Mapped[int | None] = mapped_column(BigInteger)
    corridor_name: Mapped[str | None] = mapped_column(String(500))
    corridor_code: Mapped[str | None] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)


class ScheduleV2Package(Base):
    __tablename__ = "schedule_v2_packages"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    import_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("schedule_v2_imports.id"))
    proj_id: Mapped[int | None] = mapped_column(BigInteger)
    corridor_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("schedule_v2_corridors.id"), nullable=True, index=True
    )
    contract_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("schedule_v2_contracts.id"), nullable=True, index=True
    )
    source_wbs_id: Mapped[int | None] = mapped_column(BigInteger)
    parent_wbs_id: Mapped[int | None] = mapped_column(BigInteger)
    parent_package_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("schedule_v2_packages.id"), nullable=True, index=True
    )
    package_name: Mapped[str | None] = mapped_column(String(500))
    package_code: Mapped[str | None] = mapped_column(String(255))
    contractor_name: Mapped[str | None] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
