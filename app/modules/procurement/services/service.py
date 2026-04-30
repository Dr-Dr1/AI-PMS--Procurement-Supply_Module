"""
Procurement Services — Business logic layer.

Orchestrates repository calls, applies validation rules, computes derived values.
Each service owns the business rules for its domain.
"""

from __future__ import annotations

import math
import uuid
from decimal import Decimal
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.procurement.repositories.repository import (
    VendorRepository, MaterialRepository, PurchaseOrderRepository,
    DeliveryRepository, FATTestRepository, VendorScoreRepository,
    ProcurementRepository,
)
from app.modules.procurement.dtos.dtos import (
    VendorCreate, VendorUpdate, VendorResponse, VendorListResponse,
    MaterialCreate, MaterialUpdate, MaterialResponse,
    PurchaseOrderCreate, PurchaseOrderUpdate, PurchaseOrderResponse,
    PurchaseOrderListResponse, StatusUpdate,
    DeliveryCreate, DeliveryUpdate, DeliveryResponse,
    FATTestCreate, FATTestUpdate, FATTestResponse,
    VendorScoreCreate, VendorScoreResponse,
    ProcurementDashboard, PaginatedResponse,
)
from app.core.enums import POStatus, DeliveryStatus, FATStatus


# ─── Valid state transitions ───────────────────────────────────────────────────

PO_TRANSITIONS: dict[str, set[str]] = {
    POStatus.DRAFT: {POStatus.PENDING_APPROVAL, POStatus.CANCELLED},
    POStatus.PENDING_APPROVAL: {POStatus.APPROVED, POStatus.CANCELLED},
    POStatus.APPROVED: {POStatus.DISPATCHED, POStatus.CANCELLED},
    POStatus.DISPATCHED: {POStatus.ACKNOWLEDGED},
    POStatus.ACKNOWLEDGED: {POStatus.PARTIALLY_DELIVERED, POStatus.DELIVERED},
    POStatus.PARTIALLY_DELIVERED: {POStatus.DELIVERED},
    POStatus.DELIVERED: {POStatus.UNDER_INSPECTION},
    POStatus.UNDER_INSPECTION: {POStatus.CLOSED},
    POStatus.CLOSED: set(),
    POStatus.CANCELLED: set(),
}

DELIVERY_TRANSITIONS: dict[str, set[str]] = {
    DeliveryStatus.SCHEDULED: {DeliveryStatus.IN_TRANSIT, DeliveryStatus.REJECTED},
    DeliveryStatus.IN_TRANSIT: {
        DeliveryStatus.DELIVERED,
        DeliveryStatus.PARTIALLY_DELIVERED,
        DeliveryStatus.REJECTED,
    },
    DeliveryStatus.PARTIALLY_DELIVERED: {DeliveryStatus.DELIVERED},
    DeliveryStatus.DELIVERED: set(),
    DeliveryStatus.REJECTED: set(),
}

FAT_TRANSITIONS: dict[str, set[str]] = {
    FATStatus.SCHEDULED: {FATStatus.NOTICE_SENT, FATStatus.CANCELLED
                          if hasattr(FATStatus, "CANCELLED") else FATStatus.SCHEDULED},
    FATStatus.NOTICE_SENT: {FATStatus.IN_PROGRESS},
    FATStatus.IN_PROGRESS: {
        FATStatus.PASSED, FATStatus.FAILED, FATStatus.CONDITIONALLY_PASSED,
    },
    FATStatus.FAILED: {FATStatus.RETEST_SCHEDULED},
    FATStatus.CONDITIONALLY_PASSED: {FATStatus.RETEST_SCHEDULED, FATStatus.PASSED},
    FATStatus.RETEST_SCHEDULED: {FATStatus.IN_PROGRESS},
    FATStatus.PASSED: set(),
}

# Vendor scoring weights per design doc
SCORE_WEIGHTS = {
    "quality": Decimal("0.35"),
    "delivery": Decimal("0.30"),
    "compliance": Decimal("0.20"),
    "price": Decimal("0.15"),
}


def _validate_transition(current: str, target: str, transitions: dict) -> None:
    """Raise 400 if the status transition is not allowed."""
    allowed = transitions.get(current, set())
    if target not in allowed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status transition: {current} → {target}. "
                   f"Allowed: {', '.join(sorted(allowed)) or 'none (terminal state)'}",
        )


# ═══════════════════════════════════════════════════════════════════════════════
# Vendor Service
# ═══════════════════════════════════════════════════════════════════════════════

