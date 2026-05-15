"""
Seed identity tables: organizations, roles, persons.

Usage (from backend/ directory):
    python -m seeds.identity_seed

Idempotent. Deterministic UUIDs — stable across environments.
"""
from __future__ import annotations

import asyncio
import uuid
from datetime import datetime, timezone

from sqlalchemy import select

from app.core.database import SessionLocal as _session_factory
from app.models_v2.identity import Organization, Role, Person
from app.core.enums import OrgType, RBACTier, AIAccessLevel


NS = uuid.NAMESPACE_DNS


def did(prefix: str, value: str) -> uuid.UUID:
    return uuid.uuid5(NS, f"aipms.identity.{prefix}.{value}")


ORG_SEEDS = [
    ("owner",      OrgType.OWNER,      "DMRC (Delhi Metro Rail Corporation)"),
    ("contractor", OrgType.CONTRACTOR, "L&T Metro Rail Contractor"),
    ("pmc",        OrgType.PMC,        "AECOM PMC Consortium"),
    ("client",     OrgType.OWNER,      "Ministry of Housing & Urban Affairs"),
]

ROLE_SEEDS = [
    ("SUPERADMIN",                "Super Administrator",                  RBACTier.L1, AIAccessLevel.FULL),
    ("OWNER_MANAGING_DIRECTOR",   "Owner — Managing Director (OE)",       RBACTier.L5, AIAccessLevel.FULL),
    ("OWNER_DIRECTOR_FINANCE",    "Owner — Director (Finance)",           RBACTier.L5, AIAccessLevel.FULL),
    ("OWNER_DIRECTOR_TECHNICAL",  "Owner — Director (E&M/Technical)",     RBACTier.L5, AIAccessLevel.FULL),
    ("OWNER_CHIEF_PM",            "Owner — Chief Project Manager",        RBACTier.L5, AIAccessLevel.FULL),
    ("OWNER_GENERAL_MGR",         "Owner — General Manager",              RBACTier.L5, AIAccessLevel.FULL),
    ("OWNER_EXECUTIVE_ENG",       "Owner — Executive Engineer",           RBACTier.L4, AIAccessLevel.PARTIAL),
    ("OWNER_QC_MANAGER",          "Owner — Quality Control Manager",      RBACTier.L4, AIAccessLevel.FULL),
    ("OWNER_SITE_ENG_INSPECTOR",  "Owner — Site Engineer / Inspector",    RBACTier.L4, AIAccessLevel.PARTIAL),
    ("OWNER_QUANTITY_SURVEYOR",   "Owner — Quantity Surveyor",            RBACTier.L4, AIAccessLevel.PARTIAL),
    ("OWNER_CHIEF_PLANNING_ENG",  "Owner — Chief Planning Engineer",      RBACTier.L4, AIAccessLevel.PARTIAL),
    ("OWNER_COST_CONTROL_ENG",    "Owner — Cost Control Engineer",        RBACTier.L4, AIAccessLevel.PARTIAL),
    ("OWNER_CHIEF_SAFETY",        "Owner — Chief Safety Officer",         RBACTier.L4, AIAccessLevel.PARTIAL),
    ("OWNER_CHIEF_CONTRACT_MGR",  "Owner — Chief Contract Manager",       RBACTier.L4, AIAccessLevel.PARTIAL),
    ("OWNER_DESIGN_MGR",          "Owner — Design Manager",               RBACTier.L4, AIAccessLevel.PARTIAL),
    ("OWNER_BIM_MGR",             "Owner — BIM Manager",                  RBACTier.L4, AIAccessLevel.PARTIAL),
    ("OWNER_FINANCE_MGR",         "Owner — Finance Manager",              RBACTier.L4, AIAccessLevel.PARTIAL),
    ("OWNER_TENDER_MGR",          "Owner — Tender Manager",               RBACTier.L4, AIAccessLevel.PARTIAL),
    ("OWNER_LOGISTICS_MGR",       "Owner — Logistics Manager",            RBACTier.L4, AIAccessLevel.PARTIAL),
    ("OWNER_AEE_JE",              "Owner — Asst. Exec. Eng / Junior Eng", RBACTier.L4, AIAccessLevel.LIMITED),
    ("OWNER_PLANNING_ENG",        "Owner — Planning Engineer",            RBACTier.L2, AIAccessLevel.PARTIAL),
    ("OWNER_CONTRACT_ENG",        "Owner — Contract Engineer",            RBACTier.L3, AIAccessLevel.LIMITED),
    ("CONTRACTOR_PM",             "Contractor — Project Manager",         RBACTier.L3, AIAccessLevel.PARTIAL),
    ("CONTRACTOR_SITE_ENG",       "Contractor — Site Engineer",           RBACTier.L3, AIAccessLevel.LIMITED),
    ("CONTRACTOR_QC_LEAD",        "Contractor — QC Lead",                 RBACTier.L3, AIAccessLevel.LIMITED),
    ("PMC_REVIEWER",              "PMC — Reviewer",                       RBACTier.L6, AIAccessLevel.LIMITED),
    ("CLIENT_REVIEWER",           "Client — Reviewer",                    RBACTier.L6, AIAccessLevel.LIMITED),
]

