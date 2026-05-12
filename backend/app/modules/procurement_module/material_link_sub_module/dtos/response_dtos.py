from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import date, datetime


class MaterialLinkResponseDTO(BaseModel):
    id: UUID
    package_id: UUID
    material_name: str
    activity_id: Optional[str] = None
    po_id: Optional[UUID] = None
    is_critical_path: bool
    risk_score: int
    risk_level: str
    status: str
    planned_delivery_date: Optional[date] = None
    actual_delivery_date: Optional[date] = None
    last_risk_refresh: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class BulkRefreshResponseDTO(BaseModel):
    refreshed: int
    package_id: UUID
