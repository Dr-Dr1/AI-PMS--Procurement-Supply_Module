"""
Procurement Repositories — Data access layer.

Each repository encapsulates all DB operations for its domain entity.
Uses SQLAlchemy async sessions throughout.
"""

from __future__ import annotations

import uuid
from decimal import Decimal
from typing import Optional

from sqlalchemy import select, func, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.procurement import (
    Vendor, Material, PurchaseOrder, POLineItem,
    Delivery, DeliveryItem, FATTest, VendorScoreHistory,
)
from app.models.models import ProcurementOrder


# ─── Vendor Repository ─────────────────────────────────────────────────────────

class VendorRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, **kwargs) -> Vendor:
        vendor = Vendor(**kwargs)
        self.db.add(vendor)
        await self.db.commit()
        await self.db.refresh(vendor)
        return vendor

    async def get_by_id(self, vendor_id: uuid.UUID) -> Optional[Vendor]:
        result = await self.db.execute(
            select(Vendor).where(Vendor.id == vendor_id)
        )
        return result.scalar_one_or_none()

    async def get_by_code(self, code: str) -> Optional[Vendor]:
        result = await self.db.execute(
            select(Vendor).where(Vendor.code == code)
        )
        return result.scalar_one_or_none()

    async def get_all(
        self,
        skip: int = 0,
        limit: int = 20,
        status: Optional[str] = None,
        is_active: Optional[bool] = None,
    ) -> tuple[list[Vendor], int]:
        query = select(Vendor)
        count_query = select(func.count(Vendor.id))

        if status:
            query = query.where(Vendor.vendor_status == status)
            count_query = count_query.where(Vendor.vendor_status == status)
        if is_active is not None:
            query = query.where(Vendor.is_active == is_active)
            count_query = count_query.where(Vendor.is_active == is_active)

        total = (await self.db.execute(count_query)).scalar() or 0
        result = await self.db.execute(
            query.order_by(Vendor.created_at.desc()).offset(skip).limit(limit)
        )
        return result.scalars().all(), total

    async def update(self, vendor_id: uuid.UUID, **kwargs) -> Optional[Vendor]:
        vendor = await self.get_by_id(vendor_id)
        if not vendor:
            return None
        for key, value in kwargs.items():
            if value is not None:
                setattr(vendor, key, value)
        await self.db.commit()
        await self.db.refresh(vendor)
        return vendor

    async def count(self, is_active: Optional[bool] = None) -> int:
        query = select(func.count(Vendor.id))
        if is_active is not None:
            query = query.where(Vendor.is_active == is_active)
        result = await self.db.execute(query)
        return result.scalar() or 0


# ─── Material Repository ───────────────────────────────────────────────────────

class MaterialRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, **kwargs) -> Material:
        material = Material(**kwargs)
        self.db.add(material)
        await self.db.commit()
        await self.db.refresh(material)
        return material

    async def get_by_id(self, material_id: uuid.UUID) -> Optional[Material]:
        result = await self.db.execute(
            select(Material).where(Material.id == material_id)
        )
        return result.scalar_one_or_none()

    async def get_by_code(self, code: str) -> Optional[Material]:
        result = await self.db.execute(
            select(Material).where(Material.code == code)
        )
        return result.scalar_one_or_none()

    async def get_all(
        self,
        skip: int = 0,
        limit: int = 20,
        category: Optional[str] = None,
        is_active: Optional[bool] = None,
    ) -> tuple[list[Material], int]:
        query = select(Material)
        count_query = select(func.count(Material.id))

        if category:
            query = query.where(Material.category == category)
            count_query = count_query.where(Material.category == category)
        if is_active is not None:
            query = query.where(Material.is_active == is_active)
            count_query = count_query.where(Material.is_active == is_active)

        total = (await self.db.execute(count_query)).scalar() or 0
        result = await self.db.execute(
            query.order_by(Material.created_at.desc()).offset(skip).limit(limit)
        )
        return result.scalars().all(), total

    async def update(self, material_id: uuid.UUID, **kwargs) -> Optional[Material]:
        material = await self.get_by_id(material_id)
        if not material:
            return None
        for key, value in kwargs.items():
            if value is not None:
                setattr(material, key, value)
        await self.db.commit()
        await self.db.refresh(material)
        return material

    async def count(self) -> int:
        result = await self.db.execute(select(func.count(Material.id)))
        return result.scalar() or 0


# ─── Purchase Order Repository ─────────────────────────────────────────────────

class PurchaseOrderRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, line_items_data: list[dict], **kwargs) -> PurchaseOrder:
        """Create PO with nested line items in a single transaction."""
        po = PurchaseOrder(**kwargs)

        # Calculate total and create line items
        total_value = Decimal("0")
        for item_data in line_items_data:
            item_total = item_data["quantity"] * item_data["unit_price"]
            line_item = POLineItem(
                **item_data,
                total_price=item_total,
            )
            po.line_items.append(line_item)
            total_value += item_total

        po.total_value = total_value
        self.db.add(po)
        await self.db.commit()
        await self.db.refresh(po)
        return po

    async def get_by_id(self, po_id: uuid.UUID) -> Optional[PurchaseOrder]:
        result = await self.db.execute(
            select(PurchaseOrder)
            .options(selectinload(PurchaseOrder.line_items))
            .where(PurchaseOrder.id == po_id)
        )
        return result.scalar_one_or_none()

    async def get_by_po_number(self, po_number: str) -> Optional[PurchaseOrder]:
        result = await self.db.execute(
            select(PurchaseOrder).where(PurchaseOrder.po_number == po_number)
        )
        return result.scalar_one_or_none()

    async def get_all(
        self,
        skip: int = 0,
        limit: int = 20,
        status: Optional[str] = None,
        vendor_id: Optional[uuid.UUID] = None,
    ) -> tuple[list[PurchaseOrder], int]:
        query = select(PurchaseOrder)
        count_query = select(func.count(PurchaseOrder.id))

        if status:
            query = query.where(PurchaseOrder.status == status)
            count_query = count_query.where(PurchaseOrder.status == status)
        if vendor_id:
            query = query.where(PurchaseOrder.vendor_id == vendor_id)
            count_query = count_query.where(PurchaseOrder.vendor_id == vendor_id)

        total = (await self.db.execute(count_query)).scalar() or 0
        result = await self.db.execute(
            query.order_by(PurchaseOrder.created_at.desc()).offset(skip).limit(limit)
        )
        return result.scalars().all(), total

    async def update(self, po_id: uuid.UUID, **kwargs) -> Optional[PurchaseOrder]:
        po = await self.get_by_id(po_id)
        if not po:
            return None
        for key, value in kwargs.items():
            if value is not None:
                setattr(po, key, value)
        await self.db.commit()
        await self.db.refresh(po)
        return po

    async def update_status(
        self, po_id: uuid.UUID, status: str, **extra
    ) -> Optional[PurchaseOrder]:
        po = await self.get_by_id(po_id)
        if not po:
            return None
        po.status = status
        for key, value in extra.items():
            if value is not None:
                setattr(po, key, value)
        await self.db.commit()
        await self.db.refresh(po)
        return po

    async def count(self, status: Optional[str] = None) -> int:
        query = select(func.count(PurchaseOrder.id))
        if status:
            query = query.where(PurchaseOrder.status == status)
        return (await self.db.execute(query)).scalar() or 0

    async def count_by_status(self) -> dict[str, int]:
        """Return {status: count} for all statuses with at least one PO."""
        result = await self.db.execute(
            select(PurchaseOrder.status, func.count(PurchaseOrder.id))
            .group_by(PurchaseOrder.status)
        )
        return {row[0]: row[1] for row in result.all()}

    async def total_value(self) -> Decimal:
        result = await self.db.execute(
            select(func.coalesce(func.sum(PurchaseOrder.total_value), 0))
        )
        return result.scalar() or Decimal("0")


# ─── Delivery Repository ───────────────────────────────────────────────────────

class DeliveryRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, items_data: list[dict], **kwargs) -> Delivery:
        delivery = Delivery(**kwargs)
        for item_data in items_data:
            delivery.items.append(DeliveryItem(**item_data))
        self.db.add(delivery)
        await self.db.commit()
        await self.db.refresh(delivery)
        return delivery

    async def get_by_id(self, delivery_id: uuid.UUID) -> Optional[Delivery]:
        result = await self.db.execute(
            select(Delivery)
            .options(selectinload(Delivery.items))
            .where(Delivery.id == delivery_id)
        )
        return result.scalar_one_or_none()

    async def get_all(
        self,
        skip: int = 0,
        limit: int = 20,
        po_id: Optional[uuid.UUID] = None,
        status: Optional[str] = None,
    ) -> tuple[list[Delivery], int]:
        query = select(Delivery)
        count_query = select(func.count(Delivery.id))

        if po_id:
            query = query.where(Delivery.po_id == po_id)
            count_query = count_query.where(Delivery.po_id == po_id)
        if status:
            query = query.where(Delivery.status == status)
            count_query = count_query.where(Delivery.status == status)

        total = (await self.db.execute(count_query)).scalar() or 0
        result = await self.db.execute(
            query.order_by(Delivery.created_at.desc()).offset(skip).limit(limit)
        )
        return result.scalars().all(), total

    async def update(self, delivery_id: uuid.UUID, **kwargs) -> Optional[Delivery]:
        delivery = await self.get_by_id(delivery_id)
        if not delivery:
            return None
        for key, value in kwargs.items():
            if value is not None:
                setattr(delivery, key, value)
        await self.db.commit()
        await self.db.refresh(delivery)
        return delivery

    async def update_status(
        self, delivery_id: uuid.UUID, status: str
    ) -> Optional[Delivery]:
        delivery = await self.get_by_id(delivery_id)
        if not delivery:
            return None
        delivery.status = status
        await self.db.commit()
        await self.db.refresh(delivery)
        return delivery

    async def count_pending(self) -> int:
        result = await self.db.execute(
            select(func.count(Delivery.id)).where(
                Delivery.status.in_(["SCHEDULED", "IN_TRANSIT"])
            )
        )
        return result.scalar() or 0


