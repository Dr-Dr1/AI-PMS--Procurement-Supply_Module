from uuid import UUID
from pydantic import BaseModel, Field

from app.core.enums import OrgType, RBACTier, AIAccessLevel


class OrganizationCreateDTO(BaseModel):
    org_type: OrgType
    org_name: str = Field(min_length=2, max_length=300)
    packages: list[UUID] | None = None


class RoleCreateDTO(BaseModel):
    role_code: str = Field(min_length=2, max_length=50)
    role_name: str = Field(min_length=2, max_length=150)
    rbac_tier: RBACTier
    ai_access_level: AIAccessLevel
    description: str | None = None


class PersonCreateDTO(BaseModel):
    org_id: UUID
    name: str = Field(min_length=2, max_length=200)
    email: str | None = None
    role_id: UUID
    packages: list[UUID] | None = None