class VendorService:
    def __init__(self, db: AsyncSession):
        self.repo = VendorRepository(db)

    async def create_vendor(self, data: VendorCreate) -> VendorResponse:
        existing = await self.repo.get_by_code(data.code)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Vendor with code '{data.code}' already exists.",
            )
        vendor = await self.repo.create(**data.model_dump())
        return VendorResponse.model_validate(vendor)

    async def get_vendor(self, vendor_id: uuid.UUID) -> VendorResponse:
        vendor = await self.repo.get_by_id(vendor_id)
        if not vendor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Vendor not found.",
            )
        return VendorResponse.model_validate(vendor)

    async def list_vendors(
        self,
        page: int = 1,
        page_size: int = 20,
        status_filter: Optional[str] = None,
        is_active: Optional[bool] = None,
    ) -> PaginatedResponse:
        skip = (page - 1) * page_size
        vendors, total = await self.repo.get_all(
            skip=skip, limit=page_size, status=status_filter, is_active=is_active,
        )
        return PaginatedResponse(
            items=[VendorListResponse.model_validate(v) for v in vendors],
            total=total,
            page=page,
            page_size=page_size,
            total_pages=math.ceil(total / page_size) if total else 0,
        )

    async def update_vendor(
        self, vendor_id: uuid.UUID, data: VendorUpdate
    ) -> VendorResponse:
        update_data = data.model_dump(exclude_unset=True)
        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No fields to update.",
            )
        vendor = await self.repo.update(vendor_id, **update_data)
        if not vendor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Vendor not found.",
            )
        return VendorResponse.model_validate(vendor)


# ═══════════════════════════════════════════════════════════════════════════════
# Material Service
# ═══════════════════════════════════════════════════════════════════════════════

class MaterialService:
    def __init__(self, db: AsyncSession):
        self.repo = MaterialRepository(db)

    async def create_material(self, data: MaterialCreate) -> MaterialResponse:
        existing = await self.repo.get_by_code(data.code)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Material with code '{data.code}' already exists.",
            )
        material = await self.repo.create(**data.model_dump())
        return MaterialResponse.model_validate(material)

    async def get_material(self, material_id: uuid.UUID) -> MaterialResponse:
        material = await self.repo.get_by_id(material_id)
        if not material:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Material not found.",
            )
        return MaterialResponse.model_validate(material)

    async def list_materials(
        self,
        page: int = 1,
        page_size: int = 20,
        category: Optional[str] = None,
        is_active: Optional[bool] = None,
    ) -> PaginatedResponse:
        skip = (page - 1) * page_size
        materials, total = await self.repo.get_all(
            skip=skip, limit=page_size, category=category, is_active=is_active,
        )
        return PaginatedResponse(
            items=[MaterialResponse.model_validate(m) for m in materials],
            total=total,
            page=page,
            page_size=page_size,
            total_pages=math.ceil(total / page_size) if total else 0,
        )

    async def update_material(
        self, material_id: uuid.UUID, data: MaterialUpdate
    ) -> MaterialResponse:
        update_data = data.model_dump(exclude_unset=True)
        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No fields to update.",
            )
        material = await self.repo.update(material_id, **update_data)
        if not material:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Material not found.",
            )
        return MaterialResponse.model_validate(material)


# ═══════════════════════════════════════════════════════════════════════════════
# Purchase Order Service
# ═══════════════════════════════════════════════════════════════════════════════

class PurchaseOrderService:
    def __init__(self, db: AsyncSession):
        self.repo = PurchaseOrderRepository(db)
        self.vendor_repo = VendorRepository(db)

    async def create_order(self, data: PurchaseOrderCreate) -> PurchaseOrderResponse:
        # Validate vendor exists
        vendor = await self.vendor_repo.get_by_id(data.vendor_id)
        if not vendor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Vendor not found.",
            )

        # Check PO number uniqueness
        existing = await self.repo.get_by_po_number(data.po_number)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"PO number '{data.po_number}' already exists.",
            )

        # Extract line items and main PO fields
        line_items_data = [item.model_dump() for item in data.line_items]
        po_fields = data.model_dump(exclude={"line_items"})

        po = await self.repo.create(line_items_data=line_items_data, **po_fields)
        return PurchaseOrderResponse.model_validate(po)

    async def get_order(self, po_id: uuid.UUID) -> PurchaseOrderResponse:
        po = await self.repo.get_by_id(po_id)
        if not po:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Purchase order not found.",
            )
        return PurchaseOrderResponse.model_validate(po)

    async def list_orders(
        self,
        page: int = 1,
        page_size: int = 20,
        status_filter: Optional[str] = None,
        vendor_id: Optional[uuid.UUID] = None,
    ) -> PaginatedResponse:
        skip = (page - 1) * page_size
        orders, total = await self.repo.get_all(
            skip=skip, limit=page_size, status=status_filter, vendor_id=vendor_id,
        )
        return PaginatedResponse(
            items=[PurchaseOrderListResponse.model_validate(o) for o in orders],
            total=total,
            page=page,
            page_size=page_size,
            total_pages=math.ceil(total / page_size) if total else 0,
        )

    async def update_order(
        self, po_id: uuid.UUID, data: PurchaseOrderUpdate
    ) -> PurchaseOrderResponse:
        # Only allow updates on DRAFT POs
        po = await self.repo.get_by_id(po_id)
        if not po:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Purchase order not found.",
            )
        if po.status != POStatus.DRAFT:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot update PO in '{po.status}' status. Only DRAFT POs can be edited.",
            )

        update_data = data.model_dump(exclude_unset=True)
        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No fields to update.",
            )
        po = await self.repo.update(po_id, **update_data)
        return PurchaseOrderResponse.model_validate(po)

    async def update_status(
        self, po_id: uuid.UUID, data: StatusUpdate
    ) -> PurchaseOrderResponse:
        po = await self.repo.get_by_id(po_id)
        if not po:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Purchase order not found.",
            )
        _validate_transition(po.status, data.status, PO_TRANSITIONS)

        extra = {}
        if data.remarks:
            extra["remarks"] = data.remarks

        po = await self.repo.update_status(po_id, data.status, **extra)
        return PurchaseOrderResponse.model_validate(po)


