from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import date

from app.core.enums import GRNStatus


class GRNCreateDTO(BaseModel):
    po_id: UUID
    package_id: UUID
    grn_number: str
    received_date: date
    received_qty: float
    ordered_qty: Optional[float] = None
    unit: str
    status: GRNStatus = GRNStatus.ACCEPTED
    test_certificate_ref: Optional[str] = None
    inspector: Optional[str] = None
    remarks: Optional[str] = None
