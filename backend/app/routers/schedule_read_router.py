"""
Read-only schedule data endpoints for dropdown population.
Provides projects, corridors, packages, and activities for the frontend selectors.
"""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models_v2.schedule_readonly import (
    ProjectReadOnly,
    CorridorReadOnly,
    PackageReadOnly,
    ActivityReadOnly,
)

router = APIRouter(tags=["Schedule — Read Only"])


@router.get("/projects")
async def list_projects(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ProjectReadOnly))
    projects = result.scalars().all()
    return {
        "message": "Projects fetched",
        "count": len(projects),
        "data": [
            {
                "id": str(p.id),
                "proj_id": p.proj_id,
                "proj_name": p.proj_name,
                "proj_short_name": p.proj_short_name,
                "scd_start_date": p.scd_start_date,
                "scd_end_date": p.scd_end_date,
                "activity_count": p.activity_count,
            }
            for p in projects
        ],
    }


@router.get("/corridors")
async def list_corridors(proj_id: Optional[int] = None, db: AsyncSession = Depends(get_db)):
    stmt = select(CorridorReadOnly)
    if proj_id is not None:
        stmt = stmt.where(CorridorReadOnly.proj_id == proj_id)
    result = await db.execute(stmt)
    corridors = result.scalars().all()
    return {
        "message": "Corridors fetched",
        "count": len(corridors),
        "data": [
            {
                "id": str(c.id),
                "corridor_name": c.corridor_name,
                "corridor_code": c.corridor_code,
                "import_id": str(c.import_id),
            }
            for c in corridors
        ],
    }


@router.get("/packages")
async def list_packages(corridor_id: Optional[UUID] = None, db: AsyncSession = Depends(get_db)):
    stmt = select(PackageReadOnly)
    if corridor_id:
        stmt = stmt.where(PackageReadOnly.corridor_id == corridor_id)
    result = await db.execute(stmt)
    packages = result.scalars().all()
    return {
        "message": "Packages fetched",
        "count": len(packages),
        "data": [
            {
                "id": str(p.id),
                "package_name": p.package_name,
                "package_code": p.package_code,
                "contractor_name": p.contractor_name,
                "corridor_id": str(p.corridor_id) if p.corridor_id else None,
            }
            for p in packages
        ],
    }


@router.get("/packages/{package_id}")
async def get_package(package_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(PackageReadOnly).where(PackageReadOnly.id == package_id)
    )
    pkg = result.scalar_one_or_none()
    if not pkg:
        raise HTTPException(status_code=404, detail="Package not found")
    return {
        "message": "Package fetched",
        "data": {
            "id": str(pkg.id),
            "package_name": pkg.package_name,
            "package_code": pkg.package_code,
            "contractor_name": pkg.contractor_name,
            "corridor_id": str(pkg.corridor_id) if pkg.corridor_id else None,
        },
    }


@router.get("/activities/package/{package_id}")
async def list_activities_by_package(package_id: UUID, db: AsyncSession = Depends(get_db)):
    stmt = select(ActivityReadOnly).where(
        ActivityReadOnly.package_id == package_id
    )
    result = await db.execute(stmt)
    activities = result.scalars().all()
    return {
        "message": "Activities fetched",
        "count": len(activities),
        "data": [
            {
                "id": str(a.id),
                "p6_activity_id": a.p6_activity_id,
                "activity_name": a.activity_name,
                "package_id": str(a.package_id) if a.package_id else None,
            }
            for a in activities
        ],
    }
