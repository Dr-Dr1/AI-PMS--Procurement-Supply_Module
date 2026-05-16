from uuid import UUID
from typing import Optional
from datetime import date, datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.procurement_module.material_link_sub_module.dtos.request_dtos import (
    MaterialLinkCreateDTO, MaterialLinkUpdateDTO,
)
from app.modules.procurement_module.material_link_sub_module.repositories.repository import MaterialLinkRepository
from app.models_v2.procurement import MaterialScheduleLink
from app.core.enums import RiskLevel, MaterialLinkStatus


def _calc_risk(
    planned_delivery_date: Optional[date],
    actual_delivery_date: Optional[date],
    is_critical_path: bool,
) -> tuple[int, RiskLevel, MaterialLinkStatus]:
    today = date.today()
    base_score = 10
    status = MaterialLinkStatus.ON_TRACK
    level = RiskLevel.LOW

    if planned_delivery_date:
        if actual_delivery_date is None and planned_delivery_date < today:
            days_overdue = (today - planned_delivery_date).days
            base_score = min(100, 85 + days_overdue)
            level = RiskLevel.HIGH
            status = MaterialLinkStatus.OVERDUE
        elif actual_delivery_date is None:
            days_remaining = (planned_delivery_date - today).days
            if days_remaining <= 7:
                base_score = min(75, 40 + max(0, 7 - days_remaining) * 5)
                level = RiskLevel.MEDIUM
                status = MaterialLinkStatus.AT_RISK
            else:
                base_score = max(10, 35 - days_remaining)
                level = RiskLevel.LOW
                status = MaterialLinkStatus.ON_TRACK
        else:
            base_score = 5
            level = RiskLevel.LOW
            status = MaterialLinkStatus.ON_TRACK

    if is_critical_path and level != RiskLevel.LOW:
        base_score = min(100, base_score + 15)

    return base_score, level, status


class MaterialLinkService:
    def __init__(self, db: AsyncSession):
        self.repo = MaterialLinkRepository(db)

    async def create(self, payload: MaterialLinkCreateDTO) -> MaterialScheduleLink:
        data = payload.model_dump()
        score, level, status = _calc_risk(
            data.get("planned_delivery_date"),
            data.get("actual_delivery_date"),
            data.get("is_critical_path", False),
        )
        data["risk_score"] = score
        data["risk_level"] = level
        data["status"] = status
        data["last_risk_refresh"] = datetime.utcnow()
        return await self.repo.create(data)

    async def get_by_id(self, link_id: UUID) -> MaterialScheduleLink:
        link = await self.repo.get_by_id(link_id)
        if not link:
            raise ValueError(f"Material link {link_id} not found")
        return link

    async def list_by_package(
        self,
        package_id: UUID,
        risk_level: Optional[str] = None,
        on_critical_path: Optional[bool] = None,
    ) -> list[MaterialScheduleLink]:
        return await self.repo.list_by_package(package_id, risk_level, on_critical_path)

    async def update(self, link_id: UUID, payload: MaterialLinkUpdateDTO) -> MaterialScheduleLink:
        link = await self.get_by_id(link_id)
        data = payload.model_dump(exclude_none=True)
        updated = await self.repo.update(link, data)
        # Recalc risk after update
        return await self.refresh_risk(updated.id)

    async def delete(self, link_id: UUID) -> None:
        link = await self.get_by_id(link_id)
        await self.repo.delete(link)

    async def refresh_risk(self, link_id: UUID) -> MaterialScheduleLink:
        link = await self.get_by_id(link_id)
        score, level, status = _calc_risk(
            link.planned_delivery_date,
            link.actual_delivery_date,
            link.is_critical_path,
        )
        return await self.repo.update(link, {
            "risk_score": score,
            "risk_level": level,
            "status": status,
            "last_risk_refresh": datetime.utcnow(),
        })

    async def bulk_refresh_risk(self, package_id: UUID) -> int:
        links = await self.repo.list_all_for_package(package_id)
        now = datetime.utcnow()
        for link in links:
            score, level, status = _calc_risk(
                link.planned_delivery_date, link.actual_delivery_date, link.is_critical_path
            )
            await self.repo.update(link, {
                "risk_score": score,
                "risk_level": level,
                "status": status,
                "last_risk_refresh": now,
            })
        return len(links)
