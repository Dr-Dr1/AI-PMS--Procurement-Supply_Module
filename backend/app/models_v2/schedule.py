from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    Enum as SAEnum,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.core.enums import ActivityStatus, ActivityType, SubsystemType, DependencyType
# from app.models_v2.imports import XERImport



# =====================================================
# PROJECTS
# =====================================================

class Project(Base):
    __tablename__ = "projects"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    import_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("xer_imports.id"))

    proj_id: Mapped[int | None] = mapped_column(BigInteger)
    proj_short_name: Mapped[str | None] = mapped_column(String(255))
    proj_name: Mapped[str | None] = mapped_column(String(500))

    scd_start_date: Mapped[str | None] = mapped_column(String(100))
    scd_end_date: Mapped[str | None] = mapped_column(String(100))
    last_recalc_date: Mapped[str | None] = mapped_column(String(100))

    activity_count: Mapped[int] = mapped_column(Integer, default=0)
    completed: Mapped[int] = mapped_column(Integer, default=0)
    in_progress: Mapped[int] = mapped_column(Integer, default=0)
    not_started: Mapped[int] = mapped_column(Integer, default=0)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    schedule_import: Mapped["XERImport"] = relationship(back_populates="projects")


# =====================================================
# ACTIVITIES
# =====================================================

class Activity(Base):
    __tablename__ = "activities"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    import_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("xer_imports.id"))

    task_id: Mapped[int | None] = mapped_column(BigInteger)
    p6_activity_id: Mapped[str | None] = mapped_column(String(255))
    activity_name: Mapped[str | None] = mapped_column(String(500))

    status: Mapped[str | None] = mapped_column(
        SAEnum(
            ActivityStatus,
            name="schedule_v2_activity_status_enum",
            create_constraint=True,
        ),
        nullable=True,
    )
    activity_type: Mapped[str | None] = mapped_column(
        SAEnum(
            ActivityType,
            name="schedule_v2_activity_type_enum",
            create_constraint=True,
        ),
        nullable=True,
    )
    subsystem_type: Mapped[str | None] = mapped_column(
        SAEnum(
            SubsystemType,
            name="subsystem_type_enum",
            create_constraint=True,
            create_type=False,
        ),
        nullable=True,
    )

    is_critical: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_near_critical: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    requires_rfi: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    requires_material: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    duration: Mapped[float | None] = mapped_column(Float)
    total_float_hr_cnt: Mapped[float | None] = mapped_column(Float)
    free_float_hr_cnt: Mapped[float | None] = mapped_column(Float)
    float_days: Mapped[float | None] = mapped_column(Float, nullable=True)
    phys_complete_pct: Mapped[float | None] = mapped_column(Float)
    bac: Mapped[float | None] = mapped_column(Float, nullable=True, default=None)

    early_start_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    early_end_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    late_start_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    late_end_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    act_start_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    act_end_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    planned_start: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    planned_end: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    wbs_id: Mapped[int | None] = mapped_column(BigInteger)
    wbs_path: Mapped[str | None] = mapped_column(Text, nullable=True)
    clndr_id: Mapped[int | None] = mapped_column(BigInteger)
    proj_id: Mapped[int | None] = mapped_column(BigInteger)

    package_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("packages.id"), nullable=True)
    baseline_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("baselines.id"), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    schedule_import: Mapped["XERImport"] = relationship(back_populates="activities")


# =====================================================
# WBS
# =====================================================

class WBS(Base):
    __tablename__ = "wbs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    import_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("xer_imports.id"))

    wbs_id: Mapped[int | None] = mapped_column(BigInteger)
    wbs_name: Mapped[str | None] = mapped_column(String(500))
    wbs_short_name: Mapped[str | None] = mapped_column(String(255))
    parent_wbs_id: Mapped[int | None] = mapped_column(BigInteger)
    proj_id: Mapped[int | None] = mapped_column(BigInteger)
    seq_num: Mapped[int | None] = mapped_column(BigInteger)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    schedule_import: Mapped["XERImport"] = relationship(back_populates="wbs_items")


# =====================================================
# CALENDARS
# =====================================================

