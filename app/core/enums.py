"""
CDM Enums — Single source of truth for all enumerated types.

Every ENUM in the CDM is defined here. SQLAlchemy models and Pydantic schemas
both import from this file. Adding a new enum value is a one-place change.
"""

import enum


# === Layer 0: Foundation ===

class SubsystemType(str, enum.Enum):
    """Per expert AS01: all rail subsystems are first-class. Extensible per instance config."""
    CIVIL = "CIVIL"
    ELEC = "ELEC"
    SIG = "SIG"
    TEL = "TEL"
    TVS = "TVS"
    BMS = "BMS"
    SCADA = "SCADA"
    TRACK = "TRACK"
    RS = "RS"
    AFC = "AFC"
    PSD = "PSD"
    DRAINAGE = "DRAINAGE"
    FIRE_ALARM = "FIRE_ALARM"
    TRACTION_POWER = "TRACTION_POWER"
    OHE = "OHE"
    EARTHWORK = "EARTHWORK"
    BRIDGE = "BRIDGE"
    TUNNEL = "TUNNEL"


class SubsystemCategory(str, enum.Enum):
    CIVIL_WORKS = "CIVIL_WORKS"
    E_AND_M = "E_AND_M"
    SYSTEMS = "SYSTEMS"
    ROLLING_STOCK = "ROLLING_STOCK"


class ContractStandard(str, enum.Enum):
    """Per expert AS06: FIDIC covers all contract types."""
    FIDIC_RED = "FIDIC_RED"
    FIDIC_YELLOW = "FIDIC_YELLOW"
    FIDIC_SILVER = "FIDIC_SILVER"
    FIDIC_GOLD = "FIDIC_GOLD"
    IR_GCC = "IR_GCC"
    IR_SCC = "IR_SCC"
    CUSTOM = "CUSTOM"


class EOTMethodology(str, enum.Enum):
    PROSPECTIVE = "PROSPECTIVE"
    IMPACTED_AS_PLANNED = "IMPACTED_AS_PLANNED"
    WINDOWS = "WINDOWS"
    TIA = "TIA"


class OrgType(str, enum.Enum):
    OWNER = "OWNER"
    CONTRACTOR = "CONTRACTOR"
    SUBCONTRACTOR = "SUBCONTRACTOR"
    PMC = "PMC"
    VENDOR = "VENDOR"
    OEM = "OEM"
    REGULATORY = "REGULATORY"
    TPI = "TPI"


class RBACTier(str, enum.Enum):
    """6-tier RBAC per Method Statement Section 14.1"""
    L1 = "L1"  # Administrative (System Admin, IT)
    L2 = "L2"  # Write access (Planning Eng, PM)
    L3 = "L3"  # Write access (Planning Eng, PM) — overlaps with L2 per doc
    L4 = "L4"  # High-volume site (Site Mgr, Supervisors)
    L5 = "L5"  # Read-only executive (MD, CPM)
    L6 = "L6"  # Restricted external (Vendors, Consultants)


class AIAccessLevel(str, enum.Enum):
    FULL = "FULL"
    PARTIAL = "PARTIAL"
    LIMITED = "LIMITED"
    NONE = "NONE"
    META_AI = "META_AI"


# === Layer 1: Operational Core ===

class ActivityType(str, enum.Enum):
    TASK = "TASK"
    MILESTONE = "MILESTONE"
    SUMMARY = "SUMMARY"
    LOE = "LOE"
    WBS_SUMMARY = "WBS_SUMMARY"


class ActivityStatus(str, enum.Enum):
    NOT_STARTED = "NOT_STARTED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    SUSPENDED = "SUSPENDED"


class DependencyType(str, enum.Enum):
    FS = "FS"  # Finish-to-Start
    SS = "SS"
    FF = "FF"
    SF = "SF"


class BaselineStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    SUBMITTED = "SUBMITTED"
    UNDER_REVIEW = "UNDER_REVIEW"
    APPROVED = "APPROVED"
    LOCKED = "LOCKED"
    SUPERSEDED = "SUPERSEDED"


class RFIStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    SUBMITTED = "SUBMITTED"
    ASSIGNED = "ASSIGNED"
    INSPECTED = "INSPECTED"
    APPROVED = "APPROVED"
    COMMENTED = "COMMENTED"
    REJECTED = "REJECTED"
    CLOSED = "CLOSED"


class RFIResult(str, enum.Enum):
    APPROVED = "APPROVED"
    APPROVED_WITH_COMMENTS = "APPROVED_WITH_COMMENTS"
    REJECTED = "REJECTED"


class InitiatorRole(str, enum.Enum):
    """Per expert W02: RFI initiator is not just Site Eng."""
    SITE_ENG = "SITE_ENG"
    PLANNING_ENG = "PLANNING_ENG"
    CONTRACTOR_SE = "CONTRACTOR_SE"


class RoutingTargetType(str, enum.Enum):
    """Per expert W02: RFIs route externally, not just internal owner."""
    OWNER_INTERNAL = "OWNER_INTERNAL"
    PMC = "PMC"
    CLIENT = "CLIENT"


class DPRStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    SUBMITTED = "SUBMITTED"
    REVIEWED = "REVIEWED"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class ITPStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    APPROVED = "APPROVED"
    ACTIVE = "ACTIVE"
    CLOSED = "CLOSED"


# === Layer 4: Audit ===

class AuditAction(str, enum.Enum):
    CREATE = "CREATE"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    STATUS_CHANGE = "STATUS_CHANGE"
    APPROVAL = "APPROVAL"
    REJECTION = "REJECTION"
    CONFIG_RELOAD = "CONFIG_RELOAD"
    LOGIN = "LOGIN"
    LOGOUT = "LOGOUT"