# ─── FAT Test Repository ───────────────────────────────────────────────────────

class FATTestRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, **kwargs) -> FATTest:
        fat = FATTest(**kwargs)
        self.db.add(fat)
        await self.db.commit()
        await self.db.refresh(fat)
        return fat

    async def get_by_id(self, fat_id: uuid.UUID) -> Optional[FATTest]:
        result = await self.db.execute(
            select(FATTest).where(FATTest.id == fat_id)
        )
        return result.scalar_one_or_none()

    async def get_all(
        self,
        skip: int = 0,
        limit: int = 20,
        po_id: Optional[uuid.UUID] = None,
        vendor_id: Optional[uuid.UUID] = None,
        status: Optional[str] = None,
    ) -> tuple[list[FATTest], int]:
        query = select(FATTest)
        count_query = select(func.count(FATTest.id))

        if po_id:
            query = query.where(FATTest.po_id == po_id)
            count_query = count_query.where(FATTest.po_id == po_id)
        if vendor_id:
            query = query.where(FATTest.vendor_id == vendor_id)
            count_query = count_query.where(FATTest.vendor_id == vendor_id)
        if status:
            query = query.where(FATTest.status == status)
            count_query = count_query.where(FATTest.status == status)

        total = (await self.db.execute(count_query)).scalar() or 0
        result = await self.db.execute(
            query.order_by(FATTest.created_at.desc()).offset(skip).limit(limit)
        )
        return result.scalars().all(), total

    async def update(self, fat_id: uuid.UUID, **kwargs) -> Optional[FATTest]:
        fat = await self.get_by_id(fat_id)
        if not fat:
            return None
        for key, value in kwargs.items():
            if value is not None:
                setattr(fat, key, value)
        await self.db.commit()
        await self.db.refresh(fat)
        return fat

    async def update_status(
        self, fat_id: uuid.UUID, status: str, **extra
    ) -> Optional[FATTest]:
        fat = await self.get_by_id(fat_id)
        if not fat:
            return None
        fat.status = status
        for key, value in extra.items():
            if value is not None:
                setattr(fat, key, value)
        await self.db.commit()
        await self.db.refresh(fat)
        return fat

    async def count_upcoming(self) -> int:
        """Count FAT tests that are scheduled but not yet completed."""
        result = await self.db.execute(
            select(func.count(FATTest.id)).where(
                FATTest.status.in_(["SCHEDULED", "NOTICE_SENT"])
            )
        )
        return result.scalar() or 0


# ─── Vendor Score History Repository ────────────────────────────────────────────

class VendorScoreRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, **kwargs) -> VendorScoreHistory:
        score = VendorScoreHistory(**kwargs)
        self.db.add(score)
        await self.db.commit()
        await self.db.refresh(score)
        return score

    async def get_by_vendor(
        self,
        vendor_id: uuid.UUID,
        skip: int = 0,
        limit: int = 20,
    ) -> list[VendorScoreHistory]:
        result = await self.db.execute(
            select(VendorScoreHistory)
            .where(VendorScoreHistory.vendor_id == vendor_id)
            .order_by(VendorScoreHistory.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()


# ─── Legacy Repository (backward compat) ───────────────────────────────────────

class ProcurementRepository:
    """Legacy repository for the original ProcurementOrder model."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, title: str) -> ProcurementOrder:
        obj = ProcurementOrder(title=title)
        self.db.add(obj)
        await self.db.commit()
        await self.db.refresh(obj)
        return obj

    async def get_all(self) -> list[ProcurementOrder]:
        result = await self.db.execute(select(ProcurementOrder))
        return result.scalars().all()
