from __future__ import annotations

import uuid
from datetime import datetime, date

from sqlalchemy import (
    Boolean, DateTime, Date, Enum as SAEnum,
    Float, ForeignKey, Integer, JSON, String, Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.core.enums import (
    SubsystemType, ITPStatus, CheckpointType,
    RFIStatus, RFIResult, NCRStatus, NCRSeverity, ChecklistResult,
    TestRecordResult, PunchItemStatus,
)


class QualityITP(Base):
    __tablename__ = "quality_itps"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    package_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False, index=True)
    baseline_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    subsystem_type: Mapped[str | None] = mapped_column(SAEnum(SubsystemType, name="subsystem_type_enum", create_constraint=False), nullable=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    revision: Mapped[str] = mapped_column(String(20), nullable=False, default="A")
    discipline: Mapped[str | None] = mapped_column(String(100), nullable=True)
    applicable_phase: Mapped[str | None] = mapped_column(String(100), nullable=True)
    hold_point_default: Mapped[str | None] = mapped_column(String(50), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    reference_standard: Mapped[str | None] = mapped_column(String(500), nullable=True)
    spec_document: Mapped[str | None] = mapped_column(String(500), nullable=True)
    prepared_by: Mapped[str | None] = mapped_column(String(255), nullable=True)
    approved_by_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    effective_date: Mapped[str | None] = mapped_column(String(20), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(SAEnum(ITPStatus, name="itp_status_enum", create_constraint=True), nullable=False, default=ITPStatus.DRAFT)
    approved_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)


class QualityITPCheckpoint(Base):
    __tablename__ = "quality_itp_checkpoints"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    itp_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("quality_itps.id", ondelete="CASCADE"), nullable=False, index=True)
    activity_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    checkpoint_code: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    inspection_type: Mapped[str] = mapped_column(SAEnum(CheckpointType, name="checkpoint_type_enum", create_constraint=True), nullable=False)
    acceptance_criteria: Mapped[str | None] = mapped_column(Text, nullable=True)
    reference_doc: Mapped[str | None] = mapped_column(String(500), nullable=True)
    sequence: Mapped[int] = mapped_column(Integer, nullable=False, default=0)


class QualityRFI(Base):
    __tablename__ = "quality_rfis"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    rfi_number: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    activity_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False, index=True)
    checkpoint_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("quality_itp_checkpoints.id"), nullable=True)
    package_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False, index=True)
    subsystem_type: Mapped[str | None] = mapped_column(SAEnum(SubsystemType, name="subsystem_type_enum", create_constraint=False), nullable=True)
    title: Mapped[str | None] = mapped_column(String(500), nullable=True)
    discipline: Mapped[str | None] = mapped_column(String(100), nullable=True)
    priority: Mapped[str | None] = mapped_column(String(20), nullable=True)
    rfi_category: Mapped[str | None] = mapped_column(String(50), nullable=True)
    rfi_serial: Mapped[str | None] = mapped_column(String(20), nullable=True)
    location: Mapped[str | None] = mapped_column(String(500), nullable=True)
    chainage_from: Mapped[str | None] = mapped_column(String(50), nullable=True)
    chainage_to: Mapped[str | None] = mapped_column(String(50), nullable=True)
    raised_by_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    signing_place: Mapped[str | None] = mapped_column(String(255), nullable=True)
    cpm_office: Mapped[str | None] = mapped_column(String(255), nullable=True)
    inspection_date: Mapped[str | None] = mapped_column(String(20), nullable=True)
    inspection_time: Mapped[str | None] = mapped_column(String(10), nullable=True)
    due_date: Mapped[str | None] = mapped_column(String(20), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    boq_item_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    uom: Mapped[str | None] = mapped_column(String(50), nullable=True)
    quantity: Mapped[float | None] = mapped_column(Float, nullable=True)
    remarks: Mapped[str | None] = mapped_column(Text, nullable=True)
    reference_docs: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    attachment_name: Mapped[str | None] = mapped_column(String(500), nullable=True)
    status: Mapped[str] = mapped_column(SAEnum(RFIStatus, name="rfi_status_enum", create_constraint=True), nullable=False, default=RFIStatus.DRAFT)
    raised_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    raised_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    sla_deadline: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    assigned_to: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    assigned_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    inspected_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    result: Mapped[str | None] = mapped_column(SAEnum(RFIResult, name="rfi_result_enum", create_constraint=True), nullable=True)
    verified_quantity: Mapped[float | None] = mapped_column(Float, nullable=True)
    quantity_unit: Mapped[str | None] = mapped_column(String(50), nullable=True)
    verified_pct: Mapped[float | None] = mapped_column(Float, nullable=True)
    inspection_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    location_lat: Mapped[float | None] = mapped_column(Float, nullable=True)
    location_lon: Mapped[float | None] = mapped_column(Float, nullable=True)
    photos: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    ncr_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    cp_impact_flag: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    routing_targets: Mapped[list | None] = mapped_column(JSON, nullable=True)
    external_routing_status: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)


