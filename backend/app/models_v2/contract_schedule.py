from __future__ import annotations

import uuid
from datetime import date, datetime

from sqlalchemy import Date, DateTime, ForeignKey, Integer, JSON, Numeric, String
from sqlalchemy import Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.core.enums import ContractStandard, EOTMethodology


class ScheduleV2Contract(Base):
    """Schedule module's contract table (schedule_v2_contracts)."""
    __tablename__ = "schedule_v2_contracts"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    contract_number: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    contract_standard: Mapped[str] = mapped_column(
        SAEnum(ContractStandard, name="contract_standard_enum", create_constraint=True, create_type=False),
        nullable=False,
    )
    contract_value: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False)
    revised_value: Mapped[float | None] = mapped_column(Numeric(15, 2), nullable=True)
    commencement_date: Mapped[date] = mapped_column(Date, nullable=False)
    completion_date: Mapped[date] = mapped_column(Date, nullable=False)
    dlp_months: Mapped[int] = mapped_column(Integer, nullable=False)
    eot_methodology: Mapped[str] = mapped_column(
        SAEnum(EOTMethodology, name="eot_methodology_enum", create_constraint=True, create_type=False),
        nullable=False,
    )
    ld_formula: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    notice_rules: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
