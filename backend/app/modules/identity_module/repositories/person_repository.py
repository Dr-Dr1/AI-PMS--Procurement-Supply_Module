from uuid import UUID
from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.models_v2.identity import Person, Role, Organization


class PersonRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, person_id: UUID) -> Person | None:
        result = await self.db.execute(
            select(Person).where(Person.id == person_id),
        )
        return result.scalar_one_or_none()

    async def list_active(self) -> Sequence[Person]:
        result = await self.db.execute(
            select(Person).where(Person.is_active == True).order_by(Person.name),  # noqa: E712
        )
        return result.scalars().all()

    async def get_role(self, role_id: UUID) -> Role | None:
        result = await self.db.execute(
            select(Role).where(Role.id == role_id),
        )
        return result.scalar_one_or_none()

    async def get_org(self, org_id: UUID) -> Organization | None:
        result = await self.db.execute(
            select(Organization).where(Organization.id == org_id),
        )
        return result.scalar_one_or_none()

    async def list_roles(self) -> Sequence[Role]:
        result = await self.db.execute(select(Role).order_by(Role.role_code))
        return result.scalars().all()
