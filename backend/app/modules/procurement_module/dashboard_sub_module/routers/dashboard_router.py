from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.modules.procurement_module.dashboard_sub_module.dtos.response_dtos import ProcurementDashboardDTO
from app.modules.procurement_module.dashboard_sub_module.services.service import DashboardService

router = APIRouter(prefix="/procurement/dashboard", tags=["Procurement — Dashboard"])


@router.get("", response_model=ProcurementDashboardDTO)
async def get_dashboard(
    package_id: Optional[UUID] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    svc = DashboardService(db)
    return await svc.get_dashboard(package_id)
