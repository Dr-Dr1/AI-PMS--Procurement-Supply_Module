from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import date


class MaterialLinkCreateDTO(BaseModel):
    package_id: UUID
    material_name: str
    activity_id: Optional[str] = None
    po_id: Optional[UUID] = None
    is_critical_path: bool = False
    planned_delivery_date: Optional[date] = None
    actual_delivery_date: Optional[date] = None


class MaterialLinkUpdateDTO(BaseModel):
    material_name: Optional[str] = None
    activity_id: Optional[str] = None
    po_id: Optional[UUID] = None
    is_critical_path: Optional[bool] = None
    planned_delivery_date: Optional[date] = None
    actual_delivery_date: Optional[date] = None
