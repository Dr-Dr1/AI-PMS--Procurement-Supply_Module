"""
Procurement DTOs (Pydantic v2 schemas).

Organized by domain: Vendor, Material, PurchaseOrder, Delivery, FAT, VendorScore.
Each domain has Create / Update / Response schemas.
"""

from __future__ import annotations

import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


# ═══════════════════════════════════════════════════════════════════════════════
# Vendor
# ═══════════════════════════════════════════════════════════════════════════════

class VendorCreate(BaseModel):
    name: str = Field(..., max_length=300, examples=["Larsen & Toubro Ltd"])
    code: str = Field(..., max_length=50, examples=["VND-LT-001"])
    contact_email: Optional[str] = Field(None, max_length=255)
    contact_phone: Optional[str] = Field(None, max_length=20)
    address: Optional[str] = None
    gst_number: Optional[str] = Field(None, max_length=20)
    pan_number: Optional[str] = Field(None, max_length=15)


class VendorUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=300)
    contact_email: Optional[str] = Field(None, max_length=255)
    contact_phone: Optional[str] = Field(None, max_length=20)
    address: Optional[str] = None
    gst_number: Optional[str] = Field(None, max_length=20)
    pan_number: Optional[str] = Field(None, max_length=15)
    vendor_status: Optional[str] = None
    vendor_tier: Optional[str] = None


class VendorResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    code: str
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    address: Optional[str] = None
    gst_number: Optional[str] = None
    pan_number: Optional[str] = None
    vendor_status: str
    vendor_tier: Optional[str] = None
    overall_score: Optional[Decimal] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime


class VendorListResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    code: str
    vendor_status: str
    vendor_tier: Optional[str] = None
    overall_score: Optional[Decimal] = None
    is_active: bool


# ═══════════════════════════════════════════════════════════════════════════════
# Material
# ═══════════════════════════════════════════════════════════════════════════════

class MaterialCreate(BaseModel):
    name: str = Field(..., max_length=300, examples=["TMT Steel Bar 16mm"])
    code: str = Field(..., max_length=50, examples=["MAT-STL-016"])
    description: Optional[str] = None
    category: str = Field(..., examples=["STRUCTURAL"])
    unit: str = Field(..., max_length=30, examples=["MT"])
    hsn_code: Optional[str] = Field(None, max_length=20)
    specifications: Optional[dict] = None
    is_equipment: bool = False
    acquisition_strategy: str = "NOT_APPLICABLE"


class MaterialUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=300)
    description: Optional[str] = None
    category: Optional[str] = None
    unit: Optional[str] = Field(None, max_length=30)
    hsn_code: Optional[str] = Field(None, max_length=20)
    specifications: Optional[dict] = None
    is_equipment: Optional[bool] = None
    acquisition_strategy: Optional[str] = None
    is_active: Optional[bool] = None


class MaterialResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    code: str
    description: Optional[str] = None
    category: str
    unit: str
    hsn_code: Optional[str] = None
    specifications: Optional[dict] = None
    is_equipment: bool
    acquisition_strategy: str
    is_active: bool
    created_at: datetime


# ═══════════════════════════════════════════════════════════════════════════════
# PO Line Item (nested within PO)
# ═══════════════════════════════════════════════════════════════════════════════

class POLineItemCreate(BaseModel):
    material_id: uuid.UUID
    description: Optional[str] = Field(None, max_length=500)
    quantity: Decimal = Field(..., gt=0)
    unit_price: Decimal = Field(..., gt=0)
    unit: str = Field(..., max_length=30)


class POLineItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    po_id: uuid.UUID
    material_id: uuid.UUID
    description: Optional[str] = None
    quantity: Decimal
    unit_price: Decimal
    total_price: Decimal
    delivered_quantity: Decimal
    unit: str


# ═══════════════════════════════════════════════════════════════════════════════
# Purchase Order
# ═══════════════════════════════════════════════════════════════════════════════

class PurchaseOrderCreate(BaseModel):
    po_number: str = Field(..., max_length=50, examples=["PO-2026-0001"])
    vendor_id: uuid.UUID
    package_id: Optional[uuid.UUID] = None
    title: str = Field(..., max_length=500, examples=["Steel Reinforcement for Station A"])
    description: Optional[str] = None
    currency: str = Field(default="INR", examples=["INR"])
    delivery_address: Optional[str] = None
    expected_delivery_date: Optional[date] = None
    indent_id: Optional[uuid.UUID] = None
    terms_and_conditions: Optional[str] = None
    remarks: Optional[str] = None
    line_items: list[POLineItemCreate] = Field(default_factory=list)


class PurchaseOrderUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=500)
    description: Optional[str] = None
    delivery_address: Optional[str] = None
    expected_delivery_date: Optional[date] = None
    terms_and_conditions: Optional[str] = None
    remarks: Optional[str] = None


class StatusUpdate(BaseModel):
    """Generic status transition request."""
    status: str
    remarks: Optional[str] = None


class PurchaseOrderResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    po_number: str
    vendor_id: uuid.UUID
    package_id: Optional[uuid.UUID] = None
    title: str
    description: Optional[str] = None
    status: str
    total_value: Decimal
    currency: str
    delivery_address: Optional[str] = None
    expected_delivery_date: Optional[date] = None
    actual_delivery_date: Optional[date] = None
    terms_and_conditions: Optional[str] = None
    remarks: Optional[str] = None
    indent_id: Optional[uuid.UUID] = None
    created_by: Optional[uuid.UUID] = None
    approved_by: Optional[uuid.UUID] = None
    approved_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    line_items: list[POLineItemResponse] = []


class PurchaseOrderListResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    po_number: str
    vendor_id: uuid.UUID
    title: str
    status: str
    total_value: Decimal
    currency: str
    expected_delivery_date: Optional[date] = None
    created_at: datetime


# ═══════════════════════════════════════════════════════════════════════════════
# Delivery
# ═══════════════════════════════════════════════════════════════════════════════

class DeliveryItemCreate(BaseModel):
    po_line_item_id: uuid.UUID
    delivered_quantity: Decimal = Field(..., gt=0)
    accepted_quantity: Decimal = Field(default=0, ge=0)
    rejected_quantity: Decimal = Field(default=0, ge=0)
    rejection_reason: Optional[str] = None


class DeliveryItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    delivery_id: uuid.UUID
    po_line_item_id: uuid.UUID
    delivered_quantity: Decimal
    accepted_quantity: Decimal
    rejected_quantity: Decimal
    rejection_reason: Optional[str] = None


class DeliveryCreate(BaseModel):
    po_id: uuid.UUID
    delivery_number: str = Field(..., max_length=50, examples=["DLV-2026-0001"])
    dispatch_date: Optional[date] = None
    expected_arrival: Optional[date] = None
    transporter_name: Optional[str] = Field(None, max_length=300)
    tracking_number: Optional[str] = Field(None, max_length=100)
    remarks: Optional[str] = None
    items: list[DeliveryItemCreate] = Field(default_factory=list)


class DeliveryUpdate(BaseModel):
    dispatch_date: Optional[date] = None
    expected_arrival: Optional[date] = None
    actual_arrival: Optional[date] = None
    transporter_name: Optional[str] = Field(None, max_length=300)
    tracking_number: Optional[str] = Field(None, max_length=100)
    remarks: Optional[str] = None


class DeliveryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    po_id: uuid.UUID
    delivery_number: str
    status: str
    dispatch_date: Optional[date] = None
    expected_arrival: Optional[date] = None
    actual_arrival: Optional[date] = None
    transporter_name: Optional[str] = None
    tracking_number: Optional[str] = None
    received_by: Optional[uuid.UUID] = None
    remarks: Optional[str] = None
    created_at: datetime
    items: list[DeliveryItemResponse] = []


# ═══════════════════════════════════════════════════════════════════════════════
# FAT (Factory Acceptance Test)
# ═══════════════════════════════════════════════════════════════════════════════

class FATTestCreate(BaseModel):
    po_id: uuid.UUID
    vendor_id: uuid.UUID
    test_number: str = Field(..., max_length=50, examples=["FAT-2026-0001"])
    scheduled_date: date
    inspector_name: Optional[str] = Field(None, max_length=200)
    inspector_id: Optional[uuid.UUID] = None
    test_location: Optional[str] = Field(None, max_length=500)
    remarks: Optional[str] = None


class FATTestUpdate(BaseModel):
    scheduled_date: Optional[date] = None
    actual_date: Optional[date] = None
    inspector_name: Optional[str] = Field(None, max_length=200)
    inspector_id: Optional[uuid.UUID] = None
    test_location: Optional[str] = Field(None, max_length=500)
    test_report_url: Optional[str] = Field(None, max_length=1000)
    result_summary: Optional[str] = None
    remarks: Optional[str] = None


class FATTestResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    po_id: uuid.UUID
    vendor_id: uuid.UUID
    test_number: str
    status: str
    scheduled_date: date
    actual_date: Optional[date] = None
    notice_sent_date: Optional[date] = None
    inspector_name: Optional[str] = None
    inspector_id: Optional[uuid.UUID] = None
    test_location: Optional[str] = None
    test_report_url: Optional[str] = None
    result_summary: Optional[str] = None
    remarks: Optional[str] = None
    retest_of: Optional[uuid.UUID] = None
    created_at: datetime


# ═══════════════════════════════════════════════════════════════════════════════
# Vendor Score History
# ═══════════════════════════════════════════════════════════════════════════════

class VendorScoreCreate(BaseModel):
    vendor_id: uuid.UUID
    scoring_period: str = Field(..., max_length=20, examples=["2026-Q1"])
    quality_score: Decimal = Field(..., ge=0, le=100)
    delivery_score: Decimal = Field(..., ge=0, le=100)
    compliance_score: Decimal = Field(..., ge=0, le=100)
    price_score: Decimal = Field(..., ge=0, le=100)
    remarks: Optional[str] = None


class VendorScoreResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    vendor_id: uuid.UUID
    scoring_period: str
    quality_score: Decimal
    delivery_score: Decimal
    compliance_score: Decimal
    price_score: Decimal
    overall_score: Decimal
    remarks: Optional[str] = None
    scored_by: Optional[uuid.UUID] = None
    created_at: datetime


# ═══════════════════════════════════════════════════════════════════════════════
# Indent (Material Requisition)
# ═══════════════════════════════════════════════════════════════════════════════

class IndentLineItemCreate(BaseModel):
    material_id: uuid.UUID
    quantity: Decimal = Field(..., gt=0)
    unit: str = Field(..., max_length=30)
    estimated_cost: Optional[Decimal] = None


class IndentLineItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    material_id: uuid.UUID
    quantity: Decimal
    unit: str
    estimated_cost: Optional[Decimal] = None


class IndentCreate(BaseModel):
    indent_number: str = Field(..., max_length=50, examples=["IND-2026-0001"])
    requested_by: uuid.UUID
    need_date: date
    project_id: Optional[uuid.UUID] = None
    boq_reference: Optional[str] = Field(None, max_length=100)
    remarks: Optional[str] = None
    items: list[IndentLineItemCreate] = Field(default_factory=list)


class IndentUpdate(BaseModel):
    status: Optional[str] = None
    need_date: Optional[date] = None
    boq_reference: Optional[str] = None
    remarks: Optional[str] = None


class IndentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    indent_number: str
    status: str
    requested_by: uuid.UUID
    need_date: date
    boq_reference: Optional[str] = None
    project_id: Optional[uuid.UUID] = None
    remarks: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    items: list[IndentLineItemResponse] = []


# ═══════════════════════════════════════════════════════════════════════════════
# Material Schedule Link
# ═══════════════════════════════════════════════════════════════════════════════

class MaterialScheduleLinkCreate(BaseModel):
    material_id: uuid.UUID
    activity_id: uuid.UUID
    po_id: Optional[uuid.UUID] = None
    required_quantity: Decimal = Field(..., gt=0)
    need_date: date


class MaterialScheduleLinkResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    material_id: uuid.UUID
    activity_id: uuid.UUID
    po_id: Optional[uuid.UUID] = None
    required_quantity: Decimal
    need_date: date
    status_flag: Optional[str] = None
    gap_days: Optional[int] = None
    created_at: datetime


# ═══════════════════════════════════════════════════════════════════════════════
# Dashboard / Summary
# ═══════════════════════════════════════════════════════════════════════════════

class ProcurementDashboard(BaseModel):
    total_purchase_orders: int = 0
    po_by_status: dict[str, int] = {}
    total_vendors: int = 0
    active_vendors: int = 0
    total_materials: int = 0
    pending_deliveries: int = 0
    upcoming_fat_tests: int = 0
    total_procurement_value: Decimal = Decimal("0.00")


# ═══════════════════════════════════════════════════════════════════════════════
# Pagination wrapper
# ═══════════════════════════════════════════════════════════════════════════════

class PaginatedResponse(BaseModel):
    """Generic paginated response wrapper."""
    items: list = []
    total: int = 0
    page: int = 1
    page_size: int = 20
    total_pages: int = 0


# Legacy DTO (kept for backward compatibility)

class ProcurementOrderCreate(BaseModel):
    title: str


class ProcurementOrderResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    status: str
