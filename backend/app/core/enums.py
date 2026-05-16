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


class BaselineType(str, enum.Enum):
    """CDM v1.2: distinguishes contractual programme revisions for arbitration traceability."""
    ORIGINAL = "ORIGINAL"
    REVISED = "REVISED"
    CONTRACTOR_RECOVERY = "CONTRACTOR_RECOVERY"
    AGREED_REBASELINE = "AGREED_REBASELINE"


class EVSource(str, enum.Enum):
    """CDM v1.2 Q07: EVM earned value must declare its progress data source."""
    RFI_VERIFIED = "RFI_VERIFIED"
    P6_SELF_REPORTED = "P6_SELF_REPORTED"
    BLENDED = "BLENDED"


class EVMPeriodType(str, enum.Enum):
    MONTHLY = "MONTHLY"
    WEEKLY = "WEEKLY"
    SNAPSHOT = "SNAPSHOT"


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


# === Quality Module ===

class CheckpointType(str, enum.Enum):
    HOLD = "HOLD"
    WITNESS = "WITNESS"
    REVIEW = "REVIEW"


class NCRStatus(str, enum.Enum):
    OPEN = "OPEN"
    UNDER_REVIEW = "UNDER_REVIEW"
    CORRECTIVE_ACTION = "CORRECTIVE_ACTION"
    RE_INSPECTION = "RE_INSPECTION"
    CLOSED = "CLOSED"
    ACCEPTED_AS_IS = "ACCEPTED_AS_IS"


class NCRSeverity(str, enum.Enum):
    CRITICAL = "CRITICAL"
    MAJOR = "MAJOR"
    MINOR = "MINOR"
    OBSERVATION = "OBSERVATION"


