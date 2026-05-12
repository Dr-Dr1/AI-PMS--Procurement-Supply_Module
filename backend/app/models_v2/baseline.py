from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import (
    BigInteger, Boolean, DateTime, Float, ForeignKey,
    Integer, String, Text, UniqueConstraint,
    Enum as SAEnum,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.core.enums import BaselineStatus, BaselineType, EVMSnapshotType, EVSource, EVMPeriodType


class ScheduleV2Baseline(Base):
    __tablename__ = "schedule_v2_baselines"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    package_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("schedule_v2_packages.id"), nullable=False)
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    version_label: Mapped[str | None] = mapped_column(String(100), nullable=True)
    supersedes_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("schedule_v2_baselines.id"), nullable=True
    )
    status: Mapped[str] = mapped_column(
        SAEnum(BaselineStatus, name="schedule_v2_baseline_status_enum", create_constraint=True),
        nullable=False,
        default=BaselineStatus.DRAFT,
    )
    baseline_type: Mapped[str | None] = mapped_column(
        SAEnum(BaselineType, name="baseline_type_enum", create_constraint=True),
        nullable=True,
    )
    rebaseline_approved_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    rebaseline_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    approved_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    locked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    source_file: Mapped[str | None] = mapped_column(String(500))
    import_hash: Mapped[str | None] = mapped_column(String(64))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("package_id", "version", name="uq_baseline_package_version"),
    )


class ScheduleV2BaselineHistory(Base):
    __tablename__ = "schedule_v2_baseline_history"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    baseline_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("schedule_v2_baselines.id"), nullable=False)
    action: Mapped[str] = mapped_column(String(50), nullable=False)
    from_status: Mapped[str] = mapped_column(String(50), nullable=False)
    to_status: Mapped[str] = mapped_column(String(50), nullable=False)
    acted_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    remarks: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)


class ScheduleV2EVMSnapshot(Base):
    __tablename__ = "schedule_v2_evm_snapshots"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    baseline_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("schedule_v2_baselines.id"), nullable=False, index=True)
    activity_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("schedule_v2_activities.id"), nullable=False, index=True)
    data_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    snapshot_type: Mapped[str] = mapped_column(
        SAEnum(EVMSnapshotType, name="evm_snapshot_type_enum", create_constraint=True),
        nullable=False,
        index=True,
    )
    ev_source: Mapped[str | None] = mapped_column(
        SAEnum(EVSource, name="ev_source_enum", create_constraint=True),
        nullable=True,
    )
    period_type: Mapped[str | None] = mapped_column(
        SAEnum(EVMPeriodType, name="evm_period_type_enum", create_constraint=True),
        nullable=True,
    )
    bac: Mapped[float | None] = mapped_column(Float)
    planned_pct: Mapped[float | None] = mapped_column(Float)
    actual_pct: Mapped[float | None] = mapped_column(Float)
    ai_eac_forecast: Mapped[float | None] = mapped_column(Float, nullable=True)
    pv: Mapped[float | None] = mapped_column(Float)
    ev: Mapped[float | None] = mapped_column(Float)
    ac: Mapped[float | None] = mapped_column(Float)
    cv: Mapped[float | None] = mapped_column(Float)
    sv: Mapped[float | None] = mapped_column(Float)
    cpi: Mapped[float | None] = mapped_column(Float)
    spi: Mapped[float | None] = mapped_column(Float)
    eac: Mapped[float | None] = mapped_column(Float)
    etc: Mapped[float | None] = mapped_column(Float)
    vac: Mapped[float | None] = mapped_column(Float)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)


class ScheduleV2ActivityBaselineLink(Base):
    __tablename__ = "schedule_v2_activity_baseline_links"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    activity_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("schedule_v2_activities.id"), nullable=False, index=True
    )
    baseline_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("schedule_v2_baselines.id"), nullable=False, index=True
    )
    snapshot_planned_start: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    snapshot_planned_end: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    snapshot_bac: Mapped[float | None] = mapped_column(Float, nullable=True)

    __table_args__ = (
        UniqueConstraint("activity_id", "baseline_id", name="uq_activity_baseline_link"),
    )
