from uuid import UUID
from fastapi import Depends, Header, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models_v2.identity import Person
from .repositories.person_repository import PersonRepository
from .role_permissions import role_has_feature, is_superadmin


async def get_current_person(
    x_user_id: str | None = Header(None, alias="X-User-ID"),
    db: AsyncSession = Depends(get_db),
) -> Person:
    if not x_user_id:
        raise HTTPException(401, detail="Missing X-User-ID header")
    try:
        person_id = UUID(x_user_id)
    except ValueError:
        raise HTTPException(400, detail="X-User-ID is not a valid UUID")
    p = await PersonRepository(db).get_by_id(person_id)
    if not p or not p.is_active:
        raise HTTPException(401, detail="Unknown or inactive user")
    return p


async def get_current_person_role_code(
    person: Person = Depends(get_current_person),
    db: AsyncSession = Depends(get_db),
) -> str:
    role = await PersonRepository(db).get_role(person.role_id)
    if not role:
        raise HTTPException(500, detail="Person has dangling role")
    return role.role_code


def require_feature(feature: str):
    """Dependency factory. Use as: Depends(require_feature('quality.rfi.inspect'))"""
    async def _checker(role_code: str = Depends(get_current_person_role_code)) -> None:
        if is_superadmin(role_code):
            return
        if not role_has_feature(role_code, feature):
            raise HTTPException(403, detail=f"Role {role_code} lacks feature {feature}")
    return _checker
