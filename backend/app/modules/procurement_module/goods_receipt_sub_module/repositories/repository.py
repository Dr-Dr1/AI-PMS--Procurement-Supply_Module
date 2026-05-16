from uuid import UUID
from typing import Optional
from datetime import date

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models_v2.procurement import GoodsReceipt


class GRNRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, data: dict) -> GoodsReceipt:
        grn = GoodsReceipt(**data)
        self.db.add(grn)
        await self.db.flush()
        await self.db.refresh(grn)
        return grn

    async def get_by_id(self, grn_id: UUID) -> Optional[GoodsReceipt]:
        result = await self.db.execute(
            select(GoodsReceipt).where(GoodsReceipt.id == grn_id)
        )
        return result.scalar_one_or_none()

    async def list_by_package(
        self,
        package_id: UUID,
        po_id: Optional[UUID] = None,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
    ) -> list[GoodsReceipt]:
        q = select(GoodsReceipt).where(GoodsReceipt.package_id == package_id)
        if po_id:
            q = q.where(GoodsReceipt.po_id == po_id)
        if date_from:
            q = q.where(GoodsReceipt.received_date >= date_from)
        if date_to:
            q = q.where(GoodsReceipt.received_date <= date_to)
        result = await self.db.execute(q.order_by(GoodsReceipt.received_date.desc()))
        return list(result.scalars().all())
