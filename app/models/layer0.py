"""
Layer 0: Foundation Entities — CDM v1.1

Program (ROOT), Corridor, Package, Contract, Organization, Person, Role, SubsystemType.
These are configured once per deployment. Everything else references these.
No tenant_id per ADR-001.
"""

import uuid
from datetime import date, datetime
from sqlalchemy import (
    String, Integer, Boolean, Date, DateTime, Numeric, Enum as SAEnum,
    ForeignKey, Text, ARRAY, JSON
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from app.core.database import Base
from app.core.enums import (
    ContractStandard, EOTMethodology, OrgType, RBACTier, AIAccessLevel,
    SubsystemType, SubsystemCategory,
)


class Program(Base):
    """
    ROOT entity per CDM v1.1. Replaces Tenant as hierarchy root.
    Represents the overall metro programme (e.g., Delhi Metro Phase IV).
    """
    __tablename__ = "programs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(300), nullable=False)
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    start_date: Mapped[date | None] = mapped_column(Date)
    end_date: Mapped[date | None] = mapped_column(Date)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    # Relationships
    corridors: Mapped[list["Corridor"]] = relationship(back_populates="program", lazy="selectin")


class Corridor(Base):
    """
    A specific metro line within a Program.
    E.g., 'Janakpuri West – RK Ashram Marg'.
    """
    __tablename__ = "corridors"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    program_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("programs.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(300), nullable=False)
    code: Mapped[str] = mapped_column(String(50), nullable=False)
    length_km: Mapped[float | None] = mapped_column(Numeric(8, 2))
    station_count: Mapped[int | None] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    program: Mapped["Program"] = relationship(back_populates="corridors")
    packages: Mapped[list["Package"]] = relationship(back_populates="corridor", lazy="selectin")


class Package(Base):
    """
    A contract awarded to a contractor for a section of a corridor.
    E.g., 'CC-07: Tunneling from Station A to Station B'.
    Primary unit of work tracking. RBAC scopes to package.
    """
    __tablename__ = "packages"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    corridor_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("corridors.id"), nullable=False)
    contract_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("contracts.id"))
    name: Mapped[str] = mapped_column(String(300), nullable=False)
    code: Mapped[str] = mapped_column(String(50), nullable=False)  # e.g., CC-07
    description: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    corridor: Mapped["Corridor"] = relationship(back_populates="packages")
    contract: Mapped["Contract | None"] = relationship(back_populates="package")


class Contract(Base):
    """
    Legal backbone. Per expert AS06: supports all FIDIC contract types.
    Notice rules, time-bar, LD formula, EOT methodology are all per-contract.
    """
    __tablename__ = "contracts"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    contract_number: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    contract_standard: Mapped[str] = mapped_column(
        SAEnum(ContractStandard, name="contract_standard_enum", create_constraint=True),
        nullable=False
    )
    contract_value: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False)
    revised_value: Mapped[float | None] = mapped_column(Numeric(15, 2))
    commencement_date: Mapped[date] = mapped_column(Date, nullable=False)
    completion_date: Mapped[date] = mapped_column(Date, nullable=False)
    dlp_months: Mapped[int] = mapped_column(Integer, nullable=False)
    eot_methodology: Mapped[str] = mapped_column(
        SAEnum(EOTMethodology, name="eot_methodology_enum", create_constraint=True),
        nullable=False
    )
    ld_formula: Mapped[dict | None] = mapped_column(JSON)  # {rate_per_day, cap %}
    notice_rules: Mapped[dict | None] = mapped_column(JSON)  # per contract_standard
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    package: Mapped["Package | None"] = relationship(back_populates="contract", uselist=False)


class Organization(Base):
    """Party registry: Owner, Contractors, PMC, Vendors, OEMs, Regulatory."""
    __tablename__ = "organizations"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    org_type: Mapped[str] = mapped_column(
        SAEnum(OrgType, name="org_type_enum", create_constraint=True), nullable=False
    )
    org_name: Mapped[str] = mapped_column(String(300), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    persons: Mapped[list["Person"]] = relationship(back_populates="organization", lazy="selectin")


class Role(Base):
    """
    RBAC role definition. 68 roles defined in CDM.
    For prototype: 5 roles (Contractor SE, Owner AEE, Owner EE, Planning Eng, CPM).
    """
    __tablename__ = "roles"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(200), unique=True, nullable=False)
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    rbac_tier: Mapped[str] = mapped_column(
        SAEnum(RBACTier, name="rbac_tier_enum", create_constraint=True), nullable=False
    )
    description: Mapped[str | None] = mapped_column(Text)
    # Which modules this role can access
    module_access: Mapped[list | None] = mapped_column(JSON)  # ["schedule", "quality", ...]
    # Can this role approve workflows?
    can_approve: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)


class Person(Base):
    """
    RBAC identity. Links to Organization and Role.
    Package scoping: null = all packages (executives).
    """
    __tablename__ = "persons"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    org_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("organizations.id"), nullable=False)
    role_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("roles.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    email: Mapped[str | None] = mapped_column(String(200))
    rbac_tier: Mapped[str] = mapped_column(
        SAEnum(RBACTier, name="rbac_tier_enum", create_constraint=True, create_type=False),
        nullable=False
    )
    ai_access_level: Mapped[str] = mapped_column(
        SAEnum(AIAccessLevel, name="ai_access_level_enum", create_constraint=True),
        nullable=False, default=AIAccessLevel.PARTIAL
    )
    # Package scoping — null means access to all packages (for executives)
    package_ids: Mapped[list | None] = mapped_column(JSON)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    # Auth
    hashed_password: Mapped[str | None] = mapped_column(String(500))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    organization: Mapped["Organization"] = relationship(back_populates="persons")
    role: Mapped["Role"] = relationship()