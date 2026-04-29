"""
Procurement API Router — All REST endpoints for the procurement module.

Endpoint groups:
  /procurement/vendors          — Vendor CRUD + score management
  /procurement/materials        — Material catalogue CRUD
  /procurement/purchase-orders  — PO lifecycle (CRUD + state machine)
  /procurement/deliveries       — Delivery tracking
  /procurement/fat-tests        — Factory Acceptance Test scheduling
  /procurement/dashboard        — Aggregated procurement metrics
  /procurement/orders           — Legacy endpoints (backward compat)
"""

from __future__ import annotations

import uuid
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.modules.procurement.dtos.dtos import (
    # Vendor
    VendorCreate, VendorUpdate, VendorResponse, VendorListResponse,
    # Material
    MaterialCreate, MaterialUpdate, MaterialResponse,
    # PO
    PurchaseOrderCreate, PurchaseOrderUpdate, PurchaseOrderResponse,
    PurchaseOrderListResponse, StatusUpdate,
    # Delivery
    DeliveryCreate, DeliveryUpdate, DeliveryResponse,
    # FAT
    FATTestCreate, FATTestUpdate, FATTestResponse,
    # Vendor Scores
    VendorScoreCreate, VendorScoreResponse,
    # Dashboard
    ProcurementDashboard, PaginatedResponse,
    # Legacy
    ProcurementOrderCreate, ProcurementOrderResponse,
)
from app.modules.procurement.services.service import (
    VendorService, MaterialService, PurchaseOrderService,
    DeliveryService, FATTestService, VendorScoreService,
    DashboardService, ProcurementService,
)


router = APIRouter(prefix="/procurement", tags=["Procurement"])


# ═══════════════════════════════════════════════════════════════════════════════
# Dashboard
# ═══════════════════════════════════════════════════════════════════════════════

@router.get(
    "/dashboard/summary",
    response_model=ProcurementDashboard,
    summary="Get procurement dashboard metrics",
)
async def get_dashboard(db: AsyncSession = Depends(get_db)):
    """Aggregated procurement KPIs: PO counts by status, vendor stats, pending deliveries, etc."""
    return await DashboardService(db).get_summary()


# ═══════════════════════════════════════════════════════════════════════════════
# Vendors
# ═══════════════════════════════════════════════════════════════════════════════

@router.post(
    "/vendors",
    response_model=VendorResponse,
    status_code=201,
    summary="Register a new vendor",
)
async def create_vendor(
    data: VendorCreate,
    db: AsyncSession = Depends(get_db),
):
    return await VendorService(db).create_vendor(data)


@router.get(
    "/vendors",
    response_model=PaginatedResponse,
    summary="List vendors with pagination & filters",
)
async def list_vendors(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    vendor_status: Optional[str] = Query(None, description="Filter by vendor status"),
    is_active: Optional[bool] = Query(None, description="Filter by active flag"),
    db: AsyncSession = Depends(get_db),
):
    return await VendorService(db).list_vendors(
        page=page, page_size=page_size,
        vendor_status=vendor_status, is_active=is_active,
    )


