from uuid import UUID
from datetime import date
from typing import Optional

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models_v2.procurement import PO, POLineItem
from app.core.enums import POStatus


class PORepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, data: dict) -> PO:
        po = PO(**data)
        self.db.add(po)
        await self.db.flush()
        await self.db.refresh(po)
        return po

    async def get_by_id(self, po_id: UUID) -> Optional[PO]:
        result = await self.db.execute(
            select(PO).where(PO.id == po_id)
        )
        return result.scalar_one_or_none()

    async def list_by_package(self, package_id: UUID, status: Optional[str] = None) -> list[PO]:
        today = date.today()
        # Auto-update overdue flag
        await self.db.execute(
            update(PO)
            .where(
                PO.package_id == package_id,
                PO.committed_delivery_date < today,
                PO.status.notin_([POStatus.CLOSED]),
            )
            .values(is_overdue=True)
        )
        await self.db.execute(
            update(PO)
            .where(
                PO.package_id == package_id,
                PO.status == POStatus.CLOSED,
            )
            .values(is_overdue=False)
        )
        q = select(PO).where(PO.package_id == package_id)
        if status:
            q = q.where(PO.status == status)
        result = await self.db.execute(q.order_by(PO.created_at.desc()))
        return list(result.scalars().all())

    async def update(self, po: PO, data: dict) -> PO:
        for key, val in data.items():
            if val is not None:
                setattr(po, key, val)
        await self.db.flush()
        await self.db.refresh(po)
        return po

    async def delete(self, po: PO) -> None:
        await self.db.delete(po)
        await self.db.flush()

    async def transition_status(self, po: PO, new_status: POStatus) -> PO:
        po.status = new_status
        if new_status == POStatus.CLOSED:
            po.is_overdue = False
        await self.db.flush()
        await self.db.refresh(po)
        return po

    # ── Line Items ──────────────────────────────────────────────────────────

    async def add_item(self, po_id: UUID, data: dict) -> POLineItem:
        item = POLineItem(po_id=po_id, **data)
        self.db.add(item)
        await self.db.flush()
        await self.db.refresh(item)
        return item

    async def get_items(self, po_id: UUID) -> list[POLineItem]:
        result = await self.db.execute(
            select(POLineItem).where(POLineItem.po_id == po_id)
        )
        return list(result.scalars().all())

    async def get_item(self, item_id: UUID) -> Optional[POLineItem]:
        result = await self.db.execute(
            select(POLineItem).where(POLineItem.id == item_id)
        )
        return result.scalar_one_or_none()

    async def update_item(self, item: POLineItem, data: dict) -> POLineItem:
        for key, val in data.items():
            if val is not None:
                setattr(item, key, val)
        item.amount = float(item.quantity) * float(item.unit_rate)
        await self.db.flush()
        await self.db.refresh(item)
        return item

    async def delete_item(self, item: POLineItem) -> None:
        await self.db.delete(item)
        await self.db.flush()

    async def recalc_total(self, po_id: UUID) -> None:
        items = await self.get_items(po_id)
        total = sum(float(i.amount) for i in items)
        await self.db.execute(
            update(PO).where(PO.id == po_id).values(total_amount=total)
        )
        await self.db.flush()
