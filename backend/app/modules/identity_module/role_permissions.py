"""Role → ProcurementFeature mapping.

Per XLSX Sheet 4 Procurement column: Logistics Manager is the
primary owner (Stores, inventory, supplier orders); Tender Manager
co-owns (bid comparison, vendor selection); Chief Contract Manager
owns vendor contracts; BIM/Design own specs; QC owns inspection
acceptance; Contractor PM owns own material receipts.
"""
from app.core.enums import ProcurementFeature as F


SUPERADMIN_SENTINEL = "*"


_FULL_RW = set(F)


_READ_ALL = {
    F.DASHBOARD_VIEW_EXEC,
    F.PO_VIEW, F.GR_VIEW, F.MATERIAL_LINK_VIEW,
    F.VENDOR_SCORECARD_VIEW, F.BID_COMPARE_VIEW, F.SPEC_VIEW,
}


ROLE_PERMISSIONS: dict[str, set[F] | str] = {
    "SUPERADMIN": SUPERADMIN_SENTINEL,

    # Executive — read-only
    "OWNER_MANAGING_DIRECTOR":   _READ_ALL,
    "OWNER_DIRECTOR_FINANCE":    _READ_ALL,
    "OWNER_DIRECTOR_TECHNICAL":  _READ_ALL,
    "OWNER_GENERAL_MGR":         _READ_ALL,
    "CLIENT_REVIEWER":           _READ_ALL,
    "OWNER_CHIEF_PM":            _FULL_RW,

    # Logistics Manager — PRIMARY OWNER
    "OWNER_LOGISTICS_MGR": {
        F.DASHBOARD_VIEW_LOGISTICS,
        F.PO_VIEW, F.PO_CREATE, F.PO_APPROVE, F.PO_AMEND,
        F.GR_VIEW, F.GR_CREATE, F.GR_INSPECT,
        F.MATERIAL_LINK_VIEW, F.MATERIAL_LINK_EDIT,
        F.VENDOR_SCORECARD_VIEW, F.BID_COMPARE_VIEW, F.SPEC_VIEW,
    },

    # Tender Manager
    "OWNER_TENDER_MGR": {
        F.DASHBOARD_VIEW_TENDER,
        F.PO_VIEW, F.PO_CREATE,
        F.VENDOR_SCORECARD_VIEW, F.BID_COMPARE_VIEW, F.SPEC_VIEW,
    },

    # Contract — vendor contracts + PO amendments
    "OWNER_CHIEF_CONTRACT_MGR": {
        F.DASHBOARD_VIEW_CONTRACT,
        F.PO_VIEW, F.PO_CREATE, F.PO_APPROVE, F.PO_AMEND,
        F.GR_VIEW, F.MATERIAL_LINK_VIEW,
        F.VENDOR_SCORECARD_VIEW, F.BID_COMPARE_VIEW,
    },
    "OWNER_CONTRACT_ENG": {
        F.DASHBOARD_VIEW_CONTRACT,
        F.PO_VIEW, F.GR_VIEW, F.MATERIAL_LINK_VIEW,
        F.VENDOR_SCORECARD_VIEW, F.SPEC_VIEW,
    },

    # BIM / Design — material specs
    "OWNER_BIM_MGR": {
        F.DASHBOARD_VIEW_BIM,
        F.PO_VIEW, F.MATERIAL_LINK_VIEW, F.SPEC_VIEW,
    },
    "OWNER_DESIGN_MGR": {
        F.DASHBOARD_VIEW_BIM,
        F.PO_VIEW, F.MATERIAL_LINK_VIEW, F.SPEC_VIEW,
    },

    # QC — material inspection
    "OWNER_QC_MANAGER": {
        F.DASHBOARD_VIEW_EXEC,
        F.PO_VIEW, F.GR_VIEW, F.GR_INSPECT,
        F.MATERIAL_LINK_VIEW, F.SPEC_VIEW,
    },
    "OWNER_SITE_ENG_INSPECTOR": {
        F.DASHBOARD_VIEW_EXEC,
        F.GR_VIEW, F.GR_CREATE, F.GR_INSPECT,
        F.MATERIAL_LINK_VIEW,
    },

    # Finance — cost impact only
    "OWNER_FINANCE_MGR": {
        F.DASHBOARD_VIEW_EXEC,
        F.PO_VIEW, F.GR_VIEW, F.MATERIAL_LINK_VIEW,
    },
    "OWNER_COST_CONTROL_ENG": {
        F.DASHBOARD_VIEW_EXEC,
        F.PO_VIEW, F.GR_VIEW, F.MATERIAL_LINK_VIEW,
    },
    "OWNER_QUANTITY_SURVEYOR": {
        F.PO_VIEW, F.GR_VIEW,
    },

    # Senior ops
    "OWNER_EXECUTIVE_ENG": {
        F.DASHBOARD_VIEW_EXEC,
        F.PO_VIEW, F.PO_AMEND,
        F.GR_VIEW, F.GR_CREATE,
        F.MATERIAL_LINK_VIEW, F.MATERIAL_LINK_EDIT,
        F.VENDOR_SCORECARD_VIEW,
    },
    "OWNER_CHIEF_PLANNING_ENG": {
        F.DASHBOARD_VIEW_EXEC,
        F.PO_VIEW, F.GR_VIEW, F.MATERIAL_LINK_VIEW,
    },
    "OWNER_AEE_JE": {
        F.DASHBOARD_VIEW_EXEC,
        F.PO_VIEW, F.GR_VIEW, F.GR_CREATE,
        F.MATERIAL_LINK_VIEW,
    },

    # Contractor
    "CONTRACTOR_PM": {
        F.DASHBOARD_VIEW_CONTRACTOR,
        F.PO_VIEW, F.GR_VIEW, F.GR_CREATE,
        F.MATERIAL_LINK_VIEW,
    },
    "CONTRACTOR_SITE_ENG": {
        F.DASHBOARD_VIEW_CONTRACTOR,
        F.GR_VIEW, F.GR_CREATE,
        F.MATERIAL_LINK_VIEW,
    },
    "CONTRACTOR_QC_LEAD": {
        F.DASHBOARD_VIEW_CONTRACTOR,
        F.GR_VIEW, F.GR_INSPECT,
        F.SPEC_VIEW,
    },

    # PMC
    "PMC_REVIEWER": {
        F.DASHBOARD_VIEW_PMC,
        F.PO_VIEW, F.GR_VIEW, F.GR_INSPECT,
        F.MATERIAL_LINK_VIEW, F.SPEC_VIEW,
    },

    # Misc — module not heavily assigned per XLSX
    "OWNER_PLANNING_ENG":         {F.PO_VIEW, F.GR_VIEW},
    "OWNER_CHIEF_SAFETY":         {F.PO_VIEW, F.GR_VIEW, F.SPEC_VIEW},
}


