"""
Procurement & Supply Chain Models — CDM v1.1

Domain entities for W10 (Material Procurement), W11 (FAT), W12 (Vendor Management).
Follows the same patterns as layer0/layer1: UUID PKs, timezone-aware timestamps, enum columns.
"""

import uuid
from datetime import date, datetime
from decimal import Decimal
from sqlalchemy import (
    String, Integer, Boolean, Date, DateTime, Numeric, Enum as SAEnum,
    ForeignKey, Text, JSON,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from app.core.database import Base
from app.core.enums import (
    POStatus, VendorStatus, VendorTier, DeliveryStatus,
    FATStatus, ApprovalStatus, MaterialCategory, CurrencyCode,
    IndentStatus, EquipmentStrategy,
)


# ─── Vendor ────────────────────────────────────────────────────────────────────

class Vendor(Base):
    """
    Vendor / Supplier registry.
    Linked to Organization (layer0) when the same party is both an org-level
    entity and a procurement vendor.  vendor_tier is AI-recalculated nightly.
    """
    __tablename__ = "vendors"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(300), nullable=False)
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    contact_email: Mapped[str | None] = mapped_column(String(255))
    contact_phone: Mapped[str | None] = mapped_column(String(20))
    address: Mapped[str | None] = mapped_column(Text)
    gst_number: Mapped[str | None] = mapped_column(String(20))
    pan_number: Mapped[str | None] = mapped_column(String(15))
    vendor_status: Mapped[str] = mapped_column(
        SAEnum(VendorStatus, name="vendor_status_enum", create_constraint=True),
        nullable=False, default=VendorStatus.ACTIVE,
    )
    vendor_tier: Mapped[str | None] = mapped_column(
        SAEnum(VendorTier, name="vendor_tier_enum", create_constraint=True),
    )
    overall_score: Mapped[Decimal | None] = mapped_column(Numeric(5, 2))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    purchase_orders: Mapped[list["PurchaseOrder"]] = relationship(
        back_populates="vendor", lazy="selectin"
    )
    score_history: Mapped[list["VendorScoreHistory"]] = relationship(
        back_populates="vendor", lazy="selectin"
    )
    fat_tests: Mapped[list["FATTest"]] = relationship(
        back_populates="vendor", lazy="selectin"
    )


# ─── Material ──────────────────────────────────────────────────────────────────

class Material(Base):
    """
    Material master catalogue.  Category maps to subsystem groupings.
    specifications is a flexible JSON blob for material-specific attributes.
    """
    __tablename__ = "materials"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(300), nullable=False)
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    category: Mapped[str] = mapped_column(
        SAEnum(MaterialCategory, name="material_category_enum", create_constraint=True),
        nullable=False,
    )
    unit: Mapped[str] = mapped_column(String(30), nullable=False)  # e.g. "MT", "NOS", "RM"
    hsn_code: Mapped[str | None] = mapped_column(String(20))
    specifications: Mapped[dict | None] = mapped_column(JSON)
    is_equipment: Mapped[bool] = mapped_column(Boolean, default=False)
    acquisition_strategy: Mapped[str] = mapped_column(
        SAEnum(EquipmentStrategy, name="equipment_strategy_enum", create_constraint=True),
        nullable=False, default=EquipmentStrategy.NOT_APPLICABLE,
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )

    # Relationships
    line_items: Mapped[list["POLineItem"]] = relationship(
        back_populates="material", lazy="selectin"
    )


# ─── Purchase Order ────────────────────────────────────────────────────────────

