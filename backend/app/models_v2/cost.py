"""
Cost module — domain models.

8 ORM models covering BOQ, RA Bills, Measurements, Deduction Config,
Variation Orders, and Cash Flow Projections.
All cost entities are scoped to a Contract (FK → contracts.id).
"""

import uuid
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    String, Integer, Boolean, Date, DateTime, Numeric, Text,
    Enum as SAEnum, ForeignKey, JSON, Index,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from app.core.database import Base
from app.core.enums import (
    BOQStatus, BOQSource,
    RABillStatus,
    VOCostStatus, VOTriggerType,
    CashFlowPeriod,
)


class BOQ(Base):
    __tablename__ = "boqs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    contract_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("contracts.id"), nullable=False, index=True)
    version_label: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[str] = mapped_column(
        SAEnum(BOQStatus, name="boq_status_enum", create_constraint=True),
        nullable=False,
        default=BOQStatus.DRAFT,
    )
    source: Mapped[str] = mapped_column(
        SAEnum(BOQSource, name="boq_source_enum", create_constraint=True),
        nullable=False,
        default=BOQSource.MANUAL,
    )
    total_amount: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False, default=0)
    currency: Mapped[str] = mapped_column(String(10), nullable=False, default="INR")
    approved_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    items: Mapped[list["BOQItem"]] = relationship(
        back_populates="boq", cascade="all, delete-orphan", lazy="selectin"
    )
    ra_bills: Mapped[list["RABill"]] = relationship(back_populates="boq")


class BOQItem(Base):
    __tablename__ = "boq_items"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    boq_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("boqs.id", ondelete="CASCADE"), nullable=False, index=True)
    item_code: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    unit: Mapped[str] = mapped_column(String(50), nullable=False)
    quantity: Mapped[Decimal] = mapped_column(Numeric(14, 4), nullable=False)
    unit_rate: Mapped[Decimal] = mapped_column(Numeric(14, 4), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False, default=0)
    wbs_code: Mapped[str | None] = mapped_column(String(100))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    boq: Mapped["BOQ"] = relationship(back_populates="items")
    ra_bill_items: Mapped[list["RABillItem"]] = relationship(back_populates="boq_item")


class RABill(Base):
    __tablename__ = "ra_bills"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    contract_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("contracts.id"), nullable=False, index=True)
    boq_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("boqs.id"), nullable=False)
    bill_number: Mapped[int] = mapped_column(Integer, nullable=False)
    period: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[str] = mapped_column(
        SAEnum(RABillStatus, name="ra_bill_status_enum", create_constraint=True),
        nullable=False,
        default=RABillStatus.DRAFT,
    )
    gross_amount: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False, default=0)
    deductions: Mapped[dict | None] = mapped_column(JSON)
    net_amount: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False, default=0)
    ai_overbilling_flag: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    overbilling_details: Mapped[dict | None] = mapped_column(JSON)
    sla_deadline: Mapped[date | None] = mapped_column(Date)
    payment_certificate_number: Mapped[str | None] = mapped_column(String(100))
    payment_received_date: Mapped[date | None] = mapped_column(Date)

    submitted_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))
    submitted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    qs_verified_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))
    qs_verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    qs_remarks: Mapped[str | None] = mapped_column(Text)
    ee_recommended_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))
    ee_recommended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    gm_approved_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))
    gm_approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    cpm_approved_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))
    cpm_approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    finance_processed_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))
    finance_processed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    finance_remarks: Mapped[str | None] = mapped_column(Text)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    boq: Mapped["BOQ"] = relationship(back_populates="ra_bills")
    items: Mapped[list["RABillItem"]] = relationship(
        back_populates="ra_bill", cascade="all, delete-orphan", lazy="selectin"
    )


