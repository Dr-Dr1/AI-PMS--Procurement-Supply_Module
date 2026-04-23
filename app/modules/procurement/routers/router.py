from fastapi import APIRouter,Depends
from app.core.database import get_db
from app.modules.procurement.dtos.dtos import ProcurementOrderCreate,ProcurementOrderResponse
from app.modules.procurement.services.service import ProcurementService
router=APIRouter(prefix="/procurement", tags=["Procurement"])


@router.post("/orders", response_model=ProcurementOrderResponse)
async def create_order(request:ProcurementOrderCreate, db=Depends(get_db)):
    return await ProcurementService(db).create_order(request)
@router.get("/orders")
async def list_orders(db=Depends(get_db)):
    return await ProcurementService(db).list_orders()