# ═══════════════════════════════════════════════════════════════════════════════
# Delivery Service
# ═══════════════════════════════════════════════════════════════════════════════

class DeliveryService:
    def __init__(self, db: AsyncSession):
        self.repo = DeliveryRepository(db)
        self.po_repo = PurchaseOrderRepository(db)

    async def create_delivery(self, data: DeliveryCreate) -> DeliveryResponse:
        # Validate PO exists
        po = await self.po_repo.get_by_id(data.po_id)
        if not po:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Purchase order not found.",
            )

        items_data = [item.model_dump() for item in data.items]
        delivery_fields = data.model_dump(exclude={"items"})

        delivery = await self.repo.create(items_data=items_data, **delivery_fields)
        return DeliveryResponse.model_validate(delivery)

    async def get_delivery(self, delivery_id: uuid.UUID) -> DeliveryResponse:
        delivery = await self.repo.get_by_id(delivery_id)
        if not delivery:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Delivery not found.",
            )
        return DeliveryResponse.model_validate(delivery)

    async def list_deliveries(
        self,
        page: int = 1,
        page_size: int = 20,
        po_id: Optional[uuid.UUID] = None,
        status_filter: Optional[str] = None,
    ) -> PaginatedResponse:
        skip = (page - 1) * page_size
        deliveries, total = await self.repo.get_all(
            skip=skip, limit=page_size, po_id=po_id, status=status_filter,
        )
        return PaginatedResponse(
            items=[DeliveryResponse.model_validate(d) for d in deliveries],
            total=total,
            page=page,
            page_size=page_size,
            total_pages=math.ceil(total / page_size) if total else 0,
        )

    async def update_delivery(
        self, delivery_id: uuid.UUID, data: DeliveryUpdate
    ) -> DeliveryResponse:
        update_data = data.model_dump(exclude_unset=True)
        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No fields to update.",
            )
        delivery = await self.repo.update(delivery_id, **update_data)
        if not delivery:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Delivery not found.",
            )
        return DeliveryResponse.model_validate(delivery)

    async def update_status(
        self, delivery_id: uuid.UUID, data: StatusUpdate
    ) -> DeliveryResponse:
        delivery = await self.repo.get_by_id(delivery_id)
        if not delivery:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Delivery not found.",
            )
        _validate_transition(delivery.status, data.status, DELIVERY_TRANSITIONS)

        delivery = await self.repo.update_status(delivery_id, data.status)
        return DeliveryResponse.model_validate(delivery)


# ═══════════════════════════════════════════════════════════════════════════════
# FAT Test Service
# ═══════════════════════════════════════════════════════════════════════════════

