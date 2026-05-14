from pydantic import BaseModel
from typing import List, Optional
from uuid import UUID


class DashboardMetric(BaseModel):
    label: str
    value: int | float | str
    intent: str = "neutral"
    hint: Optional[str] = None


class DashboardBlock(BaseModel):
    key: str
    title: str
    metrics: List[DashboardMetric]
    drill_to: Optional[str] = None


class RoleDashboardDTO(BaseModel):
    view: str   # exec | logistics | tender | bim | contract | contractor | pmc
    role_code: str
    package_id: Optional[UUID] = None
    blocks: List[DashboardBlock]
