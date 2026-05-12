from uuid import UUID
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models_v2.procurement import ProcurementMaterialLink


class MaterialLinkRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, data: dict) -> ProcurementMaterialLink:
        link = ProcurementMaterialLink(**data)
        self.db.add(link)
        await self.db.flush()
        await self.db.refresh(link)
        return link

    async def get_by_id(self, link_id: UUID) -> Optional[ProcurementMaterialLink]:
        result = await self.db.execute(
            select(ProcurementMaterialLink).where(ProcurementMaterialLink.id == link_id)
        )
        return result.scalar_one_or_none()

    async def list_by_package(
        self,
        package_id: UUID,
        risk_level: Optional[str] = None,
        on_critical_path: Optional[bool] = None,
    ) -> list[ProcurementMaterialLink]:
        q = select(ProcurementMaterialLink).where(ProcurementMaterialLink.package_id == package_id)
        if risk_level:
            q = q.where(ProcurementMaterialLink.risk_level == risk_level)
        if on_critical_path is not None:
            q = q.where(ProcurementMaterialLink.is_critical_path == on_critical_path)
        result = await self.db.execute(q.order_by(ProcurementMaterialLink.risk_score.desc()))
        return list(result.scalars().all())

    async def update(self, link: ProcurementMaterialLink, data: dict) -> ProcurementMaterialLink:
        for key, val in data.items():
            setattr(link, key, val)
        await self.db.flush()
        await self.db.refresh(link)
        return link

    async def delete(self, link: ProcurementMaterialLink) -> None:
        await self.db.delete(link)
        await self.db.flush()

    async def list_all_for_package(self, package_id: UUID) -> list[ProcurementMaterialLink]:
        result = await self.db.execute(
            select(ProcurementMaterialLink).where(ProcurementMaterialLink.package_id == package_id)
        )
        return list(result.scalars().all())
