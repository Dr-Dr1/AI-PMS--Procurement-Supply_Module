from uuid import UUID
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.procurement_module.po_sub_module.dtos.request_dtos import (
    POCreateDTO, POUpdateDTO, POLineItemCreateDTO, POLineItemUpdateDTO,
)
from app.modules.procurement_module.po_sub_module.repositories.repository import PORepository
from app.models_v2.procurement import PO, POLineItem
from app.core.enums import POStatus

_TRANSITIONS = {
    POStatus.DRAFT: POStatus.ISSUED,
    POStatus.ISSUED: POStatus.ACKNOWLEDGED,
    POStatus.ACKNOWLEDGED: POStatus.DISPATCHED,
    POStatus.DISPATCHED: POStatus.CLOSED,
}

_ALLOWED_FROM_ACKNOWLEDGE = {POStatus.DRAFT, POStatus.ISSUED}
_ALLOWED_FROM_DISPATCH = {POStatus.ACKNOWLEDGED}
_ALLOWED_FROM_CLOSE = {POStatus.DRAFT, POStatus.ISSUED, POStatus.ACKNOWLEDGED, POStatus.DISPATCHED}


class POService:
    def __init__(self, db: AsyncSession):
        self.repo = PORepository(db)

    async def create(self, payload: POCreateDTO) -> PO:
        data = payload.model_dump()
        data["status"] = POStatus.DRAFT
        data["is_overdue"] = False
        return await self.repo.create(data)

    async def list_by_package(self, package_id: UUID, status: Optional[str] = None) -> list[PO]:
        return await self.repo.list_by_package(package_id, status)

    async def get_by_id(self, po_id: UUID) -> PO:
        po = await self.repo.get_by_id(po_id)
        if not po:
            raise ValueError(f"PO {po_id} not found")
        return po

    async def update(self, po_id: UUID, payload: POUpdateDTO) -> PO:
        po = await self.get_by_id(po_id)
        return await self.repo.update(po, payload.model_dump(exclude_none=True))

    async def delete(self, po_id: UUID) -> None:
        po = await self.get_by_id(po_id)
        await self.repo.delete(po)

    async def acknowledge(self, po_id: UUID) -> PO:
        po = await self.get_by_id(po_id)
        if po.status not in _ALLOWED_FROM_ACKNOWLEDGE:
            raise ValueError(f"Cannot acknowledge PO in status {po.status}")
        return await self.repo.transition_status(po, POStatus.ACKNOWLEDGED)

    async def dispatch(self, po_id: UUID) -> PO:
        po = await self.get_by_id(po_id)
        if po.status not in _ALLOWED_FROM_DISPATCH:
            raise ValueError(f"Cannot dispatch PO in status {po.status}")
        return await self.repo.transition_status(po, POStatus.DISPATCHED)

    async def close(self, po_id: UUID) -> PO:
        po = await self.get_by_id(po_id)
        if po.status not in _ALLOWED_FROM_CLOSE:
            raise ValueError(f"Cannot close PO in status {po.status}")
        return await self.repo.transition_status(po, POStatus.CLOSED)

    async def issue(self, po_id: UUID) -> PO:
        po = await self.get_by_id(po_id)
        if po.status != POStatus.DRAFT:
            raise ValueError(f"Cannot issue PO in status {po.status}")
        return await self.repo.transition_status(po, POStatus.ISSUED)

    # ── Line Items ──────────────────────────────────────────────────────────

    async def add_item(self, po_id: UUID, payload: POLineItemCreateDTO) -> POLineItem:
        await self.get_by_id(po_id)
        data = payload.model_dump()
        data["amount"] = data["quantity"] * data["unit_rate"]
        item = await self.repo.add_item(po_id, data)
        await self.repo.recalc_total(po_id)
        return item

    async def get_items(self, po_id: UUID) -> list[POLineItem]:
        await self.get_by_id(po_id)
        return await self.repo.get_items(po_id)

    async def update_item(self, po_id: UUID, item_id: UUID, payload: POLineItemUpdateDTO) -> POLineItem:
        await self.get_by_id(po_id)
        item = await self.repo.get_item(item_id)
        if not item or item.po_id != po_id:
            raise ValueError(f"Line item {item_id} not found on PO {po_id}")
        updated = await self.repo.update_item(item, payload.model_dump(exclude_none=True))
        await self.repo.recalc_total(po_id)
        return updated

    async def delete_item(self, po_id: UUID, item_id: UUID) -> None:
        await self.get_by_id(po_id)
        item = await self.repo.get_item(item_id)
        if not item or item.po_id != po_id:
            raise ValueError(f"Line item {item_id} not found on PO {po_id}")
        await self.repo.delete_item(item)
        await self.repo.recalc_total(po_id)
