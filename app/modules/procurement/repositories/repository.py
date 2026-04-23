from sqlalchemy import select
from app.models.models import ProcurementOrder
class ProcurementRepository:
    def __init__(self,db): self.db=db
    async def create(self,title):
        obj=ProcurementOrder(title=title)
        self.db.add(obj)
        await self.db.commit()
        await self.db.refresh(obj)
        return obj
    async def get_all(self):
        r=await self.db.execute(select(ProcurementOrder)); return r.scalars().all()
