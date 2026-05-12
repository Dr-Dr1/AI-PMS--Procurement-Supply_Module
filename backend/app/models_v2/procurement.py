"""
Procurement module ORM models — 4 entities.

ProcurementPO → ProcurementPOLineItem (1:N)
ProcurementPO → ProcurementGRN (1:N)
ProcurementPO → ProcurementMaterialLink (1:N, nullable)
"""

import uuid
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    String, Integer, Boolean, Date, DateTime, Numeric, Text,
    Enum as SAEnum, ForeignKey, Index,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from app.core.database import Base
from app.core.enums import POStatus, GRNStatus, RiskLevel, MaterialLinkStatus


class ProcurementPO(Base):
    __tablename__ = "procurement_pos"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    package_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False, index=True)
    po_number: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    vendor_name: Mapped[str] = mapped_column(String(300), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    total_amount: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False, default=0)
    currency: Mapped[str] = mapped_column(String(10), nullable=False, default="INR")
    status: Mapped[str] = mapped_column(
        SAEnum(POStatus, name="po_status_enum", create_constraint=True),
        nullable=False, default=POStatus.DRAFT,
    )
    committed_delivery_date: Mapped[date | None] = mapped_column(Date)
    is_overdue: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow
    )

    items: Mapped[list["ProcurementPOLineItem"]] = relationship(
        back_populates="po", cascade="all, delete-orphan", lazy="selectin"
    )
    grns: Mapped[list["ProcurementGRN"]] = relationship(back_populates="po")
    material_links: Mapped[list["ProcurementMaterialLink"]] = relationship(back_populates="po")

    __table_args__ = (Index("ix_procurement_pos_package_id", "package_id"),)


class ProcurementPOLineItem(Base):
    __tablename__ = "procurement_po_line_items"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    po_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("procurement_pos.id", ondelete="CASCADE"), nullable=False, index=True
    )
    item_code: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    unit: Mapped[str] = mapped_column(String(50), nullable=False)
    quantity: Mapped[Decimal] = mapped_column(Numeric(14, 4), nullable=False)
    unit_rate: Mapped[Decimal] = mapped_column(Numeric(14, 4), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    po: Mapped["ProcurementPO"] = relationship(back_populates="items")


class ProcurementGRN(Base):
    __tablename__ = "procurement_grns"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    po_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("procurement_pos.id"), nullable=False, index=True)
    package_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False, index=True)
    grn_number: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    received_date: Mapped[date] = mapped_column(Date, nullable=False)
    received_qty: Mapped[Decimal] = mapped_column(Numeric(14, 4), nullable=False)
    ordered_qty: Mapped[Decimal | None] = mapped_column(Numeric(14, 4))
    unit: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(
        SAEnum(GRNStatus, name="grn_status_enum", create_constraint=True),
        nullable=False, default=GRNStatus.ACCEPTED,
    )
    test_certificate_ref: Mapped[str | None] = mapped_column(String(200))
    inspector: Mapped[str | None] = mapped_column(String(200))
    remarks: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    po: Mapped["ProcurementPO"] = relationship(back_populates="grns")

    __table_args__ = (
        Index("ix_procurement_grns_package_id", "package_id"),
        Index("ix_procurement_grns_po_id", "po_id"),
    )


class ProcurementMaterialLink(Base):
    __tablename__ = "procurement_material_links"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    package_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False, index=True)
    material_name: Mapped[str] = mapped_column(String(300), nullable=False)
    activity_id: Mapped[str | None] = mapped_column(String(200))
    po_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("procurement_pos.id"), index=True)
    is_critical_path: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    risk_score: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    risk_level: Mapped[str] = mapped_column(
        SAEnum(RiskLevel, name="risk_level_enum", create_constraint=True),
        nullable=False, default=RiskLevel.LOW,
    )
    status: Mapped[str] = mapped_column(
        SAEnum(MaterialLinkStatus, name="material_link_status_enum", create_constraint=True),
        nullable=False, default=MaterialLinkStatus.ON_TRACK,
    )
    planned_delivery_date: Mapped[date | None] = mapped_column(Date)
    actual_delivery_date: Mapped[date | None] = mapped_column(Date)
    last_risk_refresh: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow
    )

    po: Mapped["ProcurementPO | None"] = relationship(back_populates="material_links")

    __table_args__ = (Index("ix_procurement_material_links_package_id", "package_id"),)
