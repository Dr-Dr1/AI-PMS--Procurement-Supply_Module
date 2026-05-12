from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import date


class POCreateDTO(BaseModel):
    package_id: UUID
    po_number: str
    vendor_name: str
    description: Optional[str] = None
    total_amount: float = 0.0
    currency: str = "INR"
    committed_delivery_date: Optional[date] = None


class POUpdateDTO(BaseModel):
    vendor_name: Optional[str] = None
    description: Optional[str] = None
    total_amount: Optional[float] = None
    committed_delivery_date: Optional[date] = None


class POLineItemCreateDTO(BaseModel):
    item_code: str
    description: str
    unit: str
    quantity: float
    unit_rate: float


class POLineItemUpdateDTO(BaseModel):
    item_code: Optional[str] = None
    description: Optional[str] = None
    unit: Optional[str] = None
    quantity: Optional[float] = None
    unit_rate: Optional[float] = None
