from pydantic import BaseModel
from typing import Optional
from uuid import UUID


class ProcurementDashboardDTO(BaseModel):
    total_pos: int
    pos_by_status: dict
    overdue_deliveries: int
    at_risk_materials: int
    cp_materials_delayed: int
    delivery_compliance_rate: float
    total_grns: int
    grns_this_month: int
    total_material_links: int
    package_id: Optional[UUID] = None
