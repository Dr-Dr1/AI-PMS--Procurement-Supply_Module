"""
Layer 1: Operational Core Entities — CDM v1.1

Activity, Dependency, Baseline, RFI, DPR, ITP, ProgressMeasurement.
These are the transactional entities created and modified daily by 26 workflows.
"""

import uuid
from datetime import date, datetime
from decimal import Decimal
from sqlalchemy import (
    String, Integer, Boolean, Date, DateTime, Numeric, Enum as SAEnum,
    ForeignKey, Text, JSON
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from app.core.database import Base
from app.core.enums import (
    SubsystemType, ActivityType, ActivityStatus, DependencyType,
    BaselineStatus, RFIStatus, RFIResult, InitiatorRole, RoutingTargetType,
    DPRStatus, ITPStatus,
)


# === Schedule Domain ===

class Activity(Base):
    """
    Atomic unit of schedule. Mirrors P6 activity structure (AS03).
    subsystem_type per AS01. requires_rfi links to quality chain (Q07).
    """
    __tablename__ = "activities"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    p6_activity_id: Mapped[str | None] = mapped_column(String(50))
    package_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("packages.id"), nullable=False)
    baseline_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("baselines.id"))
    wbs_path: Mapped[str] = mapped_column(String(500), nullable=False)
    subsystem_type: Mapped[str] = mapped_column(
        SAEnum(SubsystemType, name="subsystem_type_enum", create_constraint=True), nullable=False
    )
    activity_name: Mapped[str] = mapped_column(String(500), nullable=False)
    activity_type: Mapped[str] = mapped_column(
        SAEnum(ActivityType, name="activity_type_enum", create_constraint=True), nullable=False
    )
    status: Mapped[str] = mapped_column(
        SAEnum(ActivityStatus, name="activity_status_enum", create_constraint=True),
        nullable=False, default=ActivityStatus.NOT_STARTED
    )
    planned_start: Mapped[date] = mapped_column(Date, nullable=False)
    planned_finish: Mapped[date] = mapped_column(Date, nullable=False)
    actual_start: Mapped[date | None] = mapped_column(Date)
    actual_finish: Mapped[date | None] = mapped_column(Date)
    original_duration: Mapped[int] = mapped_column(Integer, nullable=False)
    remaining_duration: Mapped[int | None] = mapped_column(Integer)
    percent_complete: Mapped[Decimal | None] = mapped_column(Numeric(5, 2))
    float_days: Mapped[int | None] = mapped_column(Integer)
    is_critical: Mapped[bool] = mapped_column(Boolean, default=False)
    is_near_critical: Mapped[bool] = mapped_column(Boolean, default=False)
    requires_rfi: Mapped[bool] = mapped_column(Boolean, default=False)
    requires_material: Mapped[bool] = mapped_column(Boolean, default=False)
    calendar_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    # Relationships
    rfis: Mapped[list["RFI"]] = relationship(back_populates="activity", lazy="selectin")
    dprs: Mapped[list["DPREntry"]] = relationship(back_populates="activity", lazy="selectin")


class Dependency(Base):
    """
    Predecessor-successor links. Critical for CPM, cascade risk (A03), what-if sims.
    Cross-package and cross-subsystem flags per AS01 for high-risk identification.
    """
    __tablename__ = "dependencies"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    predecessor_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("activities.id"), nullable=False)
    successor_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("activities.id"), nullable=False)
    dep_type: Mapped[str] = mapped_column(
        SAEnum(DependencyType, name="dependency_type_enum", create_constraint=True), nullable=False
    )
    lag_days: Mapped[int | None] = mapped_column(Integer, default=0)
    is_cross_package: Mapped[bool] = mapped_column(Boolean, default=False)
    is_cross_subsystem: Mapped[bool] = mapped_column(Boolean, default=False)


class Baseline(Base):
    """
    Per AS02: single P6 master programme as contractual baseline.
    Versioned. Schedule variance always against locked baseline.
    """
    __tablename__ = "baselines"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    package_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("packages.id"), nullable=False)
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    status: Mapped[str] = mapped_column(
        SAEnum(BaselineStatus, name="baseline_status_enum", create_constraint=True),
        nullable=False, default=BaselineStatus.DRAFT
    )
    approved_by: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("persons.id"))
    locked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    source_file: Mapped[str | None] = mapped_column(String(500))
    import_hash: Mapped[str | None] = mapped_column(String(64))  # SHA-256 per NFR-11
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)


# === Quality Domain ===

class ITP(Base):
    """
    Inspection & Test Plan. Per AS09: must exist before RFI can be raised.
    Links to activities that require inspection.
    """
    __tablename__ = "itps"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    package_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("packages.id"), nullable=False)
    subsystem_type: Mapped[str] = mapped_column(
        SAEnum(SubsystemType, name="subsystem_type_enum", create_constraint=True, create_type=False),
        nullable=False
    )
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    status: Mapped[str] = mapped_column(
        SAEnum(ITPStatus, name="itp_status_enum", create_constraint=True),
        nullable=False, default=ITPStatus.DRAFT
    )
    hold_points: Mapped[dict | None] = mapped_column(JSON)  # [{name, description, witness_required}]
    test_standards: Mapped[dict | None] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)


