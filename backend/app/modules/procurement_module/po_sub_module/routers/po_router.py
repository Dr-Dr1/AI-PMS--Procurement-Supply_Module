from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.modules.procurement_module.po_sub_module.dtos.request_dtos import (
    POCreateDTO, POUpdateDTO, POLineItemCreateDTO, POLineItemUpdateDTO,
)
from app.modules.procurement_module.po_sub_module.dtos.response_dtos import (
    POResponseDTO, POLineItemResponseDTO,
)
from app.modules.procurement_module.po_sub_module.services.service import POService

router = APIRouter(prefix="/procurement/pos", tags=["Procurement — PO"])


@router.post("", response_model=POResponseDTO, status_code=201)
async def create_po(payload: POCreateDTO, db: AsyncSession = Depends(get_db)):
    svc = POService(db)
    result = await svc.create(payload)
    await db.commit()
    return result


@router.get("", response_model=List[POResponseDTO])
async def list_pos(
    package_id: UUID = Query(...),
    status: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    svc = POService(db)
    result = await svc.list_by_package(package_id, status)
    await db.commit()
    return result


@router.get("/{po_id}", response_model=POResponseDTO)
async def get_po(po_id: UUID, db: AsyncSession = Depends(get_db)):
    svc = POService(db)
    try:
        return await svc.get_by_id(po_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.patch("/{po_id}", response_model=POResponseDTO)
async def update_po(po_id: UUID, payload: POUpdateDTO, db: AsyncSession = Depends(get_db)):
    svc = POService(db)
    try:
        result = await svc.update(po_id, payload)
        await db.commit()
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/{po_id}", status_code=204)
async def delete_po(po_id: UUID, db: AsyncSession = Depends(get_db)):
    svc = POService(db)
    try:
        await svc.delete(po_id)
        await db.commit()
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/{po_id}/issue", response_model=POResponseDTO)
async def issue_po(po_id: UUID, db: AsyncSession = Depends(get_db)):
    svc = POService(db)
    try:
        result = await svc.issue(po_id)
        await db.commit()
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{po_id}/acknowledge", response_model=POResponseDTO)
async def acknowledge_po(po_id: UUID, db: AsyncSession = Depends(get_db)):
    svc = POService(db)
    try:
        result = await svc.acknowledge(po_id)
        await db.commit()
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{po_id}/dispatch", response_model=POResponseDTO)
async def dispatch_po(po_id: UUID, db: AsyncSession = Depends(get_db)):
    svc = POService(db)
    try:
        result = await svc.dispatch(po_id)
        await db.commit()
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{po_id}/close", response_model=POResponseDTO)
async def close_po(po_id: UUID, db: AsyncSession = Depends(get_db)):
    svc = POService(db)
    try:
        result = await svc.close(po_id)
        await db.commit()
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ── Line Items ───────────────────────────────────────────────────────────────

@router.post("/{po_id}/items", response_model=POLineItemResponseDTO, status_code=201)
async def add_item(po_id: UUID, payload: POLineItemCreateDTO, db: AsyncSession = Depends(get_db)):
    svc = POService(db)
    try:
        result = await svc.add_item(po_id, payload)
        await db.commit()
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{po_id}/items", response_model=List[POLineItemResponseDTO])
async def list_items(po_id: UUID, db: AsyncSession = Depends(get_db)):
    svc = POService(db)
    try:
        return await svc.get_items(po_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.patch("/{po_id}/items/{item_id}", response_model=POLineItemResponseDTO)
async def update_item(
    po_id: UUID, item_id: UUID, payload: POLineItemUpdateDTO, db: AsyncSession = Depends(get_db)
):
    svc = POService(db)
    try:
        result = await svc.update_item(po_id, item_id, payload)
        await db.commit()
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/{po_id}/items/{item_id}", status_code=204)
async def delete_item(po_id: UUID, item_id: UUID, db: AsyncSession = Depends(get_db)):
    svc = POService(db)
    try:
        await svc.delete_item(po_id, item_id)
        await db.commit()
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
