"""
Procurement Repositories — Data access layer.

Each repository encapsulates all database operations for its domain entity.
All queries use SQLAlchemy async patterns with the session injected via DI.
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


# ═══════════════════════════════════════════════════════════════════════════════
# Vendor Repository
# ═══════════════════════════════════════════════════════════════════════════════

class VendorRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, **kwargs) -> Vendor:
        vendor = Vendor(**kwargs)
        self.db.add(vendor)
        await self.db.commit()
        await self.db.refresh(vendor)
        return vendor

    async def get_by_id(self, vendor_id: uuid.UUID) -> Vendor | None:
        result = await self.db.execute(
            select(Vendor).where(Vendor.id == vendor_id)
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

        total = (await self.db.execute(count_query)).scalar()
        result = await self.db.execute(
            query.order_by(Vendor.created_at.desc()).offset(skip).limit(limit)
        )
        return result.scalars().all(), total

    async def update(self, vendor_id: uuid.UUID, **kwargs) -> Vendor | None:
        vendor = await self.get_by_id(vendor_id)
        if not vendor:
            return None
        for key, value in kwargs.items():
            if value is not None:
                setattr(vendor, key, value)
        await self.db.commit()
        await self.db.refresh(vendor)
        return vendor

    async def delete(self, vendor_id: uuid.UUID) -> bool:
        vendor = await self.get_by_id(vendor_id)
        if not vendor:
            return False
        await self.db.delete(vendor)
        await self.db.commit()
        return True

    async def count(self, is_active: Optional[bool] = None) -> int:
        query = select(func.count(Vendor.id))
        if is_active is not None:
            query = query.where(Vendor.is_active == is_active)
        result = await self.db.execute(query)
        return result.scalar()


# ═══════════════════════════════════════════════════════════════════════════════
# Material Repository
# ═══════════════════════════════════════════════════════════════════════════════

class MaterialRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, **kwargs) -> Material:
        material = Material(**kwargs)
        self.db.add(material)
        await self.db.commit()
        await self.db.refresh(material)
        return material

    async def get_by_id(self, material_id: uuid.UUID) -> Material | None:
        result = await self.db.execute(
            select(Material).where(Material.id == material_id)
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

        total = (await self.db.execute(count_query)).scalar()
        result = await self.db.execute(
            query.order_by(Material.created_at.desc()).offset(skip).limit(limit)
        )
        return result.scalars().all(), total

    async def update(self, material_id: uuid.UUID, **kwargs) -> Material | None:
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
        return result.scalar()


# ═══════════════════════════════════════════════════════════════════════════════
# Purchase Order Repository
# ═══════════════════════════════════════════════════════════════════════════════

class PurchaseOrderRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, line_items_data: list[dict] | None = None, **kwargs) -> PurchaseOrder:
        po = PurchaseOrder(**kwargs)
        self.db.add(po)
        await self.db.flush()  # Get the PO id before adding line items

        total_value = Decimal("0.00")
        if line_items_data:
            for item_data in line_items_data:
                item_total = item_data["quantity"] * item_data["unit_price"]
                line_item = POLineItem(
                    po_id=po.id,
                    material_id=item_data["material_id"],
                    description=item_data.get("description"),
                    quantity=item_data["quantity"],
                    unit_price=item_data["unit_price"],
                    total_price=item_total,
                    unit=item_data["unit"],
                )
                self.db.add(line_item)
                total_value += item_total

        po.total_value = total_value
        await self.db.commit()
        await self.db.refresh(po)
        return po

    async def get_by_id(self, po_id: uuid.UUID) -> PurchaseOrder | None:
        result = await self.db.execute(
            select(PurchaseOrder)
            .options(selectinload(PurchaseOrder.line_items))
            .where(PurchaseOrder.id == po_id)
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

        total = (await self.db.execute(count_query)).scalar()
        result = await self.db.execute(
            query.order_by(PurchaseOrder.created_at.desc()).offset(skip).limit(limit)
        )
        return result.scalars().all(), total

    async def update(self, po_id: uuid.UUID, **kwargs) -> PurchaseOrder | None:
        po = await self.get_by_id(po_id)
        if not po:
            return None
        for key, value in kwargs.items():
            if value is not None:
                setattr(po, key, value)
        await self.db.commit()
        await self.db.refresh(po)
        return po

    async def update_status(self, po_id: uuid.UUID, status: str) -> PurchaseOrder | None:
        po = await self.get_by_id(po_id)
        if not po:
            return None
        po.status = status
        await self.db.commit()
        await self.db.refresh(po)
        return po

    async def count_by_status(self) -> dict[str, int]:
        result = await self.db.execute(
            select(PurchaseOrder.status, func.count(PurchaseOrder.id))
            .group_by(PurchaseOrder.status)
        )
        return {row[0]: row[1] for row in result.all()}

    async def total_value(self) -> Decimal:
        result = await self.db.execute(
            select(func.coalesce(func.sum(PurchaseOrder.total_value), 0))
        )
        return result.scalar()


# ═══════════════════════════════════════════════════════════════════════════════
# Delivery Repository
# ═══════════════════════════════════════════════════════════════════════════════

class DeliveryRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, items_data: list[dict] | None = None, **kwargs) -> Delivery:
        delivery = Delivery(**kwargs)
        self.db.add(delivery)
        await self.db.flush()

        if items_data:
            for item_data in items_data:
                item = DeliveryItem(
                    delivery_id=delivery.id,
                    po_line_item_id=item_data["po_line_item_id"],
                    delivered_quantity=item_data["delivered_quantity"],
                    accepted_quantity=item_data.get("accepted_quantity", 0),
                    rejected_quantity=item_data.get("rejected_quantity", 0),
                    rejection_reason=item_data.get("rejection_reason"),
                )
                self.db.add(item)

        await self.db.commit()
        await self.db.refresh(delivery)
        return delivery

    async def get_by_id(self, delivery_id: uuid.UUID) -> Delivery | None:
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

        total = (await self.db.execute(count_query)).scalar()
        result = await self.db.execute(
            query.order_by(Delivery.created_at.desc()).offset(skip).limit(limit)
        )
        return result.scalars().all(), total

    async def update_status(self, delivery_id: uuid.UUID, status: str) -> Delivery | None:
        delivery = await self.get_by_id(delivery_id)
        if not delivery:
            return None
        delivery.status = status
        await self.db.commit()
        await self.db.refresh(delivery)
        return delivery

    async def update(self, delivery_id: uuid.UUID, **kwargs) -> Delivery | None:
        delivery = await self.get_by_id(delivery_id)
        if not delivery:
            return None
        for key, value in kwargs.items():
            if value is not None:
                setattr(delivery, key, value)
        await self.db.commit()
        await self.db.refresh(delivery)
        return delivery

    async def count_pending(self) -> int:
        result = await self.db.execute(
            select(func.count(Delivery.id)).where(
                Delivery.status.in_(["SCHEDULED", "IN_TRANSIT"])
            )
        )
        return result.scalar()


# ═══════════════════════════════════════════════════════════════════════════════
# FAT Test Repository
# ═══════════════════════════════════════════════════════════════════════════════

class FATTestRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, **kwargs) -> FATTest:
        fat = FATTest(**kwargs)
        self.db.add(fat)
        await self.db.commit()
        await self.db.refresh(fat)
        return fat

    async def get_by_id(self, fat_id: uuid.UUID) -> FATTest | None:
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

        total = (await self.db.execute(count_query)).scalar()
        result = await self.db.execute(
            query.order_by(FATTest.scheduled_date.desc()).offset(skip).limit(limit)
        )
        return result.scalars().all(), total

    async def update_status(self, fat_id: uuid.UUID, status: str, **kwargs) -> FATTest | None:
        fat = await self.get_by_id(fat_id)
        if not fat:
            return None
        fat.status = status
        for key, value in kwargs.items():
            if value is not None:
                setattr(fat, key, value)
        await self.db.commit()
        await self.db.refresh(fat)
        return fat

    async def count_upcoming(self) -> int:
        result = await self.db.execute(
            select(func.count(FATTest.id)).where(
                FATTest.status.in_(["SCHEDULED", "NOTICE_SENT"])
            )
        )
        return result.scalar()


# ═══════════════════════════════════════════════════════════════════════════════
# Vendor Score History Repository
# ═══════════════════════════════════════════════════════════════════════════════

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


# ═══════════════════════════════════════════════════════════════════════════════
# Legacy Repository (backward compat)
# ═══════════════════════════════════════════════════════════════════════════════

class ProcurementRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, title: str) -> ProcurementOrder:
        obj = ProcurementOrder(title=title)
        self.db.add(obj)
        await self.db.commit()
        await self.db.refresh(obj)
        return obj

    async def get_all(self) -> list[ProcurementOrder]:
        r = await self.db.execute(select(ProcurementOrder))
        return r.scalars().all()
