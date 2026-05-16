from __future__ import annotations

import uuid
from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, JSON, Numeric, String, Text
from sqlalchemy import Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.core.enums import (
    IncidentType, IncidentSeverity, InvestigationStatus, RootCauseMethod,
    PTWCategory, PTWStatus, ZoneType, CAPAStatus, SHEPlanStatus,
)


class Zone(Base):
    __tablename__ = "zones"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    package_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("packages.id"), nullable=False, index=True)
    zone_name: Mapped[str] = mapped_column(String(200), nullable=False)
    zone_type: Mapped[str] = mapped_column(SAEnum(ZoneType, name="zone_type_enum", create_constraint=True), nullable=False)
    polygon_coordinates: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    is_high_risk: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    geofencing_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)


class CAPA(Base):
    __tablename__ = "capas"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    package_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("packages.id"), nullable=False, index=True)
    incident_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True, index=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    corrective_action: Mapped[str | None] = mapped_column(Text, nullable=True)
    preventive_action: Mapped[str | None] = mapped_column(Text, nullable=True)
    assigned_to: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    due_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    status: Mapped[str] = mapped_column(SAEnum(CAPAStatus, name="capa_status_enum", create_constraint=True), nullable=False, default=CAPAStatus.OPEN)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    verified_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)


class Incident(Base):
    __tablename__ = "incidents"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    package_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("packages.id"), nullable=False, index=True)
    zone_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("zones.id"), nullable=True, index=True)
    incident_type: Mapped[str] = mapped_column(SAEnum(IncidentType, name="incident_type_enum", create_constraint=True), nullable=False)
    severity: Mapped[str] = mapped_column(SAEnum(IncidentSeverity, name="incident_severity_enum", create_constraint=True), nullable=False)
    severity_confirmed_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    severity_override_rationale: Mapped[str | None] = mapped_column(Text, nullable=True)
    location_lat: Mapped[float | None] = mapped_column(Numeric(10, 7), nullable=True)
    location_lon: Mapped[float | None] = mapped_column(Numeric(10, 7), nullable=True)
    reported_by: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    immediate_action: Mapped[str | None] = mapped_column(Text, nullable=True)
    photo_urls: Mapped[list | None] = mapped_column(JSON, nullable=True)
    investigation_status: Mapped[str] = mapped_column(SAEnum(InvestigationStatus, name="investigation_status_enum", create_constraint=True), nullable=False, default=InvestigationStatus.REPORTED)
    investigation_due_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    ltifr_contribution: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    root_cause_method: Mapped[str | None] = mapped_column(SAEnum(RootCauseMethod, name="root_cause_method_enum", create_constraint=True), nullable=True)
    root_cause_description: Mapped[str | None] = mapped_column(Text, nullable=True)
    capa_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("capas.id"), nullable=True)
    ai_severity_recommendation: Mapped[str | None] = mapped_column(SAEnum(IncidentSeverity, name="incident_severity_enum", create_constraint=False), nullable=True)
    ai_risk_score: Mapped[float | None] = mapped_column(Numeric(3, 2), nullable=True)
    ai_pattern_match_ids: Mapped[list | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)


class PTW(Base):
    __tablename__ = "ptws"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    package_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("packages.id"), nullable=False, index=True)
    zone_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("zones.id"), nullable=True, index=True)
    work_category: Mapped[str] = mapped_column(SAEnum(PTWCategory, name="ptw_category_enum", create_constraint=True), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    requested_by: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    authorized_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    status: Mapped[str] = mapped_column(SAEnum(PTWStatus, name="ptw_status_enum", create_constraint=True), nullable=False, default=PTWStatus.DRAFT)
    valid_from: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    valid_to: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    precautions: Mapped[str | None] = mapped_column(Text, nullable=True)
    ptw_cancelled_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    simultaneous_ops_conflict: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)


class ToolboxTalk(Base):
    __tablename__ = "toolbox_talks"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    package_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("packages.id"), nullable=False, index=True)
    zone_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("zones.id"), nullable=True, index=True)
    talk_date: Mapped[date] = mapped_column(Date, nullable=False)
    topic: Mapped[str] = mapped_column(String(500), nullable=False)
    conducted_by: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    attendee_count: Mapped[int] = mapped_column(Integer, nullable=False)
    evidence_doc_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)


class SHEPlan(Base):
    __tablename__ = "she_plans"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    package_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("packages.id"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    revision: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    status: Mapped[str] = mapped_column(SAEnum(SHEPlanStatus, name="she_plan_status_enum", create_constraint=True), nullable=False, default=SHEPlanStatus.DRAFT)
    approved_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    document_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    valid_from: Mapped[date | None] = mapped_column(Date, nullable=True)
    valid_to: Mapped[date | None] = mapped_column(Date, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