@router.get(
    "/vendors/{vendor_id}",
    response_model=VendorResponse,
    summary="Get vendor details",
)
async def get_vendor(
    vendor_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    return await VendorService(db).get_vendor(vendor_id)


@router.put(
    "/vendors/{vendor_id}",
    response_model=VendorResponse,
    summary="Update vendor information",
)
async def update_vendor(
    vendor_id: uuid.UUID,
    data: VendorUpdate,
    db: AsyncSession = Depends(get_db),
):
    return await VendorService(db).update_vendor(vendor_id, data)


@router.delete(
    "/vendors/{vendor_id}",
    summary="Delete a vendor",
)
async def delete_vendor(
    vendor_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    return await VendorService(db).delete_vendor(vendor_id)


# ── Vendor Scores ─────────────────────────────────────────────────────────────

@router.post(
    "/vendors/{vendor_id}/scores",
    response_model=VendorScoreResponse,
    status_code=201,
    summary="Add vendor performance score",
)
async def add_vendor_score(
    vendor_id: uuid.UUID,
    data: VendorScoreCreate,
    db: AsyncSession = Depends(get_db),
):
    """
    Records a vendor score for a period. The overall score is auto-calculated using
    weighted formula: 0.35×Quality + 0.30×Delivery + 0.20×Compliance + 0.15×Price.
    Vendor tier is auto-updated: T1 ≥ 80, T2 ≥ 60, T3 < 60.
    """
    # Ensure the path param matches the body
    data.vendor_id = vendor_id
    return await VendorScoreService(db).add_score(data)


@router.get(
    "/vendors/{vendor_id}/scores",
    response_model=list[VendorScoreResponse],
    summary="Get vendor score history",
)
async def get_vendor_scores(
    vendor_id: uuid.UUID,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    return await VendorScoreService(db).get_vendor_scores(
        vendor_id, page=page, page_size=page_size
    )


# ═══════════════════════════════════════════════════════════════════════════════
# Materials
# ═══════════════════════════════════════════════════════════════════════════════

@router.post(
    "/materials",
    response_model=MaterialResponse,
    status_code=201,
    summary="Add a new material to the catalogue",
)
async def create_material(
    data: MaterialCreate,
    db: AsyncSession = Depends(get_db),
):
    return await MaterialService(db).create_material(data)


@router.get(
    "/materials",
    response_model=PaginatedResponse,
    summary="List materials with pagination & filters",
)
async def list_materials(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    category: Optional[str] = Query(None, description="Filter by material category"),
    is_active: Optional[bool] = Query(None, description="Filter by active flag"),
    db: AsyncSession = Depends(get_db),
):
    return await MaterialService(db).list_materials(
        page=page, page_size=page_size,
        category=category, is_active=is_active,
    )


@router.get(
    "/materials/{material_id}",
    response_model=MaterialResponse,
    summary="Get material details",
)
async def get_material(
    material_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    return await MaterialService(db).get_material(material_id)


@router.put(
    "/materials/{material_id}",
    response_model=MaterialResponse,
    summary="Update material information",
)
async def update_material(
    material_id: uuid.UUID,
    data: MaterialUpdate,
    db: AsyncSession = Depends(get_db),
):
    return await MaterialService(db).update_material(material_id, data)


# ═══════════════════════════════════════════════════════════════════════════════
# Purchase Orders
# ═══════════════════════════════════════════════════════════════════════════════

@router.post(
    "/purchase-orders",
    response_model=PurchaseOrderResponse,
    status_code=201,
    summary="Create a new purchase order",
)
async def create_purchase_order(
    data: PurchaseOrderCreate,
    db: AsyncSession = Depends(get_db),
):
    """Creates a PO in DRAFT status with line items. Total value is auto-calculated."""
    return await PurchaseOrderService(db).create_po(data)


@router.get(
    "/purchase-orders",
    response_model=PaginatedResponse,
    summary="List purchase orders with pagination & filters",
)
async def list_purchase_orders(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[str] = Query(None, alias="po_status", description="Filter by PO status"),
    vendor_id: Optional[uuid.UUID] = Query(None, description="Filter by vendor"),
    db: AsyncSession = Depends(get_db),
):
    return await PurchaseOrderService(db).list_pos(
        page=page, page_size=page_size,
        po_status=status, vendor_id=vendor_id,
    )


@router.get(
    "/purchase-orders/{po_id}",
    response_model=PurchaseOrderResponse,
    summary="Get purchase order details with line items",
)
async def get_purchase_order(
    po_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    return await PurchaseOrderService(db).get_po(po_id)


@router.put(
    "/purchase-orders/{po_id}",
    response_model=PurchaseOrderResponse,
    summary="Update purchase order fields",
)
async def update_purchase_order(
    po_id: uuid.UUID,
    data: PurchaseOrderUpdate,
    db: AsyncSession = Depends(get_db),
):
    return await PurchaseOrderService(db).update_po(po_id, data)


@router.patch(
    "/purchase-orders/{po_id}/status",
    response_model=PurchaseOrderResponse,
    summary="Transition PO status (state machine enforced)",
)
async def update_po_status(
    po_id: uuid.UUID,
    data: StatusUpdate,
    db: AsyncSession = Depends(get_db),
):
    """
    Transitions the PO status following the state machine:
    DRAFT → PENDING_APPROVAL → APPROVED → DISPATCHED → ACKNOWLEDGED →
    PARTIALLY_DELIVERED / DELIVERED → UNDER_INSPECTION → CLOSED.
    Any state can → CANCELLED (where applicable). Invalid transitions return 400.
    """
    return await PurchaseOrderService(db).update_po_status(po_id, data)


# ═══════════════════════════════════════════════════════════════════════════════
# Deliveries
# ═══════════════════════════════════════════════════════════════════════════════

@router.post(
    "/deliveries",
    response_model=DeliveryResponse,
    status_code=201,
    summary="Record a delivery against a PO",
)
async def create_delivery(
    data: DeliveryCreate,
    db: AsyncSession = Depends(get_db),
):
    return await DeliveryService(db).create_delivery(data)


@router.get(
    "/deliveries",
    response_model=PaginatedResponse,
    summary="List deliveries with pagination & filters",
)
async def list_deliveries(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    po_id: Optional[uuid.UUID] = Query(None, description="Filter by purchase order"),
    delivery_status: Optional[str] = Query(None, description="Filter by delivery status"),
    db: AsyncSession = Depends(get_db),
):
    return await DeliveryService(db).list_deliveries(
        page=page, page_size=page_size,
        po_id=po_id, delivery_status=delivery_status,
    )


@router.get(
    "/deliveries/{delivery_id}",
    response_model=DeliveryResponse,
    summary="Get delivery details with items",
)
async def get_delivery(
    delivery_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    return await DeliveryService(db).get_delivery(delivery_id)


@router.put(
    "/deliveries/{delivery_id}",
    response_model=DeliveryResponse,
    summary="Update delivery information",
)
async def update_delivery(
    delivery_id: uuid.UUID,
    data: DeliveryUpdate,
    db: AsyncSession = Depends(get_db),
):
    return await DeliveryService(db).update_delivery(delivery_id, data)


@router.patch(
    "/deliveries/{delivery_id}/status",
    response_model=DeliveryResponse,
    summary="Update delivery status",
)
async def update_delivery_status(
    delivery_id: uuid.UUID,
    data: StatusUpdate,
    db: AsyncSession = Depends(get_db),
):
    return await DeliveryService(db).update_delivery_status(delivery_id, data)


# ═══════════════════════════════════════════════════════════════════════════════
# FAT (Factory Acceptance Tests)
# ═══════════════════════════════════════════════════════════════════════════════

@router.post(
    "/fat-tests",
    response_model=FATTestResponse,
    status_code=201,
    summary="Schedule a Factory Acceptance Test",
)
async def create_fat_test(
    data: FATTestCreate,
    db: AsyncSession = Depends(get_db),
):
    return await FATTestService(db).create_fat(data)


@router.get(
    "/fat-tests",
    response_model=PaginatedResponse,
    summary="List FAT tests with pagination & filters",
)
async def list_fat_tests(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    po_id: Optional[uuid.UUID] = Query(None, description="Filter by purchase order"),
    vendor_id: Optional[uuid.UUID] = Query(None, description="Filter by vendor"),
    fat_status: Optional[str] = Query(None, description="Filter by FAT status"),
    db: AsyncSession = Depends(get_db),
):
    return await FATTestService(db).list_fats(
        page=page, page_size=page_size,
        po_id=po_id, vendor_id=vendor_id, fat_status=fat_status,
    )


@router.get(
    "/fat-tests/{fat_id}",
    response_model=FATTestResponse,
    summary="Get FAT test details",
)
async def get_fat_test(
    fat_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    return await FATTestService(db).get_fat(fat_id)


@router.put(
    "/fat-tests/{fat_id}",
    response_model=FATTestResponse,
    summary="Update FAT test information",
)
async def update_fat_test(
    fat_id: uuid.UUID,
    data: FATTestUpdate,
    db: AsyncSession = Depends(get_db),
):
    return await FATTestService(db).update_fat(fat_id, data)


@router.patch(
    "/fat-tests/{fat_id}/status",
    response_model=FATTestResponse,
    summary="Update FAT test status",
)
async def update_fat_status(
    fat_id: uuid.UUID,
    data: StatusUpdate,
    db: AsyncSession = Depends(get_db),
):
    return await FATTestService(db).update_fat_status(fat_id, data)


# ═══════════════════════════════════════════════════════════════════════════════
# Legacy Endpoints (backward compatibility)
# ═══════════════════════════════════════════════════════════════════════════════

@router.post(
    "/orders",
    response_model=ProcurementOrderResponse,
    summary="[Legacy] Create a simple procurement order",
    tags=["Procurement - Legacy"],
)
async def create_order(
    request: ProcurementOrderCreate,
    db: AsyncSession = Depends(get_db),
):
    return await ProcurementService(db).create_order(request)


@router.get(
    "/orders",
    summary="[Legacy] List simple procurement orders",
    tags=["Procurement - Legacy"],
)
async def list_orders(db: AsyncSession = Depends(get_db)):
    return await ProcurementService(db).list_orders()
