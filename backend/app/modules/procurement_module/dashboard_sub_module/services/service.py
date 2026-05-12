from uuid import UUID
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.procurement_module.dashboard_sub_module.repositories.repository import DashboardRepository


class DashboardService:
    def __init__(self, db: AsyncSession):
        self.repo = DashboardRepository(db)

    async def get_dashboard(self, package_id: Optional[UUID]) -> dict:
        data = await self.repo.get_kpis(package_id)
        data["package_id"] = package_id
        return data
