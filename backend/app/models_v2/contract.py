from __future__ import annotations

import uuid
from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, JSON, Numeric, String, Text
from sqlalchemy import Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.core.enums import (
    ContractStandard, ContractStatus, EOTMethodology,
    NoticeType, NoticeStatus,
    ObligationType, ObligationStatus,
    CorrespondenceDirection, CorrespondenceStatus,
)


class Contract(Base):
    __tablename__ = "contracts"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    contract_number: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    status: Mapped[str] = mapped_column(
        SAEnum(ContractStatus, name="contract_status_enum", create_constraint=True),
        nullable=False,
        default=ContractStatus.ACTIVE,
    )

    owner_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organisations.id"), nullable=True, index=True
    )
    contractor_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organisations.id"), nullable=True, index=True
    )

    contract_standard: Mapped[str] = mapped_column(
        SAEnum(ContractStandard, name="contract_standard_enum", create_constraint=True, create_type=False),
        nullable=False,
    )

    contract_value: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False)
    revised_value: Mapped[float | None] = mapped_column(Numeric(15, 2), nullable=True)

    commencement_date: Mapped[date] = mapped_column(Date, nullable=False)
    completion_date: Mapped[date] = mapped_column(Date, nullable=False)

    dlp_months: Mapped[int] = mapped_column(Integer, nullable=False)

    eot_methodology: Mapped[str] = mapped_column(
        SAEnum(EOTMethodology, name="eot_methodology_enum", create_constraint=True, create_type=False),
        nullable=False,
    )

    ld_formula: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    notice_rules: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow
    )


class Clause(Base):
    """Per-contract clause library. Each clause is individually addressable for RAG (FR-M05-003)."""
    __tablename__ = "clauses"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    contract_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("contracts.id"), nullable=False, index=True
    )
    clause_number: Mapped[str] = mapped_column(String(50), nullable=False)
    clause_title: Mapped[str] = mapped_column(String(300), nullable=False)
    clause_text: Mapped[str] = mapped_column(Text, nullable=False)
    parent_clause_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("clauses.id"), nullable=True
    )
    tags: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    embedding_ref: Mapped[str | None] = mapped_column(String(200), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow
    )


class Notice(Base):
    """Contractual notice with time-bar monitoring. CDM §5.3.1. FR-M05-004/005."""
    __tablename__ = "notices"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    contract_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("contracts.id"), nullable=False, index=True
    )
    notice_number: Mapped[str] = mapped_column(String(50), nullable=False)
    notice_type: Mapped[str] = mapped_column(
        SAEnum(NoticeType, name="notice_type_enum", create_constraint=True), nullable=False
    )
    clause_ref: Mapped[str] = mapped_column(String(100), nullable=False)
    issued_by_org: Mapped[str] = mapped_column(String(200), nullable=False)
    issued_to_org: Mapped[str] = mapped_column(String(200), nullable=False)
    issue_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    time_bar_days: Mapped[int | None] = mapped_column(Integer, nullable=True)
    time_bar_deadline: Mapped[date | None] = mapped_column(Date, nullable=True)
    response_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    status: Mapped[str] = mapped_column(
        SAEnum(NoticeStatus, name="notice_status_enum", create_constraint=True),
        nullable=False, default=NoticeStatus.DRAFTED
    )
    is_time_barred: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    notice_validity_confirmed: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    precedent_search_done: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    ai_alert_sent: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    subject: Mapped[str] = mapped_column(String(500), nullable=False)
    draft_content: Mapped[str | None] = mapped_column(Text, nullable=True)
    attachments: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow
    )


class Obligation(Base):
    """Obligation register: recurring/milestone/conditional obligations per contract (FR-M05-006)."""
    __tablename__ = "obligations"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    contract_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("contracts.id"), nullable=False, index=True
    )
    obligation_type: Mapped[str] = mapped_column(
        SAEnum(ObligationType, name="obligation_type_enum", create_constraint=True), nullable=False
    )
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    due_date: Mapped[date] = mapped_column(Date, nullable=False)
    recurrence_pattern: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    responsible_role: Mapped[str] = mapped_column(String(200), nullable=False)
    linked_clause_ref: Mapped[str | None] = mapped_column(String(100), nullable=True)
    status: Mapped[str] = mapped_column(
        SAEnum(ObligationStatus, name="obligation_status_enum", create_constraint=True),
        nullable=False, default=ObligationStatus.PENDING
    )
    ai_extracted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_by: Mapped[str | None] = mapped_column(String(200), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow
    )


class Correspondence(Base):
    """Tamper-evident correspondence register. CDM Layer 1. FR-M05-008."""
    __tablename__ = "correspondence"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    contract_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("contracts.id"), nullable=False, index=True
    )
    ref_number: Mapped[str] = mapped_column(String(100), nullable=False)
    subject: Mapped[str] = mapped_column(String(500), nullable=False)
    direction: Mapped[str] = mapped_column(
        SAEnum(CorrespondenceDirection, name="correspondence_direction_enum", create_constraint=True),
        nullable=False
    )
    correspondence_date: Mapped[date] = mapped_column(Date, nullable=False)
    from_party: Mapped[str] = mapped_column(String(300), nullable=False)
    to_party: Mapped[str] = mapped_column(String(300), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    body_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    linked_clauses: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    linked_notice_ids: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    status: Mapped[str] = mapped_column(
        SAEnum(CorrespondenceStatus, name="correspondence_status_enum", create_constraint=True),
        nullable=False
    )
    reply_sla_deadline: Mapped[date | None] = mapped_column(Date, nullable=True)
    storage_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow
    )
