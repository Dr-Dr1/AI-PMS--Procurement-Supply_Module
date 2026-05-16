from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, JSON, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

from app.models_v2.schedule import *
from app.models_v2.structure import *

class XERImport(Base):
    __tablename__ = "xer_imports"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    file_path: Mapped[str] = mapped_column(Text, nullable=False)

    total_projects: Mapped[int] = mapped_column(Integer, default=0)
    total_activities: Mapped[int] = mapped_column(Integer, default=0)
    total_resources: Mapped[int] = mapped_column(Integer, default=0)
    total_calendars: Mapped[int] = mapped_column(Integer, default=0)
    total_wbs: Mapped[int] = mapped_column(Integer, default=0)
    total_relationships: Mapped[int] = mapped_column(Integer, default=0)
    total_corridors: Mapped[int] = mapped_column(Integer, default=0)
    total_packages: Mapped[int] = mapped_column(Integer, default=0)

    parse_response: Mapped[dict] = mapped_column(JSON, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow
    )

    projects: Mapped[list["Project"]] = relationship(
        back_populates="schedule_import",
        cascade="all, delete-orphan"
    )

    activities: Mapped[list["Activity"]] = relationship(
        back_populates="schedule_import",
        cascade="all, delete-orphan"
    )

    wbs_items: Mapped[list["WBS"]] = relationship(
        back_populates="schedule_import",
        cascade="all, delete-orphan"
    )

    calendars: Mapped[list["Calendar"]] = relationship(
        back_populates="schedule_import",
        cascade="all, delete-orphan"
    )

    resources: Mapped[list["Resource"]] = relationship(
        back_populates="schedule_import",
        cascade="all, delete-orphan"
    )

    relationships: Mapped[list["Relationship"]] = relationship(
        back_populates="schedule_import",
        cascade="all, delete-orphan"
    )

    assignments: Mapped[list["ResourceAssignment"]] = relationship(
        back_populates="schedule_import",
        cascade="all, delete-orphan"
    )

    corridors: Mapped[list["Corridor"]] = relationship(
        back_populates="schedule_import",
        cascade="all, delete-orphan"
    )

    packages: Mapped[list["Package"]] = relationship(
        back_populates="schedule_import",
        cascade="all, delete-orphan"
    )