class ChecklistResult(str, enum.Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    NA = "NA"


class TestRecordResult(str, enum.Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    PARTIAL = "PARTIAL"


class PunchItemStatus(str, enum.Enum):
    IDENTIFIED = "IDENTIFIED"
    ASSIGNED = "ASSIGNED"
    IN_PROGRESS = "IN_PROGRESS"
    VERIFIED = "VERIFIED"
    CLOSED = "CLOSED"


# === EVM (Earned Value Management) ===

class EVMSnapshotType(str, enum.Enum):
    """Type of EVM snapshot — frozen at different points in time."""
    BASELINE = "BASELINE"  # Frozen at baseline lock date
    ACTUAL = "ACTUAL"      # Current progress vs baseline
    PERIODIC = "PERIODIC"  # Scheduled/manual periodic snapshot


# === Cost Module ===

class BOQStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    APPROVED = "APPROVED"
    SUPERSEDED = "SUPERSEDED"


class BOQSource(str, enum.Enum):
    MANUAL = "MANUAL"
    XER_IMPORT = "XER_IMPORT"
    CSV_IMPORT = "CSV_IMPORT"


class RABillStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    SUBMITTED = "SUBMITTED"
    QS_VERIFIED = "QS_VERIFIED"
    EE_RECOMMENDED = "EE_RECOMMENDED"
    GM_APPROVED = "GM_APPROVED"
    CPM_APPROVED = "CPM_APPROVED"
    FINANCE_PROCESSED = "FINANCE_PROCESSED"
    PAID = "PAID"


class VOCostStatus(str, enum.Enum):
    IDENTIFIED = "IDENTIFIED"
    SUBMITTED = "SUBMITTED"
    ASSESSED = "ASSESSED"
    RECOMMENDED = "RECOMMENDED"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    IMPLEMENTED = "IMPLEMENTED"


class VOTriggerType(str, enum.Enum):
    SCOPE_CHANGE = "SCOPE_CHANGE"
    DESIGN_CHANGE = "DESIGN_CHANGE"
    UNFORESEEN_CONDITION = "UNFORESEEN_CONDITION"
    REGULATORY = "REGULATORY"
    OWNER_INSTRUCTION = "OWNER_INSTRUCTION"


class CashFlowPeriod(str, enum.Enum):
    MONTHLY = "MONTHLY"
    QUARTERLY = "QUARTERLY"


# === Governance / Approval ===

class ApprovalChainStatus(str, enum.Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    REJECTED = "REJECTED"


# === Structure ===

class PackageStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    SUSPENDED = "SUSPENDED"


# === Quality — Punch Items ===

class PunchItemCategory(str, enum.Enum):
    A = "A"
    B = "B"
    C = "C"


# === Reporting Module (M09 + M12) ===

class MPRStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    SUBMITTED = "SUBMITTED"
    APPROVED = "APPROVED"


# === Contract ===

class ContractStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    ACTIVE = "ACTIVE"
    SUSPENDED = "SUSPENDED"
    COMPLETED = "COMPLETED"
    TERMINATED = "TERMINATED"


# === Contract Administration Module (M05) ===

class NoticeType(str, enum.Enum):
    DELAY = "DELAY"
    VARIATION = "VARIATION"
    CLAIM = "CLAIM"
    FORCE_MAJEURE = "FORCE_MAJEURE"
    TERMINATION = "TERMINATION"
    GENERAL = "GENERAL"


class NoticeStatus(str, enum.Enum):
    DRAFTED = "DRAFTED"
    ISSUED = "ISSUED"
    ACKNOWLEDGED = "ACKNOWLEDGED"
    RESPONDED = "RESPONDED"
    TIME_BARRED = "TIME_BARRED"
    DISPUTED = "DISPUTED"


class ObligationType(str, enum.Enum):
    RECURRING = "RECURRING"
    MILESTONE = "MILESTONE"
    CONDITIONAL = "CONDITIONAL"


class ObligationStatus(str, enum.Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    OVERDUE = "OVERDUE"
    WAIVED = "WAIVED"


class CorrespondenceDirection(str, enum.Enum):
    INBOUND = "INBOUND"
    OUTBOUND = "OUTBOUND"


class CorrespondenceStatus(str, enum.Enum):
    SENT = "SENT"
    RECEIVED = "RECEIVED"
    ACKNOWLEDGED = "ACKNOWLEDGED"


# === Document Management Module ===

class DocumentType(str, enum.Enum):
    DRAWING = "DRAWING"
    SPECIFICATION = "SPECIFICATION"
    METHOD_STATEMENT = "METHOD_STATEMENT"
    MIX_DESIGN = "MIX_DESIGN"
    SHOP_DRAWING = "SHOP_DRAWING"
    TEST_CERTIFICATE = "TEST_CERTIFICATE"
    NCR = "NCR"
    RFI = "RFI"
    CORRESPONDENCE = "CORRESPONDENCE"
    PHOTO = "PHOTO"
    VIDEO = "VIDEO"
    OTHER = "OTHER"


class DocumentStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    UNDER_REVIEW = "UNDER_REVIEW"
    APPROVED = "APPROVED"
    SUPERSEDED = "SUPERSEDED"
    ARCHIVED = "ARCHIVED"


class DocApprovalStatus(str, enum.Enum):
    PENDING = "PENDING"
    REVIEWED = "REVIEWED"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class TransmittalStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    ISSUED = "ISSUED"
    ACKNOWLEDGED = "ACKNOWLEDGED"


# ─── EHS ─────────────────────────────────────────────────────────

class IncidentType(str, enum.Enum):
    NEAR_MISS = "NEAR_MISS"
    FIRST_AID = "FIRST_AID"
    MTI = "MTI"
    LTI = "LTI"
    FATALITY = "FATALITY"
    PROPERTY_DAMAGE = "PROPERTY_DAMAGE"
    ENVIRONMENTAL = "ENVIRONMENTAL"


class IncidentSeverity(str, enum.Enum):
    MINOR = "MINOR"
    MODERATE = "MODERATE"
    SERIOUS = "SERIOUS"
    MAJOR = "MAJOR"
    CRITICAL = "CRITICAL"
    FATAL = "FATAL"


class InvestigationStatus(str, enum.Enum):
    REPORTED = "REPORTED"
    UNDER_INVESTIGATION = "UNDER_INVESTIGATION"
    ROOT_CAUSE = "ROOT_CAUSE"
    CAPA = "CAPA"
    CLOSED = "CLOSED"


class RootCauseMethod(str, enum.Enum):
    FIVE_WHY = "FIVE_WHY"
    FISHBONE = "FISHBONE"
    FAULT_TREE = "FAULT_TREE"
    BOW_TIE = "BOW_TIE"


class PTWCategory(str, enum.Enum):
    HOT_WORK = "HOT_WORK"
    EXCAVATION = "EXCAVATION"
    CONFINED_SPACE = "CONFINED_SPACE"
    ELECTRICAL = "ELECTRICAL"
    WORKING_AT_HEIGHT = "WORKING_AT_HEIGHT"
    LIFTING = "LIFTING"
    DEMOLITION = "DEMOLITION"
    GENERAL = "GENERAL"


class PTWStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    PENDING_APPROVAL = "PENDING_APPROVAL"
    APPROVED = "APPROVED"
    ACTIVE = "ACTIVE"
    EXPIRED = "EXPIRED"
    CANCELLED = "CANCELLED"
    REJECTED = "REJECTED"


class ZoneType(str, enum.Enum):
    STATION = "STATION"
    VIADUCT = "VIADUCT"
    DEPOT = "DEPOT"
    TBM = "TBM"
    WORK_AREA = "WORK_AREA"
    EXCLUSION = "EXCLUSION"
    CASTING_YARD = "CASTING_YARD"


class CAPAStatus(str, enum.Enum):
    OPEN = "OPEN"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    VERIFIED = "VERIFIED"
    OVERDUE = "OVERDUE"


class SHEPlanStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    SUBMITTED = "SUBMITTED"
    APPROVED = "APPROVED"
    SUPERSEDED = "SUPERSEDED"


# ─── Procurement ──────────────────────────────────────────────────

class POStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    ISSUED = "ISSUED"
    ACKNOWLEDGED = "ACKNOWLEDGED"
    IN_TRANSIT = "IN_TRANSIT"
    RECEIVED = "RECEIVED"
    CLOSED = "CLOSED"
    CANCELLED = "CANCELLED"


class MaterialLinkStatus(str, enum.Enum):
    PENDING = "PENDING"
    ON_TRACK = "ON_TRACK"
    AT_RISK = "AT_RISK"
    DELAYED = "DELAYED"
    RECEIVED = "RECEIVED"


# ─── Procurement-specific (Procurement Supply Module) ─────────────

class GRNStatus(str, enum.Enum):
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    PARTIALLY_ACCEPTED = "PARTIALLY_ACCEPTED"
    REJECTED = "REJECTED"


class RiskLevel(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class ProcurementFeature(str, enum.Enum):
    # Dashboard views — logistics is its own view (XLSX: Logistics Manager = primary owner)
    DASHBOARD_VIEW_EXEC = "procurement.dashboard.exec"
    DASHBOARD_VIEW_LOGISTICS = "procurement.dashboard.logistics"
    DASHBOARD_VIEW_TENDER = "procurement.dashboard.tender"
    DASHBOARD_VIEW_BIM = "procurement.dashboard.bim"
    DASHBOARD_VIEW_CONTRACT = "procurement.dashboard.contract"
    DASHBOARD_VIEW_CONTRACTOR = "procurement.dashboard.contractor"
    DASHBOARD_VIEW_PMC = "procurement.dashboard.pmc"

    # PO
    PO_VIEW = "procurement.po.view"
    PO_CREATE = "procurement.po.create"
    PO_APPROVE = "procurement.po.approve"
    PO_AMEND = "procurement.po.amend"

    # GRN
    GR_VIEW = "procurement.gr.view"
    GR_CREATE = "procurement.gr.create"
    GR_INSPECT = "procurement.gr.inspect"

    # Material Link
    MATERIAL_LINK_VIEW = "procurement.material_link.view"
    MATERIAL_LINK_EDIT = "procurement.material_link.edit"

    # Reporting
    VENDOR_SCORECARD_VIEW = "procurement.vendor_scorecard.view"
    BID_COMPARE_VIEW = "procurement.bid_compare.view"
    SPEC_VIEW = "procurement.spec.view"