class QualityNCR(Base):
    __tablename__ = "quality_ncrs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ncr_number: Mapped[str] = mapped_column(String(50), nullable=False, unique=True, index=True)
    rfi_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    activity_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True, index=True)
    package_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False, index=True)
    subsystem_type: Mapped[str | None] = mapped_column(SAEnum(SubsystemType, name="subsystem_type_enum", create_constraint=False), nullable=True)
    status: Mapped[str] = mapped_column(SAEnum(NCRStatus, name="ncr_status_enum", create_constraint=True), nullable=False, default=NCRStatus.OPEN)
    severity: Mapped[str] = mapped_column(SAEnum(NCRSeverity, name="ncr_severity_enum", create_constraint=True), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    raised_by_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    cp_impact_flag: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    location: Mapped[str | None] = mapped_column(String(500), nullable=True)
    section_ref: Mapped[str | None] = mapped_column(String(255), nullable=True)
    design_origin_drawing_id: Mapped[str | None] = mapped_column(String(500), nullable=True)
    effectiveness_measure: Mapped[str | None] = mapped_column(Text, nullable=True)
    verification_method: Mapped[str | None] = mapped_column(Text, nullable=True)
    immediate_action_taken: Mapped[str | None] = mapped_column(Text, nullable=True)
    root_cause: Mapped[str | None] = mapped_column(Text, nullable=True)
    corrective_action: Mapped[str | None] = mapped_column(Text, nullable=True)
    preventive_action: Mapped[str | None] = mapped_column(Text, nullable=True)
    raised_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    raised_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    target_closure_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    closed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    re_inspection_rfi_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    photos: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)


class QualityChecklistTemplate(Base):
    __tablename__ = "quality_checklist_templates"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    package_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True, index=True)
    name: Mapped[str] = mapped_column(String(500), nullable=False)
    subsystem_type: Mapped[str | None] = mapped_column(SAEnum(SubsystemType, name="subsystem_type_enum", create_constraint=False), nullable=True)
    items: Mapped[list | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)


class QualityChecklistResponse(Base):
    __tablename__ = "quality_checklist_responses"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    rfi_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("quality_rfis.id", ondelete="CASCADE"), nullable=True, index=True)
    template_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("quality_checklist_templates.id"), nullable=False)
    responses: Mapped[list | None] = mapped_column(JSON, nullable=True)
    filled_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    filled_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    overall_result: Mapped[str | None] = mapped_column(SAEnum(ChecklistResult, name="checklist_result_enum", create_constraint=True), nullable=True)


class QualityTestRecord(Base):
    __tablename__ = "quality_test_records"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    test_record_number: Mapped[str] = mapped_column(String(50), nullable=False, unique=True, index=True)
    package_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False, index=True)
    activity_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    commissioning_test_ref: Mapped[str] = mapped_column(String(500), nullable=False)
    test_script_ref: Mapped[str | None] = mapped_column(String(500), nullable=True)
    result: Mapped[str] = mapped_column(SAEnum(TestRecordResult, name="test_record_result_enum", create_constraint=True), nullable=False, default=TestRecordResult.PASS)
    evidence: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    witness_attendance: Mapped[list | None] = mapped_column(JSON, nullable=True)
    retest_ref_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    punch_item_generated: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)


class QualityPunchItem(Base):
    __tablename__ = "quality_punch_items"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    punch_number: Mapped[str] = mapped_column(String(50), nullable=False, unique=True, index=True)
    package_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False, index=True)
    activity_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    ncr_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    section_ref: Mapped[str | None] = mapped_column(String(255), nullable=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    punch_category: Mapped[str | None] = mapped_column(String(100), nullable=True)
    priority: Mapped[str | None] = mapped_column(String(20), nullable=True)
    cp_impact_flag: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    location: Mapped[str | None] = mapped_column(String(500), nullable=True)
    drawing_reference: Mapped[str | None] = mapped_column(String(500), nullable=True)
    zone_ref: Mapped[str | None] = mapped_column(String(255), nullable=True)
    uom: Mapped[str | None] = mapped_column(String(50), nullable=True)
    quantity: Mapped[float | None] = mapped_column(Float, nullable=True)
    remarks: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(SAEnum(PunchItemStatus, name="punch_item_status_enum", create_constraint=True), nullable=False, default=PunchItemStatus.IDENTIFIED)
    target_closure_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    assigned_to: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    assigned_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    in_progress_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    verified_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    verification_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    closed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    closure_photos: Mapped[list | None] = mapped_column(JSON, nullable=True)
    witness_sign_off_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
