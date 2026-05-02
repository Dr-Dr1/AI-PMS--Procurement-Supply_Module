"""
Procurement API Router — All endpoints for the Procurement & Supply Chain module.

Organized by domain:
  /vendors         — Vendor management (W12)
  /materials       — Material catalogue
  /purchase-orders — PO lifecycle (W10)
  /deliveries      — Delivery tracking
  /fat-tests       — Factory Acceptance Testing (W11)
  /dashboard       — Aggregated metrics

All endpoints are prefixed with /procurement by the router and
/api/v1 by main.py → final path: /api/v1/procurement/...
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
    # Purchase Order
    PurchaseOrderCreate, PurchaseOrderUpdate, PurchaseOrderResponse,
    PurchaseOrderListResponse, StatusUpdate,
    # Delivery
    DeliveryCreate, DeliveryUpdate, DeliveryResponse,
    # FAT
    FATTestCreate, FATTestUpdate, FATTestResponse,
    # Vendor Score
    VendorScoreCreate, VendorScoreResponse,
    # Indent
    IndentCreate, IndentUpdate, IndentResponse,
    # Material Schedule Link
    MaterialScheduleLinkCreate, MaterialScheduleLinkResponse,
    # Dashboard
    ProcurementDashboard,
    # Pagination
    PaginatedResponse,
    # Legacy
    ProcurementOrderCreate, ProcurementOrderResponse,
)
from app.modules.procurement.services.service import (
    VendorService, MaterialService, PurchaseOrderService,
    DeliveryService, FATTestService, VendorScoreService,
    IndentService, MaterialScheduleLinkService,
    DashboardService, ProcurementService,
)


router = APIRouter(prefix="/procurement", tags=["Procurement"])


# ═══════════════════════════════════════════════════════════════════════════════
#  DASHBOARD
# ═══════════════════════════════════════════════════════════════════════════════

@router.get(
    "/dashboard/summary",
    response_model=ProcurementDashboard,
    summary="Procurement Dashboard",
    description="Aggregated metrics: PO counts by status, vendor stats, pending deliveries, upcoming FATs, total procurement value.",
)
async def get_dashboard(db: AsyncSession = Depends(get_db)):
    return await DashboardService(db).get_summary()


# ═══════════════════════════════════════════════════════════════════════════════
#  VENDORS  (W12: Vendor Management)
# ═══════════════════════════════════════════════════════════════════════════════

@router.post(
    "/vendors",
    response_model=VendorResponse,
    status_code=201,
    summary="Register Vendor",
    description="Register a new vendor/supplier in the system.",
)
async def create_vendor(
    data: VendorCreate, db: AsyncSession = Depends(get_db)
):
    return await VendorService(db).create_vendor(data)


@router.get(
    "/vendors",
    response_model=PaginatedResponse,
    summary="List Vendors",
    description="Paginated vendor listing with optional filters.",
)
async def list_vendors(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[str] = Query(None, description="Filter by vendor_status"),
    is_active: Optional[bool] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    return await VendorService(db).list_vendors(
        page=page, page_size=page_size, status_filter=status, is_active=is_active,
    )


@router.get(
    "/vendors/{vendor_id}",
    response_model=VendorResponse,
    summary="Get Vendor",
    description="Retrieve a single vendor by ID.",
)
async def get_vendor(
    vendor_id: uuid.UUID, db: AsyncSession = Depends(get_db)
):
    return await VendorService(db).get_vendor(vendor_id)


@router.put(
    "/vendors/{vendor_id}",
    response_model=VendorResponse,
    summary="Update Vendor",
    description="Update vendor details. Only provided fields are modified.",
)
async def update_vendor(
    vendor_id: uuid.UUID,
    data: VendorUpdate,
    db: AsyncSession = Depends(get_db),
):
    return await VendorService(db).update_vendor(vendor_id, data)


# --- Vendor Scores ---

@router.post(
    "/vendors/{vendor_id}/scores",
    response_model=VendorScoreResponse,
    status_code=201,
    summary="Add Vendor Score",
    description="Record a periodic performance score. Overall score is auto-calculated using weighted formula (Q=0.35, D=0.30, C=0.20, P=0.15). Vendor tier is updated automatically.",
)
async def add_vendor_score(
    vendor_id: uuid.UUID,
    data: VendorScoreCreate,
    db: AsyncSession = Depends(get_db),
):
    # Override vendor_id from path
    data.vendor_id = vendor_id
    return await VendorScoreService(db).add_score(data)


@router.get(
    "/vendors/{vendor_id}/scores",
    response_model=list[VendorScoreResponse],
    summary="Vendor Score History",
    description="Retrieve historical performance scores for a vendor.",
)
async def get_vendor_scores(
    vendor_id: uuid.UUID,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    return await VendorScoreService(db).get_scores(
        vendor_id, page=page, page_size=page_size,
    )


# ═══════════════════════════════════════════════════════════════════════════════
#  MATERIALS
# ═══════════════════════════════════════════════════════════════════════════════

@router.post(
    "/materials",
    response_model=MaterialResponse,
    status_code=201,
    summary="Create Material",
    description="Add a new material to the catalogue.",
)
async def create_material(
    data: MaterialCreate, db: AsyncSession = Depends(get_db)
):
    return await MaterialService(db).create_material(data)


@router.get(
    "/materials",
    response_model=PaginatedResponse,
    summary="List Materials",
    description="Paginated material catalogue with optional category filter.",
)
async def list_materials(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    category: Optional[str] = Query(None, description="Filter by MaterialCategory"),
    is_active: Optional[bool] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    return await MaterialService(db).list_materials(
        page=page, page_size=page_size, category=category, is_active=is_active,
    )


@router.get(
    "/materials/{material_id}",
    response_model=MaterialResponse,
    summary="Get Material",
    description="Retrieve a single material by ID.",
)
async def get_material(
    material_id: uuid.UUID, db: AsyncSession = Depends(get_db)
):
    return await MaterialService(db).get_material(material_id)


@router.put(
    "/materials/{material_id}",
    response_model=MaterialResponse,
    summary="Update Material",
    description="Update material details. Only provided fields are modified.",
)
async def update_material(
    material_id: uuid.UUID,
    data: MaterialUpdate,
    db: AsyncSession = Depends(get_db),
):
    return await MaterialService(db).update_material(material_id, data)


# ═══════════════════════════════════════════════════════════════════════════════
#  PURCHASE ORDERS  (W10: Material Procurement)
# ═══════════════════════════════════════════════════════════════════════════════

@router.post(
    "/purchase-orders",
    response_model=PurchaseOrderResponse,
    status_code=201,
    summary="Create Purchase Order",
    description="Create a new PO with line items. Total value is auto-calculated from line items. PO starts in DRAFT status.",
)
async def create_purchase_order(
    data: PurchaseOrderCreate, db: AsyncSession = Depends(get_db)
):
    return await PurchaseOrderService(db).create_order(data)


@router.get(
    "/purchase-orders",
    response_model=PaginatedResponse,
    summary="List Purchase Orders",
    description="Paginated PO listing with optional status and vendor filters.",
)
async def list_purchase_orders(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[str] = Query(None, description="Filter by POStatus"),
    vendor_id: Optional[uuid.UUID] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    return await PurchaseOrderService(db).list_orders(
        page=page, page_size=page_size,
        status_filter=status, vendor_id=vendor_id,
    )


@router.get(
    "/purchase-orders/{po_id}",
    response_model=PurchaseOrderResponse,
    summary="Get Purchase Order",
    description="Retrieve a single PO with all line items.",
)
async def get_purchase_order(
    po_id: uuid.UUID, db: AsyncSession = Depends(get_db)
):
    return await PurchaseOrderService(db).get_order(po_id)


@router.put(
    "/purchase-orders/{po_id}",
    response_model=PurchaseOrderResponse,
    summary="Update Purchase Order",
    description="Update PO details. Only allowed when PO is in DRAFT status.",
)
async def update_purchase_order(
    po_id: uuid.UUID,
    data: PurchaseOrderUpdate,
    db: AsyncSession = Depends(get_db),
):
    return await PurchaseOrderService(db).update_order(po_id, data)


@router.patch(
    "/purchase-orders/{po_id}/status",
    response_model=PurchaseOrderResponse,
    summary="Update PO Status",
    description="Transition PO to a new status. Validates against the PO state machine: DRAFT → PENDING_APPROVAL → APPROVED → DISPATCHED → ACKNOWLEDGED → DELIVERED → UNDER_INSPECTION → CLOSED. CANCELLED is reachable from DRAFT, PENDING_APPROVAL, or APPROVED.",
)
async def update_po_status(
    po_id: uuid.UUID,
    data: StatusUpdate,
    db: AsyncSession = Depends(get_db),
):
    return await PurchaseOrderService(db).update_status(po_id, data)


@router.post(
    "/indents/{indent_id}/convert-to-po",
    response_model=PurchaseOrderResponse,
    status_code=201,
    summary="Convert Indent to PO",
    description="Step 6: Convert an APPROVED indent into a DRAFT Purchase Order. Requires selecting a vendor and providing a PO number.",
)
async def convert_indent_to_po(
    indent_id: uuid.UUID,
    vendor_id: uuid.UUID = Query(...),
    po_number: str = Query(...),
    db: AsyncSession = Depends(get_db),
):
    return await PurchaseOrderService(db).create_from_indent(indent_id, vendor_id, po_number)


# ═══════════════════════════════════════════════════════════════════════════════
#  DELIVERIES
# ═══════════════════════════════════════════════════════════════════════════════

@router.post(
    "/deliveries",
    response_model=DeliveryResponse,
    status_code=201,
    summary="Create Delivery",
    description="Record a new delivery/shipment against a purchase order.",
)
async def create_delivery(
    data: DeliveryCreate, db: AsyncSession = Depends(get_db)
):
    return await DeliveryService(db).create_delivery(data)


@router.get(
    "/deliveries",
    response_model=PaginatedResponse,
    summary="List Deliveries",
    description="Paginated delivery listing with optional PO and status filters.",
)
async def list_deliveries(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    po_id: Optional[uuid.UUID] = Query(None),
    status: Optional[str] = Query(None, description="Filter by DeliveryStatus"),
    db: AsyncSession = Depends(get_db),
):
    return await DeliveryService(db).list_deliveries(
        page=page, page_size=page_size, po_id=po_id, status_filter=status,
    )


@router.get(
    "/deliveries/{delivery_id}",
    response_model=DeliveryResponse,
    summary="Get Delivery",
    description="Retrieve a single delivery with all line items.",
)
async def get_delivery(
    delivery_id: uuid.UUID, db: AsyncSession = Depends(get_db)
):
    return await DeliveryService(db).get_delivery(delivery_id)


@router.put(
    "/deliveries/{delivery_id}",
    response_model=DeliveryResponse,
    summary="Update Delivery",
    description="Update delivery details (dates, transporter, tracking).",
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
    summary="Update Delivery Status",
    description="Transition delivery status. Valid transitions: SCHEDULED → IN_TRANSIT → DELIVERED/PARTIALLY_DELIVERED → DELIVERED.",
)
async def update_delivery_status(
    delivery_id: uuid.UUID,
    data: StatusUpdate,
    db: AsyncSession = Depends(get_db),
):
    return await DeliveryService(db).update_status(delivery_id, data)


# ═══════════════════════════════════════════════════════════════════════════════
#  FAT TESTS  (W11: Factory Acceptance Testing)
# ═══════════════════════════════════════════════════════════════════════════════

@router.post(
    "/fat-tests",
    response_model=FATTestResponse,
    status_code=201,
    summary="Schedule FAT",
    description="Schedule a Factory Acceptance Test for a PO/vendor. Auto-triggered T-14 days before expected delivery.",
)
async def create_fat_test(
    data: FATTestCreate, db: AsyncSession = Depends(get_db)
):
    return await FATTestService(db).create_test(data)


@router.get(
    "/fat-tests",
    response_model=PaginatedResponse,
    summary="List FAT Tests",
    description="Paginated FAT listing with optional PO, vendor, and status filters.",
)
async def list_fat_tests(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    po_id: Optional[uuid.UUID] = Query(None),
    vendor_id: Optional[uuid.UUID] = Query(None),
    status: Optional[str] = Query(None, description="Filter by FATStatus"),
    db: AsyncSession = Depends(get_db),
):
    return await FATTestService(db).list_tests(
        page=page, page_size=page_size,
        po_id=po_id, vendor_id=vendor_id, status_filter=status,
    )


@router.get(
    "/fat-tests/{fat_id}",
    response_model=FATTestResponse,
    summary="Get FAT Test",
    description="Retrieve a single FAT test by ID.",
)
async def get_fat_test(
    fat_id: uuid.UUID, db: AsyncSession = Depends(get_db)
):
    return await FATTestService(db).get_test(fat_id)


@router.put(
    "/fat-tests/{fat_id}",
    response_model=FATTestResponse,
    summary="Update FAT Test",
    description="Update FAT test details (dates, inspector, location, report URL).",
)
async def update_fat_test(
    fat_id: uuid.UUID,
    data: FATTestUpdate,
    db: AsyncSession = Depends(get_db),
):
    return await FATTestService(db).update_test(fat_id, data)


@router.patch(
    "/fat-tests/{fat_id}/status",
    response_model=FATTestResponse,
    summary="Update FAT Status",
    description="Transition FAT status. Valid lifecycle: SCHEDULED → NOTICE_SENT → IN_PROGRESS → PASSED/FAILED/CONDITIONALLY_PASSED. FAILED can move to RETEST_SCHEDULED → IN_PROGRESS again.",
)
async def update_fat_status(
    fat_id: uuid.UUID,
    data: StatusUpdate,
    db: AsyncSession = Depends(get_db),
):
    return await FATTestService(db).update_status(fat_id, data)


# ═══════════════════════════════════════════════════════════════════════════════
#  INDENTS (Material Requisition)
# ═══════════════════════════════════════════════════════════════════════════════

@router.post(
    "/indents",
    response_model=IndentResponse,
    status_code=201,
    summary="Create Indent",
    description="Create a new material requisition (Step 1).",
)
async def create_indent(
    data: IndentCreate, db: AsyncSession = Depends(get_db)
):
    return await IndentService(db).create_indent(data)


@router.get(
    "/indents",
    response_model=PaginatedResponse,
    summary="List Indents",
    description="Paginated indent listing with status filter.",
)
async def list_indents(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[str] = Query(None, description="Filter by IndentStatus"),
    db: AsyncSession = Depends(get_db),
):
    return await IndentService(db).list_indents(
        page=page, page_size=page_size, status_filter=status
    )


@router.get(
    "/indents/{indent_id}",
    response_model=IndentResponse,
    summary="Get Indent",
    description="Retrieve a single indent with items.",
)
async def get_indent(
    indent_id: uuid.UUID, db: AsyncSession = Depends(get_db)
):
    return await IndentService(db).get_indent(indent_id)


@router.patch(
    "/indents/{indent_id}/status",
    response_model=IndentResponse,
    summary="Update Indent Status",
    description="Transition indent status (Step 2-4 approval flow).",
)
async def update_indent_status(
    indent_id: uuid.UUID,
    data: StatusUpdate,
    db: AsyncSession = Depends(get_db),
):
    return await IndentService(db).update_status(indent_id, data)


# ═══════════════════════════════════════════════════════════════════════════════
#  MATERIAL SCHEDULE LINKS
# ═══════════════════════════════════════════════════════════════════════════════

@router.post(
    "/schedule-links",
    response_model=MaterialScheduleLinkResponse,
    status_code=201,
    summary="Link Material to Schedule",
    description="Bridge an activity's material need to the procurement timeline (Expert A09).",
)
async def create_schedule_link(
    data: MaterialScheduleLinkCreate, db: AsyncSession = Depends(get_db)
):
    return await MaterialScheduleLinkService(db).create_link(data)


@router.get(
    "/activities/{activity_id}/material-links",
    response_model=list[MaterialScheduleLinkResponse],
    summary="Get Material Links for Activity",
    description="Retrieve all materials linked to a specific schedule activity.",
)
async def get_activity_material_links(
    activity_id: uuid.UUID, db: AsyncSession = Depends(get_db)
):
    return await MaterialScheduleLinkService(db).get_links_for_activity(activity_id)


# ═══════════════════════════════════════════════════════════════════════════════
#  LEGACY ENDPOINTS (backward compatibility)
# ═══════════════════════════════════════════════════════════════════════════════

@router.post(
    "/orders",
    response_model=ProcurementOrderResponse,
    summary="[Legacy] Create Order",
    description="Legacy endpoint. Use /purchase-orders for new integrations.",
    deprecated=True,
)
async def create_order(
    request: ProcurementOrderCreate, db: AsyncSession = Depends(get_db)
):
    return await ProcurementService(db).create_order(request)


@router.get(
    "/orders",
    summary="[Legacy] List Orders",
    description="Legacy endpoint. Use /purchase-orders for new integrations.",
    deprecated=True,
)
async def list_orders(db: AsyncSession = Depends(get_db)):
    return await ProcurementService(db).list_orders()
