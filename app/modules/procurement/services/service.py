from app.modules.procurement.repositories.repository import ProcurementRepository
class ProcurementService:
    def __init__(self,db): self.repo=ProcurementRepository(db)
    async def create_order(self,data): return await self.repo.create(data.title)
    async def list_orders(self): return await self.repo.get_all()
