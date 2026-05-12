from typing import List, Optional
from uuid import UUID
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.modules.procurement_module.goods_receipt_sub_module.dtos.request_dtos import GRNCreateDTO
from app.modules.procurement_module.goods_receipt_sub_module.dtos.response_dtos import GRNResponseDTO
from app.modules.procurement_module.goods_receipt_sub_module.services.service import GRNService

router = APIRouter(prefix="/procurement/grns", tags=["Procurement — GRN"])


@router.post("", response_model=GRNResponseDTO, status_code=201)
async def create_grn(payload: GRNCreateDTO, db: AsyncSession = Depends(get_db)):
    svc = GRNService(db)
    result = await svc.create(payload)
    await db.commit()
    return result


@router.get("", response_model=List[GRNResponseDTO])
async def list_grns(
    package_id: UUID = Query(...),
    po_id: Optional[UUID] = Query(None),
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    svc = GRNService(db)
    return await svc.list_by_package(package_id, po_id, date_from, date_to)


@router.get("/{grn_id}", response_model=GRNResponseDTO)
async def get_grn(grn_id: UUID, db: AsyncSession = Depends(get_db)):
    svc = GRNService(db)
    try:
        return await svc.get_by_id(grn_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