class RFI(Base):
    """
    Request for Inspection — THE most architecturally significant entity (CDM Section 5.2.1).
    Per Q07: RFI closures are the primary verified progress signal.
    Per W02: initiator includes Planning Eng; routes to PMC/Client.
    Bridges quality (inspection), schedule (progress gate), cost (EVM verification).
    """
    __tablename__ = "rfis"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    package_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("packages.id"), nullable=False)
    activity_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("activities.id"), nullable=False)
    itp_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("itps.id"))
    subsystem_type: Mapped[str] = mapped_column(
        SAEnum(SubsystemType, name="subsystem_type_enum", create_constraint=True, create_type=False),
        nullable=False
    )
    rfi_number: Mapped[str] = mapped_column(String(50), nullable=False)
    initiator_person_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("persons.id"), nullable=False)
    initiator_role: Mapped[str] = mapped_column(
        SAEnum(InitiatorRole, name="initiator_role_enum", create_constraint=True), nullable=False
    )
    routing_target_type: Mapped[str] = mapped_column(
        SAEnum(RoutingTargetType, name="routing_target_type_enum", create_constraint=True),
        nullable=False, default=RoutingTargetType.OWNER_INTERNAL
    )
    assigned_inspector_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("persons.id"))
    status: Mapped[str] = mapped_column(
        SAEnum(RFIStatus, name="rfi_status_enum", create_constraint=True),
        nullable=False, default=RFIStatus.DRAFT
    )
    inspection_date: Mapped[date | None] = mapped_column(Date)
    result: Mapped[str | None] = mapped_column(
        SAEnum(RFIResult, name="rfi_result_enum", create_constraint=True)
    )
    # THIS IS THE PRIMARY PROGRESS INPUT per Q07
    verified_quantity: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    quantity_unit: Mapped[str | None] = mapped_column(String(30))
    # GPS from mobile capture
    location_lat: Mapped[Decimal | None] = mapped_column(Numeric(10, 7))
    location_lon: Mapped[Decimal | None] = mapped_column(Numeric(10, 7))
    photos: Mapped[list | None] = mapped_column(JSON)  # UUID references to document store
    # SLA
    sla_deadline: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    # AI-populated fields
    cp_impact_flag: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    closed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    # Relationships
    activity: Mapped["Activity"] = relationship(back_populates="rfis")


class DPR(Base):
    """
    Daily Progress Report header. Per AS07: daily granularity, GPS+photo+weather.
    Per Q07: DPR feeds ProgressMeasurement as SUPPORTING data, not primary.
    """
    __tablename__ = "dprs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    package_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("packages.id"), nullable=False)
    report_date: Mapped[date] = mapped_column(Date, nullable=False)
    submitted_by: Mapped[uuid.UUID] = mapped_column(ForeignKey("persons.id"), nullable=False)
    status: Mapped[str] = mapped_column(
        SAEnum(DPRStatus, name="dpr_status_enum", create_constraint=True),
        nullable=False, default=DPRStatus.DRAFT
    )
    weather: Mapped[str | None] = mapped_column(String(100))
    location_lat: Mapped[Decimal | None] = mapped_column(Numeric(10, 7))
    location_lon: Mapped[Decimal | None] = mapped_column(Numeric(10, 7))
    # Aggregate fields
    manpower_count: Mapped[int | None] = mapped_column(Integer)
    equipment_count: Mapped[int | None] = mapped_column(Integer)
    remarks: Mapped[str | None] = mapped_column(Text)
    photos: Mapped[list | None] = mapped_column(JSON)
    submitted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    approved_by: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("persons.id"))
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    entries: Mapped[list["DPREntry"]] = relationship(back_populates="dpr", lazy="selectin")


class DPREntry(Base):
    """Per-activity line item within a DPR. Links to Activity for progress tracking."""
    __tablename__ = "dpr_entries"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    dpr_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("dprs.id"), nullable=False)
    activity_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("activities.id"), nullable=False)
    subsystem_type: Mapped[str] = mapped_column(
        SAEnum(SubsystemType, name="subsystem_type_enum", create_constraint=True, create_type=False),
        nullable=False
    )
    reported_quantity: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    quantity_unit: Mapped[str | None] = mapped_column(String(30))
    description: Mapped[str | None] = mapped_column(Text)

    dpr: Mapped["DPR"] = relationship(back_populates="entries")
    activity: Mapped["Activity"] = relationship(back_populates="dprs")


# === Layer 2: Derived Intelligence ===

class ProgressMeasurement(Base):
    """
    THE composite entity per Q07. Bridges:
    - RFI verified quantity (PRIMARY)
    - DPR reported quantity (SUPPORTING)
    - Schedule percent complete (DERIVED)
    Discrepancy auto-populated for ambient AI surfacing.
    """
    __tablename__ = "progress_measurements"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    activity_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("activities.id"), nullable=False)
    package_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("packages.id"), nullable=False)
    period_date: Mapped[date] = mapped_column(Date, nullable=False)
    # Primary: from RFI approvals
    rfi_verified_qty: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    # Supporting: from DPR entries
    dpr_reported_qty: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    # Derived: schedule percent
    schedule_percent: Mapped[Decimal | None] = mapped_column(Numeric(5, 2))
    # Auto-flagged when DPR diverges from RFI > threshold
    discrepancy_flag: Mapped[bool] = mapped_column(Boolean, default=False)
    discrepancy_pct: Mapped[Decimal | None] = mapped_column(Numeric(5, 2))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)