from uuid import UUID
from typing import Optional
from datetime import date

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models_v2.procurement import ProcurementGRN


class GRNRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, data: dict) -> ProcurementGRN:
        grn = ProcurementGRN(**data)
        self.db.add(grn)
        await self.db.flush()
        await self.db.refresh(grn)
        return grn

    async def get_by_id(self, grn_id: UUID) -> Optional[ProcurementGRN]:
        result = await self.db.execute(
            select(ProcurementGRN).where(ProcurementGRN.id == grn_id)
        )
        return result.scalar_one_or_none()

    async def list_by_package(
        self,
        package_id: UUID,
        po_id: Optional[UUID] = None,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
    ) -> list[ProcurementGRN]:
        q = select(ProcurementGRN).where(ProcurementGRN.package_id == package_id)
        if po_id:
            q = q.where(ProcurementGRN.po_id == po_id)
        if date_from:
            q = q.where(ProcurementGRN.received_date >= date_from)
        if date_to:
            q = q.where(ProcurementGRN.received_date <= date_to)
        result = await self.db.execute(q.order_by(ProcurementGRN.received_date.desc()))
        return list(result.scalars().all())