class PurchaseOrder(Base):
    """
    Central procurement transaction entity.
    Status follows the 10-state PO lifecycle state machine from the design doc.
    Links to vendor, package (optional scope binding), and approval chain.
    """
    __tablename__ = "purchase_orders"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    po_number: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    vendor_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("vendors.id"), nullable=False
    )
    package_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("packages.id")
    )
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(
        SAEnum(POStatus, name="po_status_enum", create_constraint=True),
        nullable=False, default=POStatus.DRAFT,
    )
    total_value: Mapped[Decimal] = mapped_column(
        Numeric(15, 2), nullable=False, default=0
    )
    currency: Mapped[str] = mapped_column(
        SAEnum(CurrencyCode, name="currency_code_enum", create_constraint=True),
        nullable=False, default=CurrencyCode.INR,
    )
    delivery_address: Mapped[str | None] = mapped_column(Text)
    indent_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("indents.id"))
    expected_delivery_date: Mapped[date | None] = mapped_column(Date)
    actual_delivery_date: Mapped[date | None] = mapped_column(Date)
    terms_and_conditions: Mapped[str | None] = mapped_column(Text)
    remarks: Mapped[str | None] = mapped_column(Text)
    created_by: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("persons.id"))
    approved_by: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("persons.id"))
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    vendor: Mapped["Vendor"] = relationship(back_populates="purchase_orders")
    line_items: Mapped[list["POLineItem"]] = relationship(
        back_populates="purchase_order", lazy="selectin", cascade="all, delete-orphan"
    )
    deliveries: Mapped[list["Delivery"]] = relationship(
        back_populates="purchase_order", lazy="selectin"
    )
    fat_tests: Mapped[list["FATTest"]] = relationship(
        back_populates="purchase_order", lazy="selectin"
    )


# ─── PO Line Item ─────────────────────────────────────────────────────────────

class POLineItem(Base):
    """Individual material line within a PO. Tracks ordered vs delivered quantities."""
    __tablename__ = "po_line_items"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    po_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("purchase_orders.id"), nullable=False
    )
    material_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("materials.id"), nullable=False
    )
    description: Mapped[str | None] = mapped_column(String(500))
    quantity: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False)
    total_price: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False)
    delivered_quantity: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), default=0
    )
    unit: Mapped[str] = mapped_column(String(30), nullable=False)

    # Relationships
    purchase_order: Mapped["PurchaseOrder"] = relationship(back_populates="line_items")
    material: Mapped["Material"] = relationship(back_populates="line_items")


# ─── Delivery ──────────────────────────────────────────────────────────────────

class Delivery(Base):
    """
    Delivery / shipment record against a PO.
    A single PO can have multiple partial deliveries.
    """
    __tablename__ = "deliveries"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    po_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("purchase_orders.id"), nullable=False
    )
    delivery_number: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False
    )
    status: Mapped[str] = mapped_column(
        SAEnum(DeliveryStatus, name="delivery_status_enum", create_constraint=True),
        nullable=False, default=DeliveryStatus.SCHEDULED,
    )
    dispatch_date: Mapped[date | None] = mapped_column(Date)
    expected_arrival: Mapped[date | None] = mapped_column(Date)
    actual_arrival: Mapped[date | None] = mapped_column(Date)
    transporter_name: Mapped[str | None] = mapped_column(String(300))
    tracking_number: Mapped[str | None] = mapped_column(String(100))
    received_by: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("persons.id"))
    remarks: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )

    # Relationships
    purchase_order: Mapped["PurchaseOrder"] = relationship(back_populates="deliveries")
    items: Mapped[list["DeliveryItem"]] = relationship(
        back_populates="delivery", lazy="selectin", cascade="all, delete-orphan"
    )


class DeliveryItem(Base):
    """Per-line-item record within a delivery, tracking accepted/rejected quantities."""
    __tablename__ = "delivery_items"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    delivery_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("deliveries.id"), nullable=False
    )
    po_line_item_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("po_line_items.id"), nullable=False
    )
    delivered_quantity: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    accepted_quantity: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
    rejected_quantity: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
    rejection_reason: Mapped[str | None] = mapped_column(Text)

    # Relationships
    delivery: Mapped["Delivery"] = relationship(back_populates="items")


# ─── Factory Acceptance Test (FAT) ─────────────────────────────────────────────

