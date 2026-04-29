"""
Procurement Services — Business logic layer.

Services orchestrate repository calls, enforce business rules (e.g. PO state
machine transitions, vendor score calculation), and return domain objects.
"""

from __future__ import annotations

import uuid
import math
from decimal import Decimal
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.enums import POStatus, FATStatus, DeliveryStatus
from app.modules.procurement.repositories.repository import (
    VendorRepository, MaterialRepository, PurchaseOrderRepository,
    DeliveryRepository, FATTestRepository, VendorScoreRepository,
    ProcurementRepository,
)
from app.modules.procurement.dtos.dtos import (
    VendorCreate, VendorUpdate,
    MaterialCreate, MaterialUpdate,
    PurchaseOrderCreate, PurchaseOrderUpdate, StatusUpdate,
    DeliveryCreate, DeliveryUpdate,
    FATTestCreate, FATTestUpdate,
    VendorScoreCreate,
    ProcurementDashboard, PaginatedResponse,
)


# ── Valid PO status transitions (state machine) ──────────────────────────────

PO_TRANSITIONS: dict[str, list[str]] = {
    POStatus.DRAFT:                 [POStatus.PENDING_APPROVAL, POStatus.CANCELLED],
    POStatus.PENDING_APPROVAL:      [POStatus.APPROVED, POStatus.REJECTED, POStatus.CANCELLED],
    POStatus.APPROVED:              [POStatus.DISPATCHED, POStatus.CANCELLED],
    POStatus.DISPATCHED:            [POStatus.ACKNOWLEDGED],
    POStatus.ACKNOWLEDGED:          [POStatus.PARTIALLY_DELIVERED, POStatus.DELIVERED],
    POStatus.PARTIALLY_DELIVERED:   [POStatus.DELIVERED],
    POStatus.DELIVERED:             [POStatus.UNDER_INSPECTION, POStatus.CLOSED],
    POStatus.UNDER_INSPECTION:      [POStatus.CLOSED],
    POStatus.CLOSED:                [],
    POStatus.CANCELLED:             [],
}

# Vendor score weights per design doc
SCORE_WEIGHTS = {
    "quality": Decimal("0.35"),
    "delivery": Decimal("0.30"),
    "compliance": Decimal("0.20"),
    "price": Decimal("0.15"),
}


# ═══════════════════════════════════════════════════════════════════════════════
# Vendor Service
# ═══════════════════════════════════════════════════════════════════════════════

class VendorService:
    def __init__(self, db: AsyncSession):
        self.repo = VendorRepository(db)

    async def create_vendor(self, data: VendorCreate):
        return await self.repo.create(**data.model_dump())

    async def get_vendor(self, vendor_id: uuid.UUID):
        vendor = await self.repo.get_by_id(vendor_id)
        if not vendor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Vendor {vendor_id} not found",
            )
        return vendor

    async def list_vendors(
        self,
        page: int = 1,
        page_size: int = 20,
        vendor_status: Optional[str] = None,
        is_active: Optional[bool] = None,
    ) -> PaginatedResponse:
        skip = (page - 1) * page_size
        vendors, total = await self.repo.get_all(
            skip=skip, limit=page_size, status=vendor_status, is_active=is_active
        )
        return PaginatedResponse(
            items=vendors,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=math.ceil(total / page_size) if page_size else 0,
        )

    async def update_vendor(self, vendor_id: uuid.UUID, data: VendorUpdate):
        updated = await self.repo.update(
            vendor_id, **data.model_dump(exclude_unset=True)
        )
        if not updated:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Vendor {vendor_id} not found",
            )
        return updated

    async def delete_vendor(self, vendor_id: uuid.UUID):
        deleted = await self.repo.delete(vendor_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Vendor {vendor_id} not found",
            )
        return {"detail": "Vendor deleted successfully"}


# ═══════════════════════════════════════════════════════════════════════════════
# Material Service
# ═══════════════════════════════════════════════════════════════════════════════

