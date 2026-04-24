"""
Layer 4: Governance & Audit — CDM v1.1

AuditEvent is append-only. Nothing is ever deleted.
Every state transition in the system creates an AuditEvent.
"""

import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, Enum as SAEnum, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID

from app.core.database import Base
from app.core.enums import AuditAction


class AuditEvent(Base):
    """
    Immutable audit trail. Per NFR-16: all workflow state transitions logged.
    actor_person_id is null for system/AI actions.
    Timestamps NTP-synchronized per NFR-38.
    """
    __tablename__ = "audit_events"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    entity_type: Mapped[str] = mapped_column(String(100), nullable=False)  # e.g., "RFI", "DPR"
    entity_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    action: Mapped[str] = mapped_column(
        SAEnum(AuditAction, name="audit_action_enum", create_constraint=True), nullable=False
    )
    old_value: Mapped[dict | None] = mapped_column(JSON)
    new_value: Mapped[dict] = mapped_column(JSON, nullable=False)
    actor_person_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("persons.id"))
    actor_agent_type: Mapped[str | None] = mapped_column(String(50))  # AI agent type if agent-initiated
    ip_address: Mapped[str | None] = mapped_column(String(45))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)