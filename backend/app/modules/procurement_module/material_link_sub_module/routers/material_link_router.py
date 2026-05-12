from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.modules.procurement_module.material_link_sub_module.dtos.request_dtos import (
    MaterialLinkCreateDTO, MaterialLinkUpdateDTO,
)
from app.modules.procurement_module.material_link_sub_module.dtos.response_dtos import (
    MaterialLinkResponseDTO, BulkRefreshResponseDTO,
)
from app.modules.procurement_module.material_link_sub_module.services.service import MaterialLinkService

router = APIRouter(prefix="/procurement/material-links", tags=["Procurement — Material Links"])


@router.post("", response_model=MaterialLinkResponseDTO, status_code=201)
async def create_material_link(payload: MaterialLinkCreateDTO, db: AsyncSession = Depends(get_db)):
    svc = MaterialLinkService(db)
    result = await svc.create(payload)
    await db.commit()
    return result


@router.get("", response_model=List[MaterialLinkResponseDTO])
async def list_material_links(
    package_id: UUID = Query(...),
    risk_level: Optional[str] = Query(None),
    on_critical_path: Optional[bool] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    svc = MaterialLinkService(db)
    return await svc.list_by_package(package_id, risk_level, on_critical_path)


@router.get("/{link_id}", response_model=MaterialLinkResponseDTO)
async def get_material_link(link_id: UUID, db: AsyncSession = Depends(get_db)):
    svc = MaterialLinkService(db)
    try:
        return await svc.get_by_id(link_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.patch("/{link_id}", response_model=MaterialLinkResponseDTO)
async def update_material_link(
    link_id: UUID, payload: MaterialLinkUpdateDTO, db: AsyncSession = Depends(get_db)
):
    svc = MaterialLinkService(db)
    try:
        result = await svc.update(link_id, payload)
        await db.commit()
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/{link_id}", status_code=204)
async def delete_material_link(link_id: UUID, db: AsyncSession = Depends(get_db)):
    svc = MaterialLinkService(db)
    try:
        await svc.delete(link_id)
        await db.commit()
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/bulk-refresh-risk", response_model=BulkRefreshResponseDTO)
async def bulk_refresh_risk(package_id: UUID = Query(...), db: AsyncSession = Depends(get_db)):
    svc = MaterialLinkService(db)
    count = await svc.bulk_refresh_risk(package_id)
    await db.commit()
    return BulkRefreshResponseDTO(refreshed=count, package_id=package_id)


@router.post("/{link_id}/refresh-risk", response_model=MaterialLinkResponseDTO)
async def refresh_risk(link_id: UUID, db: AsyncSession = Depends(get_db)):
    svc = MaterialLinkService(db)
    try:
        result = await svc.refresh_risk(link_id)
        await db.commit()
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