class Calendar(Base):
    __tablename__ = "calendars"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    import_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("xer_imports.id"))

    clndr_id: Mapped[int | None] = mapped_column(BigInteger)
    clndr_name: Mapped[str | None] = mapped_column(String(255))
    clndr_type: Mapped[str | None] = mapped_column(String(100))

    day_hr_cnt: Mapped[float | None] = mapped_column(Float)
    week_hr_cnt: Mapped[float | None] = mapped_column(Float)
    month_hr_cnt: Mapped[float | None] = mapped_column(Float)
    year_hr_cnt: Mapped[float | None] = mapped_column(Float)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    schedule_import: Mapped["XERImport"] = relationship(back_populates="calendars")


# =====================================================
# RESOURCES
# =====================================================

class Resource(Base):
    __tablename__ = "resources"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    import_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("xer_imports.id"))

    rsrc_id: Mapped[int | None] = mapped_column(BigInteger)
    rsrc_name: Mapped[str | None] = mapped_column(String(255))
    rsrc_short_name: Mapped[str | None] = mapped_column(String(255))
    rsrc_type: Mapped[str | None] = mapped_column(String(100))
    email_addr: Mapped[str | None] = mapped_column(String(255))
    parent_rsrc_id: Mapped[int | None] = mapped_column(BigInteger)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    schedule_import: Mapped["XERImport"] = relationship(back_populates="resources")


# =====================================================
# RELATIONSHIPS
# =====================================================

class Relationship(Base):
    __tablename__ = "relationships"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    import_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("xer_imports.id"))

    task_pred_id: Mapped[int | None] = mapped_column(BigInteger)
    task_id: Mapped[int | None] = mapped_column(BigInteger)
    task_code: Mapped[str | None] = mapped_column(String(255))

    pred_task_id: Mapped[int | None] = mapped_column(BigInteger)
    pred_task_code: Mapped[str | None] = mapped_column(String(255))

    pred_type: Mapped[str | None] = mapped_column(String(100))
    lag_hr_cnt: Mapped[float | None] = mapped_column(Float)
    interface_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    schedule_import: Mapped["XERImport"] = relationship(back_populates="relationships")


# =====================================================
# RESOURCE ASSIGNMENTS
# =====================================================

class ResourceAssignment(Base):
    __tablename__ = "assignments"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    import_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("xer_imports.id"))

    taskrsrc_id: Mapped[int | None] = mapped_column(BigInteger)
    task_id: Mapped[int | None] = mapped_column(BigInteger)
    rsrc_id: Mapped[int | None] = mapped_column(BigInteger)

    task_code: Mapped[str | None] = mapped_column(String(255))
    activity_name: Mapped[str | None] = mapped_column(String(500))
    rsrc_name: Mapped[str | None] = mapped_column(String(255))
    rsrc_type: Mapped[str | None] = mapped_column(String(100))

    target_qty: Mapped[float | None] = mapped_column(Float)
    target_cost: Mapped[float | None] = mapped_column(Float)
    act_reg_qty: Mapped[float | None] = mapped_column(Float)
    act_reg_cost: Mapped[float | None] = mapped_column(Float)
    act_ot_qty: Mapped[float | None] = mapped_column(Float)
    act_ot_cost: Mapped[float | None] = mapped_column(Float)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    schedule_import: Mapped["XERImport"] = relationship(back_populates="assignments")


# =====================================================
# DEPENDENCIES  (mapped/clean version of Relationship)
# =====================================================

class Dependency(Base):
    """
    CDM-mapped dependency. Relationship holds raw P6 integers;
    this table holds UUID FKs to activities plus computed cross-package /
    cross-subsystem flags — the right entity for CPM, EOT analysis, and AI.
    """
    __tablename__ = "dependencies"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    import_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("xer_imports.id"), nullable=False)

    predecessor_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("activities.id"), nullable=False, index=True
    )
    successor_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("activities.id"), nullable=False, index=True
    )

    dep_type: Mapped[str] = mapped_column(
        SAEnum(DependencyType, name="dependency_type_enum", create_constraint=True, create_type=False),
        nullable=False,
    )
    lag_days: Mapped[float | None] = mapped_column(Float, nullable=True)
    is_cross_package: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_cross_subsystem: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    interface_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