class MaterialService:
    def __init__(self, db: AsyncSession):
        self.repo = MaterialRepository(db)

    async def create_material(self, data: MaterialCreate):
        return await self.repo.create(**data.model_dump())

    async def get_material(self, material_id: uuid.UUID):
        material = await self.repo.get_by_id(material_id)
        if not material:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Material {material_id} not found",
            )
        return material

    async def list_materials(
        self,
        page: int = 1,
        page_size: int = 20,
        category: Optional[str] = None,
        is_active: Optional[bool] = None,
    ) -> PaginatedResponse:
        skip = (page - 1) * page_size
        materials, total = await self.repo.get_all(
            skip=skip, limit=page_size, category=category, is_active=is_active
        )
        return PaginatedResponse(
            items=materials,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=math.ceil(total / page_size) if page_size else 0,
        )

    async def update_material(self, material_id: uuid.UUID, data: MaterialUpdate):
        updated = await self.repo.update(
            material_id, **data.model_dump(exclude_unset=True)
        )
        if not updated:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Material {material_id} not found",
            )
        return updated


# ═══════════════════════════════════════════════════════════════════════════════
# Purchase Order Service
# ═══════════════════════════════════════════════════════════════════════════════

class PurchaseOrderService:
    def __init__(self, db: AsyncSession):
        self.repo = PurchaseOrderRepository(db)
        self.db = db

    async def create_po(self, data: PurchaseOrderCreate):
        line_items = [item.model_dump() for item in data.line_items]
        po_data = data.model_dump(exclude={"line_items"})
        return await self.repo.create(line_items_data=line_items, **po_data)

    async def get_po(self, po_id: uuid.UUID):
        po = await self.repo.get_by_id(po_id)
        if not po:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Purchase Order {po_id} not found",
            )
        return po

    async def list_pos(
        self,
        page: int = 1,
        page_size: int = 20,
        po_status: Optional[str] = None,
        vendor_id: Optional[uuid.UUID] = None,
    ) -> PaginatedResponse:
        skip = (page - 1) * page_size
        pos, total = await self.repo.get_all(
            skip=skip, limit=page_size, status=po_status, vendor_id=vendor_id
        )
        return PaginatedResponse(
            items=pos,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=math.ceil(total / page_size) if page_size else 0,
        )

    async def update_po(self, po_id: uuid.UUID, data: PurchaseOrderUpdate):
        updated = await self.repo.update(
            po_id, **data.model_dump(exclude_unset=True)
        )
        if not updated:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Purchase Order {po_id} not found",
            )
        return updated

    async def update_po_status(self, po_id: uuid.UUID, data: StatusUpdate):
        """Enforce the PO state machine. Only valid transitions are allowed."""
        po = await self.repo.get_by_id(po_id)
        if not po:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Purchase Order {po_id} not found",
            )

        current = po.status
        target = data.status

        # Validate transition
        allowed = PO_TRANSITIONS.get(current, [])
        if target not in allowed:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"Invalid status transition: {current} → {target}. "
                    f"Allowed transitions from {current}: {allowed}"
                ),
            )

        return await self.repo.update_status(po_id, target)


# ═══════════════════════════════════════════════════════════════════════════════
# Delivery Service
# ═══════════════════════════════════════════════════════════════════════════════

class DeliveryService:
    def __init__(self, db: AsyncSession):
        self.repo = DeliveryRepository(db)

    async def create_delivery(self, data: DeliveryCreate):
        items = [item.model_dump() for item in data.items]
        delivery_data = data.model_dump(exclude={"items"})
        return await self.repo.create(items_data=items, **delivery_data)

    async def get_delivery(self, delivery_id: uuid.UUID):
        delivery = await self.repo.get_by_id(delivery_id)
        if not delivery:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Delivery {delivery_id} not found",
            )
        return delivery

    async def list_deliveries(
        self,
        page: int = 1,
        page_size: int = 20,
        po_id: Optional[uuid.UUID] = None,
        delivery_status: Optional[str] = None,
    ) -> PaginatedResponse:
        skip = (page - 1) * page_size
        deliveries, total = await self.repo.get_all(
            skip=skip, limit=page_size, po_id=po_id, status=delivery_status
        )
        return PaginatedResponse(
            items=deliveries,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=math.ceil(total / page_size) if page_size else 0,
        )

    async def update_delivery(self, delivery_id: uuid.UUID, data: DeliveryUpdate):
        updated = await self.repo.update(
            delivery_id, **data.model_dump(exclude_unset=True)
        )
        if not updated:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Delivery {delivery_id} not found",
            )
        return updated

    async def update_delivery_status(self, delivery_id: uuid.UUID, data: StatusUpdate):
        updated = await self.repo.update_status(delivery_id, data.status)
        if not updated:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Delivery {delivery_id} not found",
            )
        return updated


