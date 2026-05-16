from uuid import UUID
from typing import Optional
from datetime import date

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.procurement_module.goods_receipt_sub_module.dtos.request_dtos import GRNCreateDTO
from app.modules.procurement_module.goods_receipt_sub_module.repositories.repository import GRNRepository
from app.models_v2.procurement import GoodsReceipt


class GRNService:
    def __init__(self, db: AsyncSession):
        self.repo = GRNRepository(db)

    async def create(self, payload: GRNCreateDTO) -> GoodsReceipt:
        return await self.repo.create(payload.model_dump())

    async def get_by_id(self, grn_id: UUID) -> GoodsReceipt:
        grn = await self.repo.get_by_id(grn_id)
        if not grn:
            raise ValueError(f"GRN {grn_id} not found")
        return grn

    async def list_by_package(
        self,
        package_id: UUID,
        po_id: Optional[UUID] = None,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
    ) -> list[GoodsReceipt]:
        return await self.repo.list_by_package(package_id, po_id, date_from, date_to)