class RABillItem(Base):
    __tablename__ = "ra_bill_items"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ra_bill_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("ra_bills.id", ondelete="CASCADE"), nullable=False, index=True)
    boq_item_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("boq_items.id"), nullable=False)
    reported_quantity: Mapped[Decimal] = mapped_column(Numeric(14, 4), nullable=False)
    reported_amount: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)
    previous_claimed_qty: Mapped[Decimal] = mapped_column(Numeric(14, 4), nullable=False, default=0)
    rfi_verified_qty: Mapped[Decimal | None] = mapped_column(Numeric(14, 4))
    overbilling_qty: Mapped[Decimal] = mapped_column(Numeric(14, 4), nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    ra_bill: Mapped["RABill"] = relationship(back_populates="items")
    boq_item: Mapped["BOQItem"] = relationship(back_populates="ra_bill_items")


class Measurement(Base):
    __tablename__ = "measurements"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    contract_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("contracts.id"), nullable=False, index=True)
    ra_bill_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("ra_bills.id"))
    boq_item_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("boq_items.id"))
    measurement_date: Mapped[date] = mapped_column(Date, nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    quantity_measured: Mapped[Decimal] = mapped_column(Numeric(14, 4), nullable=False)
    unit: Mapped[str] = mapped_column(String(50), nullable=False)
    verified_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))
    verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    remarks: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    __table_args__ = (
        Index("ix_measurements_ra_bill_id", "ra_bill_id"),
    )


class DeductionConfig(Base):
    __tablename__ = "deduction_configs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    contract_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("contracts.id"), nullable=False, unique=True)
    retention_pct: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False, default=0)
    retention_cap_pct: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False, default=0)
    recovery_pct: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False, default=0)
    tds_pct: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False, default=0)
    gst_pct: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False, default=0)
    ld_formula: Mapped[str | None] = mapped_column(String(300))
    ld_rate_per_day_pct: Mapped[Decimal] = mapped_column(Numeric(5, 4), nullable=False, default=0)
    ld_max_pct: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False, default=0)
    mobilization_advance: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)


class VariationOrder(Base):
    __tablename__ = "variation_orders"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    contract_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("contracts.id"), nullable=False, index=True)
    vo_number: Mapped[str] = mapped_column(String(100), nullable=False)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    trigger_type: Mapped[str | None] = mapped_column(
        SAEnum(VOTriggerType, name="vo_trigger_type_enum", create_constraint=True)
    )
    clause_ref: Mapped[str | None] = mapped_column(String(200))
    cost_impact: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False, default=0)
    revised_cost_impact: Mapped[Decimal | None] = mapped_column(Numeric(18, 4))
    schedule_impact_days: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    status: Mapped[str] = mapped_column(
        SAEnum(VOCostStatus, name="vo_cost_status_enum", create_constraint=True),
        nullable=False,
        default=VOCostStatus.IDENTIFIED,
    )
    submitted_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))
    submitted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    assessed_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))
    assessed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    assessment_remarks: Mapped[str | None] = mapped_column(Text)
    recommended_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))
    recommended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    approved_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    rejection_reason: Mapped[str | None] = mapped_column(Text)
    implemented_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)



class CashFlowProjection(Base):
    __tablename__ = "cash_flow_projections"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    contract_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("contracts.id"), nullable=False, index=True)
    period: Mapped[str] = mapped_column(
        SAEnum(CashFlowPeriod, name="cash_flow_period_enum", create_constraint=True),
        nullable=False,
        default=CashFlowPeriod.MONTHLY,
    )
    period_label: Mapped[str] = mapped_column(String(20), nullable=False)
    month: Mapped[date | None] = mapped_column(Date)
    planned_inflow: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False, default=0)
    actual_inflow: Mapped[Decimal | None] = mapped_column(Numeric(18, 4))
    planned_outflow: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False, default=0)
    actual_outflow: Mapped[Decimal | None] = mapped_column(Numeric(18, 4))
    net_position: Mapped[Decimal | None] = mapped_column(Numeric(18, 4))
    cumulative: Mapped[Decimal | None] = mapped_column(Numeric(18, 4))
    ai_forecast: Mapped[Decimal | None] = mapped_column(Numeric(18, 4))
    shortfall_alert: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    data_source: Mapped[str] = mapped_column(String(50), nullable=False, default="GENERATED")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