class FATTestService:
    def __init__(self, db: AsyncSession):
        self.repo = FATTestRepository(db)
        self.po_repo = PurchaseOrderRepository(db)
        self.vendor_repo = VendorRepository(db)

    async def create_test(self, data: FATTestCreate) -> FATTestResponse:
        # Validate PO and Vendor exist
        po = await self.po_repo.get_by_id(data.po_id)
        if not po:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Purchase order not found.",
            )
        vendor = await self.vendor_repo.get_by_id(data.vendor_id)
        if not vendor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Vendor not found.",
            )

        fat = await self.repo.create(**data.model_dump())
        return FATTestResponse.model_validate(fat)

    async def get_test(self, fat_id: uuid.UUID) -> FATTestResponse:
        fat = await self.repo.get_by_id(fat_id)
        if not fat:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="FAT test not found.",
            )
        return FATTestResponse.model_validate(fat)

    async def list_tests(
        self,
        page: int = 1,
        page_size: int = 20,
        po_id: Optional[uuid.UUID] = None,
        vendor_id: Optional[uuid.UUID] = None,
        status_filter: Optional[str] = None,
    ) -> PaginatedResponse:
        skip = (page - 1) * page_size
        tests, total = await self.repo.get_all(
            skip=skip, limit=page_size,
            po_id=po_id, vendor_id=vendor_id, status=status_filter,
        )
        return PaginatedResponse(
            items=[FATTestResponse.model_validate(t) for t in tests],
            total=total,
            page=page,
            page_size=page_size,
            total_pages=math.ceil(total / page_size) if total else 0,
        )

    async def update_test(
        self, fat_id: uuid.UUID, data: FATTestUpdate
    ) -> FATTestResponse:
        update_data = data.model_dump(exclude_unset=True)
        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No fields to update.",
            )
        fat = await self.repo.update(fat_id, **update_data)
        if not fat:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="FAT test not found.",
            )
        return FATTestResponse.model_validate(fat)

    async def update_status(
        self, fat_id: uuid.UUID, data: StatusUpdate
    ) -> FATTestResponse:
        fat = await self.repo.get_by_id(fat_id)
        if not fat:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="FAT test not found.",
            )
        _validate_transition(fat.status, data.status, FAT_TRANSITIONS)

        extra = {}
        if data.remarks:
            extra["remarks"] = data.remarks

        fat = await self.repo.update_status(fat_id, data.status, **extra)
        return FATTestResponse.model_validate(fat)


# ═══════════════════════════════════════════════════════════════════════════════
# Vendor Score Service
# ═══════════════════════════════════════════════════════════════════════════════

class VendorScoreService:
    def __init__(self, db: AsyncSession):
        self.repo = VendorScoreRepository(db)
        self.vendor_repo = VendorRepository(db)

    async def add_score(self, data: VendorScoreCreate) -> VendorScoreResponse:
        # Validate vendor exists
        vendor = await self.vendor_repo.get_by_id(data.vendor_id)
        if not vendor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Vendor not found.",
            )

        # Compute weighted overall score
        overall = (
            data.quality_score * SCORE_WEIGHTS["quality"]
            + data.delivery_score * SCORE_WEIGHTS["delivery"]
            + data.compliance_score * SCORE_WEIGHTS["compliance"]
            + data.price_score * SCORE_WEIGHTS["price"]
        )

        score_data = data.model_dump()
        score_data["overall_score"] = overall.quantize(Decimal("0.01"))

        score = await self.repo.create(**score_data)

        # Update vendor's overall_score and tier
        tier = "TIER_1" if overall >= 80 else ("TIER_2" if overall >= 60 else "TIER_3")
        await self.vendor_repo.update(
            data.vendor_id,
            overall_score=overall.quantize(Decimal("0.01")),
            vendor_tier=tier,
        )

        return VendorScoreResponse.model_validate(score)

    async def get_scores(
        self, vendor_id: uuid.UUID, page: int = 1, page_size: int = 20
    ) -> list[VendorScoreResponse]:
        vendor = await self.vendor_repo.get_by_id(vendor_id)
        if not vendor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Vendor not found.",
            )
        skip = (page - 1) * page_size
        scores = await self.repo.get_by_vendor(vendor_id, skip=skip, limit=page_size)
        return [VendorScoreResponse.model_validate(s) for s in scores]


# ═══════════════════════════════════════════════════════════════════════════════
# Dashboard Service
# ═══════════════════════════════════════════════════════════════════════════════

class DashboardService:
    def __init__(self, db: AsyncSession):
        self.po_repo = PurchaseOrderRepository(db)
        self.vendor_repo = VendorRepository(db)
        self.material_repo = MaterialRepository(db)
        self.delivery_repo = DeliveryRepository(db)
        self.fat_repo = FATTestRepository(db)

    async def get_summary(self) -> ProcurementDashboard:
        return ProcurementDashboard(
            total_purchase_orders=await self.po_repo.count(),
            po_by_status=await self.po_repo.count_by_status(),
            total_vendors=await self.vendor_repo.count(),
            active_vendors=await self.vendor_repo.count(is_active=True),
            total_materials=await self.material_repo.count(),
            pending_deliveries=await self.delivery_repo.count_pending(),
            upcoming_fat_tests=await self.fat_repo.count_upcoming(),
            total_procurement_value=await self.po_repo.total_value(),
        )


# ═══════════════════════════════════════════════════════════════════════════════
# Legacy Service (backward compat)
# ═══════════════════════════════════════════════════════════════════════════════

class ProcurementService:
    def __init__(self, db: AsyncSession):
        self.repo = ProcurementRepository(db)

    async def create_order(self, data):
        return await self.repo.create(data.title)

    async def list_orders(self):
        return await self.repo.get_all()
