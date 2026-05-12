from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import date, datetime


class GRNResponseDTO(BaseModel):
    id: UUID
    po_id: UUID
    package_id: UUID
    grn_number: str
    received_date: date
    received_qty: float
    ordered_qty: Optional[float] = None
    unit: str
    status: str
    test_certificate_ref: Optional[str] = None
    inspector: Optional[str] = None
    remarks: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
