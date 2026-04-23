from pydantic import BaseModel
class ProcurementOrderCreate(BaseModel):
    title:str

class ProcurementOrderResponse(BaseModel):
    id:int
    title:str
    status:str
    class Config:
        from_attributes=True
