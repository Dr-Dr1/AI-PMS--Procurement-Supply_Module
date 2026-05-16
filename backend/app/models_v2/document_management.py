from __future__ import annotations

import uuid
from datetime import date, datetime

from sqlalchemy import BigInteger, Boolean, Date, DateTime, ForeignKey, String, Text
from sqlalchemy import Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.core.enums import DocumentType, DocumentStatus, DocApprovalStatus, TransmittalStatus


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    package_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("packages.id"), nullable=False, index=True)

    doc_number: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    doc_type: Mapped[str] = mapped_column(
        SAEnum(DocumentType, name="document_type_enum", create_constraint=True),
        nullable=False,
    )
    revision: Mapped[str] = mapped_column(String(20), nullable=False, default="A")
    originator: Mapped[str | None] = mapped_column(String(200), nullable=True)
    subsystem_ref: Mapped[str | None] = mapped_column(String(200), nullable=True)
    discipline: Mapped[str | None] = mapped_column(String(100), nullable=True)
    status: Mapped[str] = mapped_column(
        SAEnum(DocumentStatus, name="document_status_enum", create_constraint=True),
        nullable=False,
        default=DocumentStatus.DRAFT,
    )

    storage_path: Mapped[str] = mapped_column(String(1000), nullable=False)
    filename: Mapped[str] = mapped_column(String(500), nullable=False)
    file_size_bytes: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    mime_type: Mapped[str | None] = mapped_column(String(200), nullable=True)
    version_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    ocr_text: Mapped[str | None] = mapped_column(Text, nullable=True)

    predecessor_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("documents.id"), nullable=True, index=True)
    is_current_revision: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    issue_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)


class Drawing(Base):
    __tablename__ = "drawings"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("documents.id"), nullable=False, unique=True)
    package_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("packages.id"), nullable=False, index=True)

    drawing_number: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    drawing_title: Mapped[str] = mapped_column(String(500), nullable=False)
    sheet_number: Mapped[str | None] = mapped_column(String(50), nullable=True)
    scale: Mapped[str | None] = mapped_column(String(50), nullable=True)
    revision_code: Mapped[str] = mapped_column(String(20), nullable=False, default="A")

    is_superseded: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    superseded_by_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("drawings.id"), nullable=True)
    superseded_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)


class ApprovalRecord(Base):
    __tablename__ = "approvals"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("documents.id"), nullable=False, index=True)

    reviewer_role: Mapped[str] = mapped_column(String(200), nullable=False)
    reviewer_name: Mapped[str | None] = mapped_column(String(300), nullable=True)
    status: Mapped[str] = mapped_column(
        SAEnum(DocApprovalStatus, name="doc_approval_status_enum", create_constraint=True),
        nullable=False,
        default=DocApprovalStatus.PENDING,
    )
    comments: Mapped[str | None] = mapped_column(Text, nullable=True)
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)


class Transmittal(Base):
    __tablename__ = "transmittals"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    package_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("packages.id"), nullable=False, index=True)

    transmittal_number: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    issued_to: Mapped[str | None] = mapped_column(String(500), nullable=True)
    purpose: Mapped[str | None] = mapped_column(String(300), nullable=True)
    status: Mapped[str] = mapped_column(
        SAEnum(TransmittalStatus, name="transmittal_status_enum", create_constraint=True),
        nullable=False,
        default=TransmittalStatus.DRAFT,
    )
    issued_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)


class TransmittalItem(Base):
    __tablename__ = "transmittal_items"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    transmittal_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("transmittals.id"), nullable=False, index=True)
    document_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("documents.id"), nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