# ═══════════════════════════════════════════════════════════════════════════════
# FAT Test Service
# ═══════════════════════════════════════════════════════════════════════════════

class FATTestService:
    def __init__(self, db: AsyncSession):
        self.repo = FATTestRepository(db)

    async def create_fat(self, data: FATTestCreate):
        return await self.repo.create(**data.model_dump())

    async def get_fat(self, fat_id: uuid.UUID):
        fat = await self.repo.get_by_id(fat_id)
        if not fat:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"FAT Test {fat_id} not found",
            )
        return fat

    async def list_fats(
        self,
        page: int = 1,
        page_size: int = 20,
        po_id: Optional[uuid.UUID] = None,
        vendor_id: Optional[uuid.UUID] = None,
        fat_status: Optional[str] = None,
    ) -> PaginatedResponse:
        skip = (page - 1) * page_size
        fats, total = await self.repo.get_all(
            skip=skip, limit=page_size,
            po_id=po_id, vendor_id=vendor_id, status=fat_status,
        )
        return PaginatedResponse(
            items=fats,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=math.ceil(total / page_size) if page_size else 0,
        )

    async def update_fat_status(self, fat_id: uuid.UUID, data: StatusUpdate):
        updated = await self.repo.update_status(fat_id, data.status)
        if not updated:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"FAT Test {fat_id} not found",
            )
        return updated

    async def update_fat(self, fat_id: uuid.UUID, data: FATTestUpdate):
        fat = await self.repo.get_by_id(fat_id)
        if not fat:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"FAT Test {fat_id} not found",
            )
        update_data = data.model_dump(exclude_unset=True)
        return await self.repo.update_status(
            fat_id, fat.status, **update_data
        )


# ═══════════════════════════════════════════════════════════════════════════════
# Vendor Score Service
# ═══════════════════════════════════════════════════════════════════════════════

class VendorScoreService:
    def __init__(self, db: AsyncSession):
        self.score_repo = VendorScoreRepository(db)
        self.vendor_repo = VendorRepository(db)

    async def add_score(self, data: VendorScoreCreate):
        # Calculate weighted overall score
        overall = (
            data.quality_score * SCORE_WEIGHTS["quality"]
            + data.delivery_score * SCORE_WEIGHTS["delivery"]
            + data.compliance_score * SCORE_WEIGHTS["compliance"]
            + data.price_score * SCORE_WEIGHTS["price"]
        ).quantize(Decimal("0.01"))

        score = await self.score_repo.create(
            **data.model_dump(),
            overall_score=overall,
        )

        # Update vendor's current overall_score and tier
        tier = "TIER_1" if overall >= 80 else "TIER_2" if overall >= 60 else "TIER_3"
        await self.vendor_repo.update(
            data.vendor_id,
            overall_score=overall,
            vendor_tier=tier,
        )

        return score

    async def get_vendor_scores(
        self,
        vendor_id: uuid.UUID,
        page: int = 1,
        page_size: int = 20,
    ):
        # Verify vendor exists
        vendor = await self.vendor_repo.get_by_id(vendor_id)
        if not vendor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Vendor {vendor_id} not found",
            )
        skip = (page - 1) * page_size
        return await self.score_repo.get_by_vendor(
            vendor_id, skip=skip, limit=page_size
        )


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
        po_by_status = await self.po_repo.count_by_status()
        total_po = sum(po_by_status.values())
        total_value = await self.po_repo.total_value()
        total_vendors = await self.vendor_repo.count()
        active_vendors = await self.vendor_repo.count(is_active=True)
        total_materials = await self.material_repo.count()
        pending_deliveries = await self.delivery_repo.count_pending()
        upcoming_fats = await self.fat_repo.count_upcoming()

        return ProcurementDashboard(
            total_purchase_orders=total_po,
            po_by_status=po_by_status,
            total_vendors=total_vendors,
            active_vendors=active_vendors,
            total_materials=total_materials,
            pending_deliveries=pending_deliveries,
            upcoming_fat_tests=upcoming_fats,
            total_procurement_value=total_value,
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
