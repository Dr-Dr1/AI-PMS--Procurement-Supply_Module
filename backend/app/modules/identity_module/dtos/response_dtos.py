from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict

from app.core.enums import OrgType, RBACTier, AIAccessLevel


class OrganizationDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    org_id: UUID
    org_type: OrgType
    org_name: str


class RoleDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    role_id: UUID
    role_code: str
    role_name: str
    rbac_tier: RBACTier
    ai_access_level: AIAccessLevel
    description: str | None


class PersonaCardDTO(BaseModel):
    """Compact card used in the dropdown."""
    person_id: UUID
    name: str
    email: str | None
    role_code: str
    role_name: str
    rbac_tier: RBACTier
    org_name: str
    org_type: OrgType
    is_active: bool


class MeDTO(BaseModel):
    person_id: UUID
    name: str
    email: str | None
    role_code: str
    role_name: str
    rbac_tier: RBACTier
    ai_access_level: AIAccessLevel
    org_id: UUID
    org_name: str
    org_type: OrgType
    packages: list[UUID] | None
    features: list[str]
    is_superadmin: bool
    dashboard_view: str
    created_at: datetime
