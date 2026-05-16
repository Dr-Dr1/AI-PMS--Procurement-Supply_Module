from uuid import UUID
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.models_v2.identity import Person, Role, Organization
from ..repositories.person_repository import PersonRepository
from ..role_permissions import (
    features_for_role, is_superadmin, ROLE_DASHBOARD_VIEW,
)
from ..dtos.response_dtos import PersonaCardDTO, MeDTO, RoleDTO


class PersonService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = PersonRepository(db)

    async def list_personas(self) -> list[PersonaCardDTO]:
        persons = await self.repo.list_active()
        cards: list[PersonaCardDTO] = []
        for p in persons:
            role = await self.repo.get_role(p.role_id)
            org = await self.repo.get_org(p.org_id)
            if not role or not org:
                continue
            cards.append(PersonaCardDTO(
                person_id=p.id,
                name=p.name,
                email=p.email,
                role_code=role.role_code,
                role_name=role.role_name,
                rbac_tier=p.rbac_tier,
                org_name=org.org_name,
                org_type=org.org_type,
                is_active=p.is_active,
            ))
        return cards

    async def get_me(self, person_id: UUID) -> MeDTO:
        p: Person | None = await self.repo.get_by_id(person_id)
        if not p or not p.is_active:
            raise HTTPException(401, detail="Unknown or inactive user")
        role = await self.repo.get_role(p.role_id)
        org = await self.repo.get_org(p.org_id)
        if not role or not org:
            raise HTTPException(500, detail="Person has dangling role/org reference")
        return MeDTO(
            person_id=p.id,
            name=p.name,
            email=p.email,
            role_code=role.role_code,
            role_name=role.role_name,
            rbac_tier=p.rbac_tier,
            ai_access_level=p.ai_access_level,
            org_id=org.id,
            org_name=org.org_name,
            org_type=org.org_type,
            packages=p.packages,
            features=features_for_role(role.role_code),
            is_superadmin=is_superadmin(role.role_code),
            dashboard_view=ROLE_DASHBOARD_VIEW.get(role.role_code, "exec"),
            created_at=p.created_at,
        )

    async def list_roles(self) -> list[RoleDTO]:
        roles = await self.repo.list_roles()
        return [RoleDTO.model_validate(r) for r in roles]