PERSON_SEEDS = [
    ("SUPERADMIN",                "Admin (System)",   "admin@aipms.local",       "owner"),
    ("OWNER_MANAGING_DIRECTOR",   "Dr. R. Menon",     "rmenon@dmrc.in",          "owner"),
    ("OWNER_DIRECTOR_FINANCE",    "S. Banerjee",      "sbanerjee@dmrc.in",       "owner"),
    ("OWNER_DIRECTOR_TECHNICAL",  "G. Pillai",        "gpillai@dmrc.in",         "owner"),
    ("OWNER_CHIEF_PM",            "R. Sharma",        "rsharma@dmrc.in",         "owner"),
    ("OWNER_GENERAL_MGR",         "A. Verma",         "averma@dmrc.in",          "owner"),
    ("OWNER_EXECUTIVE_ENG",       "S. Kumar",         "skumar@dmrc.in",          "owner"),
    ("OWNER_QC_MANAGER",          "P. Iyer",          "piyer@dmrc.in",           "owner"),
    ("OWNER_SITE_ENG_INSPECTOR",  "M. Singh",         "msingh@dmrc.in",          "owner"),
    ("OWNER_QUANTITY_SURVEYOR",   "N. Rao",           "nrao@dmrc.in",            "owner"),
    ("OWNER_CHIEF_PLANNING_ENG",  "T. Chatterjee",    "tchatterjee@dmrc.in",     "owner"),
    ("OWNER_COST_CONTROL_ENG",    "H. Reddy",         "hreddy@dmrc.in",          "owner"),
    ("OWNER_CHIEF_SAFETY",        "L. Fernandes",     "lfernandes@dmrc.in",      "owner"),
    ("OWNER_CHIEF_CONTRACT_MGR",  "I. Bose",          "ibose@dmrc.in",           "owner"),
    ("OWNER_DESIGN_MGR",          "C. Nair",          "cnair@dmrc.in",           "owner"),
    ("OWNER_BIM_MGR",             "U. Saxena",        "usaxena@dmrc.in",         "owner"),
    ("OWNER_FINANCE_MGR",         "F. Kapoor",        "fkapoor@dmrc.in",         "owner"),
    ("OWNER_TENDER_MGR",          "Q. Bhatt",         "qbhatt@dmrc.in",          "owner"),
    ("OWNER_LOGISTICS_MGR",       "E. Das",           "edas@dmrc.in",            "owner"),
    ("OWNER_AEE_JE",              "W. Khan",          "wkhan@dmrc.in",           "owner"),
    ("OWNER_PLANNING_ENG",        "K. Joshi",         "kjoshi@dmrc.in",          "owner"),
    ("OWNER_CONTRACT_ENG",        "O. Gupta",         "ogupta@dmrc.in",          "owner"),
    ("CONTRACTOR_PM",             "Y. Choudhury",     "ychoudhury@lntmetro.in",  "contractor"),
    ("CONTRACTOR_SITE_ENG",       "D. Patel",         "dpatel@lntmetro.in",      "contractor"),
    ("CONTRACTOR_QC_LEAD",        "V. Mehta",         "vmehta@lntmetro.in",      "contractor"),
    ("PMC_REVIEWER",              "J. Anderson",      "janderson@aecom.com",     "pmc"),
    ("CLIENT_REVIEWER",           "B. Krishnan",      "bkrishnan@mohua.gov.in",  "client"),
]


async def seed() -> None:
    async with _session_factory() as db:
        org_id_by_code: dict[str, uuid.UUID] = {}
        for code, org_type, name in ORG_SEEDS:
            oid = did("org", code)
            org_id_by_code[code] = oid
            if (await db.execute(select(Organization).where(Organization.org_id == oid))).scalar_one_or_none():
                continue
            db.add(Organization(org_id=oid, org_type=org_type, org_name=name,
                                created_at=datetime.now(tz=timezone.utc)))
        await db.flush()

        role_id_by_code: dict[str, uuid.UUID] = {}
        for code, name, tier, ai_acc in ROLE_SEEDS:
            rid = did("role", code)
            role_id_by_code[code] = rid
            if (await db.execute(select(Role).where(Role.role_id == rid))).scalar_one_or_none():
                continue
            db.add(Role(role_id=rid, role_code=code, role_name=name,
                        rbac_tier=tier, ai_access_level=ai_acc, description=None))
        await db.flush()

        person_id_by_role: dict[str, uuid.UUID] = {}
        for role_code, name, email, org_code in PERSON_SEEDS:
            pid = did("person", role_code)
            person_id_by_role[role_code] = pid
            if (await db.execute(select(Person).where(Person.person_id == pid))).scalar_one_or_none():
                continue
            tier   = next(t  for c, _n, t,  _ai in ROLE_SEEDS if c == role_code)
            ai_acc = next(ai for c, _n, _t, ai  in ROLE_SEEDS if c == role_code)
            db.add(Person(person_id=pid, org_id=org_id_by_code[org_code], name=name,
                          email=email, role_id=role_id_by_code[role_code], rbac_tier=tier,
                          packages=None, ai_access_level=ai_acc, is_active=True,
                          created_at=datetime.now(tz=timezone.utc)))

        await db.commit()

        print("\n=== Seeded Identity ===")
        print(f"  Orgs:    {len(org_id_by_code)}")
        print(f"  Roles:   {len(role_id_by_code)}")
        print(f"  Persons: {len(person_id_by_role)}")
        print("\nX-User-ID values:")
        for role_code, pid in person_id_by_role.items():
            print(f"  {role_code:30s} {pid}")
        print()


if __name__ == "__main__":
    asyncio.run(seed())
