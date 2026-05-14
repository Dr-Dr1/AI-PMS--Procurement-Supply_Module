from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models_v2.identity import Person
from app.modules.procurement_module.dashboard_sub_module.dtos.response_dtos import ProcurementDashboardDTO
from app.modules.procurement_module.dashboard_sub_module.dtos.role_response_dtos import RoleDashboardDTO
from app.modules.procurement_module.dashboard_sub_module.services.service import DashboardService
from app.modules.procurement_module.dashboard_sub_module.services.role_dashboard_service import RoleDashboardService
from app.modules.identity_module.dependencies import get_current_person, get_current_person_role_code

router = APIRouter(prefix="/procurement/dashboard", tags=["Procurement — Dashboard"])


@router.get("/me", response_model=RoleDashboardDTO)
async def get_my_dashboard(
    package_id: Optional[UUID] = Query(None),
    db: AsyncSession = Depends(get_db),
    person: Person = Depends(get_current_person),
    role_code: str = Depends(get_current_person_role_code),
):
    """Role-aware Procurement dashboard. 7 builders incl. logistics (primary owner per XLSX)."""
    return await RoleDashboardService(db).get_my_dashboard(
        package_id=package_id, role_code=role_code, person_id=person.person_id,
    )


@router.get("", response_model=ProcurementDashboardDTO)
async def get_dashboard(
    package_id: Optional[UUID] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    svc = DashboardService(db)
    return await svc.get_dashboard(package_id)
