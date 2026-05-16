from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models_v2.identity import Person
from ..services.person_service import PersonService
from ..dependencies import get_current_person
from ..dtos.response_dtos import PersonaCardDTO, MeDTO, RoleDTO


router = APIRouter(prefix="/identity", tags=["Identity"])


@router.get("/personas", response_model=list[PersonaCardDTO])
async def list_personas(db: AsyncSession = Depends(get_db)):
    return await PersonService(db).list_personas()


@router.get("/me", response_model=MeDTO)
async def get_me(
    person: Person = Depends(get_current_person),
    db: AsyncSession = Depends(get_db),
):
    return await PersonService(db).get_me(person.id)


@router.get("/roles", response_model=list[RoleDTO])
async def list_roles(db: AsyncSession = Depends(get_db)):
    return await PersonService(db).list_roles()