class FATTest(Base):
    """
    Factory Acceptance Test — W11 workflow.
    Triggered T-14 days before expected delivery. Follows the
    SCHEDULED → NOTICE_SENT → IN_PROGRESS → PASSED/FAILED lifecycle.
    """
    __tablename__ = "fat_tests"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    po_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("purchase_orders.id"), nullable=False
    )
    vendor_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("vendors.id"), nullable=False
    )
    test_number: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False
    )
    status: Mapped[str] = mapped_column(
        SAEnum(FATStatus, name="fat_status_enum", create_constraint=True),
        nullable=False, default=FATStatus.SCHEDULED,
    )
    scheduled_date: Mapped[date] = mapped_column(Date, nullable=False)
    actual_date: Mapped[date | None] = mapped_column(Date)
    notice_sent_date: Mapped[date | None] = mapped_column(Date)
    inspector_name: Mapped[str | None] = mapped_column(String(200))
    inspector_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("persons.id"))
    test_location: Mapped[str | None] = mapped_column(String(500))
    test_report_url: Mapped[str | None] = mapped_column(String(1000))
    result_summary: Mapped[str | None] = mapped_column(Text)
    remarks: Mapped[str | None] = mapped_column(Text)
    retest_of: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("fat_tests.id")
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )

    # Relationships
    purchase_order: Mapped["PurchaseOrder"] = relationship(back_populates="fat_tests")
    vendor: Mapped["Vendor"] = relationship(back_populates="fat_tests")


# ─── Vendor Score History ──────────────────────────────────────────────────────

class VendorScoreHistory(Base):
    """
    Periodic vendor performance scoring (W12).
    Weighted formula: Overall = 0.35×Quality + 0.30×Delivery + 0.20×Compliance + 0.15×Price.
    AI agent recalculates nightly; manual overrides are allowed with audit trail.
    """
    __tablename__ = "vendor_score_history"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    vendor_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("vendors.id"), nullable=False
    )
    scoring_period: Mapped[str] = mapped_column(
        String(20), nullable=False
    )  # e.g. "2026-Q1"
    quality_score: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    delivery_score: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    compliance_score: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    price_score: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    overall_score: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    remarks: Mapped[str | None] = mapped_column(Text)
    scored_by: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("persons.id"))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )

    # Relationships
    vendor: Mapped["Vendor"] = relationship(back_populates="score_history")


# ─── Indent (Material Requisition) ─────────────────────────────────────────────

class Indent(Base):
    """
    Material Requisition / Indent (Step 1-4).
    Bridges site need to purchase action.
    """
    __tablename__ = "indents"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    indent_number: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    status: Mapped[str] = mapped_column(
        SAEnum(IndentStatus, name="indent_status_enum", create_constraint=True),
        nullable=False, default=IndentStatus.DRAFT,
    )
    requested_by: Mapped[uuid.UUID] = mapped_column(ForeignKey("persons.id"), nullable=False)
    need_date: Mapped[date] = mapped_column(Date, nullable=False)
    boq_reference: Mapped[str | None] = mapped_column(String(100))
    project_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("projects.id"))
    remarks: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    items: Mapped[list["IndentLineItem"]] = relationship(
        back_populates="indent", lazy="selectin", cascade="all, delete-orphan"
    )
    purchase_orders: Mapped[list["PurchaseOrder"]] = relationship(lazy="selectin")


class IndentLineItem(Base):
    """Items requested within an indent."""
    __tablename__ = "indent_line_items"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    indent_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("indents.id"), nullable=False
    )
    material_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("materials.id"), nullable=False
    )
    quantity: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    unit: Mapped[str] = mapped_column(String(30), nullable=False)
    estimated_cost: Mapped[Decimal | None] = mapped_column(Numeric(15, 2))

    # Relationships
    indent: Mapped["Indent"] = relationship(back_populates="items")
    material: Mapped["Material"] = relationship(lazy="selectin")


# ─── Material Schedule Link ────────────────────────────────────────────────────

class MaterialScheduleLink(Base):
    """
    Expert A09: High Value entity bridging Schedule (Activity) and Procurement (PO/Material).
    PO.expected_delivery_date vs Activity.planned_start.
    """
    __tablename__ = "material_schedule_links"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    material_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("materials.id"), nullable=False
    )
    activity_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("activities.id"), nullable=False
    )
    po_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("purchase_orders.id")
    )
    required_quantity: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    need_date: Mapped[date] = mapped_column(Date, nullable=False)
    
    # AI-derived status: ON_TRACK, LATE, AT_RISK
    status_flag: Mapped[str | None] = mapped_column(String(20))
    gap_days: Mapped[int | None] = mapped_column(Integer)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )

    # Relationships
    material: Mapped["Material"] = relationship(lazy="selectin")
    activity: Mapped["Activity"] = relationship(lazy="selectin")
    purchase_order: Mapped["PurchaseOrder"] = relationship(lazy="selectin")