def features_for_role(role_code: str) -> list[str]:
    perm = ROLE_PERMISSIONS.get(role_code)
    if perm == SUPERADMIN_SENTINEL:
        return ["*"]
    if perm is None or not perm:
        return []
    return sorted(f.value for f in perm)


def is_superadmin(role_code: str) -> bool:
    return ROLE_PERMISSIONS.get(role_code) == SUPERADMIN_SENTINEL


def role_has_feature(role_code: str, feature: str) -> bool:
    if is_superadmin(role_code):
        return True
    return feature in features_for_role(role_code)


# Dashboard view per role (7 views, logistics is own view)
ROLE_DASHBOARD_VIEW: dict[str, str] = {
    "SUPERADMIN":                "exec",
    "OWNER_MANAGING_DIRECTOR":   "exec",
    "OWNER_DIRECTOR_FINANCE":    "exec",
    "OWNER_DIRECTOR_TECHNICAL":  "exec",
    "OWNER_CHIEF_PM":            "exec",
    "OWNER_GENERAL_MGR":         "exec",
    "CLIENT_REVIEWER":           "exec",
    "OWNER_QC_MANAGER":          "exec",
    "OWNER_SITE_ENG_INSPECTOR":  "exec",
    "OWNER_FINANCE_MGR":         "exec",
    "OWNER_COST_CONTROL_ENG":    "exec",
    "OWNER_EXECUTIVE_ENG":       "exec",
    "OWNER_CHIEF_PLANNING_ENG":  "exec",
    "OWNER_AEE_JE":              "exec",
    "OWNER_CHIEF_SAFETY":        "exec",

    "OWNER_LOGISTICS_MGR":       "logistics",

    "OWNER_TENDER_MGR":          "tender",

    "OWNER_BIM_MGR":             "bim",
    "OWNER_DESIGN_MGR":          "bim",

    "OWNER_CHIEF_CONTRACT_MGR":  "contract",
    "OWNER_CONTRACT_ENG":        "contract",

    "CONTRACTOR_PM":             "contractor",
    "CONTRACTOR_SITE_ENG":       "contractor",
    "CONTRACTOR_QC_LEAD":        "contractor",

    "PMC_REVIEWER":              "pmc",
}
