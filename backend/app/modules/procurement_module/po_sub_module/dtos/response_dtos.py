from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID
from datetime import date, datetime


class POLineItemResponseDTO(BaseModel):
    id: UUID
    po_id: UUID
    item_code: str
    description: str
    unit: str
    quantity: float
    unit_rate: float
    amount: float
    created_at: datetime

    class Config:
        from_attributes = True


class POResponseDTO(BaseModel):
    id: UUID
    package_id: UUID
    po_number: str
    vendor_name: str
    description: Optional[str] = None
    total_amount: float
    currency: str
    status: str
    committed_delivery_date: Optional[date] = None
    is_overdue: bool
    created_at: datetime
    updated_at: datetime
    items: List[POLineItemResponseDTO] = []

    class Config:
        from_attributes = True
