"""
Seed schedule tables: XERImport, Project, Calendar, WBS, Resource,
Contract, Corridor, Package, Baseline, BaselineHistory, Activity (30),
Relationship, Dependency, ActivityBaselineLink, EVMSnapshot.

DMRC Phase IV — Delhi Metro Construction (realistic enterprise data).

Usage (from backend/ directory):
    python -m seeds.schedule_seed

Idempotent. Deterministic UUIDs. Run BEFORE quality_seed / cost_seed.
All six module repos share one Supabase DB — only needs to run once total.
"""
from __future__ import annotations

import asyncio
import uuid
from datetime import datetime, date, timezone, timedelta

from sqlalchemy import select

from app.core.database import async_session as async_session_factory
from app.models_v2.schedule import (
    XERImport, Project, Calendar, WBS, Resource,
    Activity, Relationship, ResourceAssignment, Dependency,
)
from app.models_v2.structure import Corridor, Package
from app.models_v2.contract import Contract
from app.models_v2.baseline import (
    Baseline, BaselineHistory, ActivityBaselineLink, EVMSnapshot,
)
from app.core.enums import (
    ActivityStatus, ActivityType, SubsystemType, DependencyType,
    BaselineStatus, BaselineType, EVMSnapshotType, EVSource, EVMPeriodType,
    ContractStandard, ContractStatus, EOTMethodology, PackageStatus,
)

NS = uuid.NAMESPACE_DNS
NOW = datetime.now(tz=timezone.utc)


def qid(entity: str, code: str) -> uuid.UUID:
    """Mirror of quality_seed.py — same namespace so cross-module FKs resolve."""
    return uuid.uuid5(NS, f"aipms.quality.{entity}.{code}")


def sid(entity: str, code: str) -> uuid.UUID:
    return uuid.uuid5(NS, f"aipms.schedule.{entity}.{code}")


async def _exists(db, model, col, val) -> bool:
    res = await db.execute(select(model).where(col == val))
    return res.scalar_one_or_none() is not None


# ---------------------------------------------------------------------------
# Shared IDs — MUST match quality_seed.py, cost_seed.py exactly
# ---------------------------------------------------------------------------
PKG_CIVIL = qid("package", "PKG-CIVIL-001")
PKG_ELEC  = qid("package", "PKG-ELEC-001")
PKG_SIG   = qid("package", "PKG-SIG-001")

# Original 6 activity IDs — preserved for FK compatibility with quality/cost data
ACT_FOUND  = qid("activity", "ACT-CIVIL-FOUNDATION")
ACT_BRIDGE = qid("activity", "ACT-CIVIL-BRIDGE")
ACT_EARTH  = qid("activity", "ACT-CIVIL-EARTHWORK")
ACT_TRAC   = qid("activity", "ACT-ELEC-TRACTION")
ACT_SIG    = qid("activity", "ACT-SIG-INSTALL")
ACT_TRACK  = qid("activity", "ACT-TRACK-ALIGN")

BASELINE_01 = qid("baseline", "BL-2024-REV0")

# ---------------------------------------------------------------------------
# Schedule-only IDs
# ---------------------------------------------------------------------------
IMPORT_01 = sid("import",   "DMRC-P4-2024-EXPORT")
PROJ_CIVIL = sid("project", "DMRC-P4-CIVIL")
PROJ_EM    = sid("project", "DMRC-P4-EM")
PROJ_SIG   = sid("project", "DMRC-P4-SIG")

CTR_CIVIL  = sid("contract", "DMRC-P4-CC-007")
CTR_EM     = sid("contract", "DMRC-P4-CC-012")
CTR_SIG    = sid("contract", "DMRC-P4-CC-023")

COR_A = sid("corridor", "DMRC-P4-COR-A")
COR_B = sid("corridor", "DMRC-P4-COR-B")

BASELINE_02 = sid("baseline", "BL-ELEC-2024-REV0")
BASELINE_03 = sid("baseline", "BL-SIG-2024-DRAFT")

CAL_6DAY = sid("calendar", "CAL-6DAY-STD")
CAL_7DAY = sid("calendar", "CAL-7DAY-CRIT")

RSC_CIVIL = sid("resource", "RSC-CIVIL-ENG")
RSC_ELEC  = sid("resource", "RSC-ELEC-ENG")
RSC_SIG   = sid("resource", "RSC-SIG-ENG")
RSC_QC    = sid("resource", "RSC-QC-MGR")

# New activity IDs (24 additional)
ACT_PILE_A   = sid("activity", "A-PILE-P01-P15")
ACT_PILE_B   = sid("activity", "A-PILE-P16-P35")
ACT_PIERCAP_A = sid("activity", "A-PIERCAP-P01-P15")
ACT_PIERCAP_B = sid("activity", "A-PIERCAP-P16-P35")
ACT_UGIRDER_CAST = sid("activity", "A-UGIRDER-CAST")
ACT_UGIRDER_S01  = sid("activity", "A-UGIRDER-ERECT-S01-20")
ACT_UGIRDER_S02  = sid("activity", "A-UGIRDER-ERECT-S21-40")
ACT_DECK_SLAB    = sid("activity", "A-DECK-SLAB-CH0-5")
ACT_STN_EXCV     = sid("activity", "A-STN-EXCV-HAUZKHAS")
ACT_STN_STRUCT   = sid("activity", "A-STN-STRUCT-HAUZKHAS")
ACT_STN_ARCH     = sid("activity", "A-STN-ARCH-HAUZKHAS")
ACT_TBM_SHAFT    = sid("activity", "A-TBM-SHAFT")
ACT_TBM_DRIVE1   = sid("activity", "A-TBM-DRIVE1")
ACT_TBM_DRIVE2   = sid("activity", "A-TBM-DRIVE2")
ACT_TUNNEL_INVERT = sid("activity", "A-TUNNEL-INVERT")
ACT_OHE_MAST     = sid("activity", "A-OHE-MAST-CH0-10")
ACT_CATENARY     = sid("activity", "A-CATENARY-WIRE")
ACT_TSS_CIVIL    = sid("activity", "A-TSS-CIVIL-RSS1")
ACT_TSS_EM       = sid("activity", "A-TSS-EM-RSS1")
ACT_STN_LIGHT    = sid("activity", "A-STN-LIGHTING")
ACT_ESCL_LIFT    = sid("activity", "A-ESCALATOR-LIFT")
ACT_OFC_CABLE    = sid("activity", "A-OFC-CABLE")
ACT_ATP_TRACKSIDE = sid("activity", "A-ATP-TRACKSIDE")
ACT_AFC          = sid("activity", "A-AFC-SYSTEM")
ACT_STN_TELECOM  = sid("activity", "A-STN-TELECOM")


async def seed() -> None:
    async with async_session_factory() as db:
        counts: dict[str, int] = {k: 0 for k in [
            "imports", "projects", "calendars", "wbs", "resources", "contracts",
            "corridors", "packages", "baselines", "baseline_history",
            "activities", "relationships", "dependencies", "baseline_links",
            "evm_snapshots",
        ]}

        # ----------------------------------------------------------------
        # 1. Import record
        # ----------------------------------------------------------------
        if not await _exists(db, XERImport, XERImport.id, IMPORT_01):
            db.add(XERImport(
                id=IMPORT_01,
                file_path="/data/imports/DMRC_Phase4_P6_Export_2024.xer",
                total_projects=3, total_activities=30, total_resources=4,
                total_calendars=2, total_wbs=9, total_relationships=12,
                total_corridors=2, total_packages=3,
                parse_response={
                    "status": "SUCCESS",
                    "source": "Primavera P6 R22.12",
                    "project": "DMRC Phase-IV Metro Rail",
                    "parsed_at": str(NOW - timedelta(days=90)),
                    "parser_version": "2.4.1",
                },
                created_at=NOW - timedelta(days=90),
            ))
            counts["imports"] += 1
        await db.flush()

        # ----------------------------------------------------------------
        # 2. Projects
        # ----------------------------------------------------------------
        for p in [
            dict(id=PROJ_CIVIL, import_id=IMPORT_01, proj_id=1001,
                 proj_short_name="DMRC-P4-CIVIL",
                 proj_name="DMRC Phase-IV — Civil & Structural Works",
                 scd_start_date="2024-01-15", scd_end_date="2027-06-30",
                 last_recalc_date="2024-07-01",
                 activity_count=15, completed=5, in_progress=5, not_started=5),
            dict(id=PROJ_EM, import_id=IMPORT_01, proj_id=1002,
                 proj_short_name="DMRC-P4-EM",
                 proj_name="DMRC Phase-IV — Electrical & Mechanical Systems",
                 scd_start_date="2025-01-01", scd_end_date="2027-03-31",
                 last_recalc_date="2024-07-01",
                 activity_count=7, completed=1, in_progress=2, not_started=4),
            dict(id=PROJ_SIG, import_id=IMPORT_01, proj_id=1003,
                 proj_short_name="DMRC-P4-SIG",
                 proj_name="DMRC Phase-IV — Signalling & Telecom",
                 scd_start_date="2025-04-01", scd_end_date="2027-03-31",
                 last_recalc_date="2024-07-01",
                 activity_count=8, completed=1, in_progress=2, not_started=5),
        ]:
            if not await _exists(db, Project, Project.id, p["id"]):
                db.add(Project(**p))
                counts["projects"] += 1
        await db.flush()

        # ----------------------------------------------------------------
        # 3. Calendars
        # ----------------------------------------------------------------
        for c in [
            dict(id=CAL_6DAY, import_id=IMPORT_01, clndr_id=1,
                 clndr_name="Standard 6-Day Week (Mon–Sat)", clndr_type="Global",
                 day_hr_cnt=10.0, week_hr_cnt=60.0,
                 month_hr_cnt=260.0, year_hr_cnt=3120.0),
            dict(id=CAL_7DAY, import_id=IMPORT_01, clndr_id=2,
                 clndr_name="Critical Path 7-Day Week", clndr_type="Global",
                 day_hr_cnt=10.0, week_hr_cnt=70.0,
                 month_hr_cnt=300.0, year_hr_cnt=3640.0),
        ]:
            if not await _exists(db, Calendar, Calendar.id, c["id"]):
                db.add(Calendar(**c))
                counts["calendars"] += 1
        await db.flush()

        # ----------------------------------------------------------------
        # 4. WBS
        # ----------------------------------------------------------------
        for w in [
            dict(id=sid("wbs","WBS-CIVIL-ROOT"),  import_id=IMPORT_01, wbs_id=101, proj_id=1001,
                 wbs_name="DMRC Phase-IV Civil Works",             wbs_short_name="P4-CIV",      parent_wbs_id=None, seq_num=1),
            dict(id=sid("wbs","WBS-CIVIL-FOUND"), import_id=IMPORT_01, wbs_id=102, proj_id=1001,
                 wbs_name="Foundation & Earthwork",                 wbs_short_name="P4-CIV-FND",  parent_wbs_id=101,  seq_num=2),
            dict(id=sid("wbs","WBS-CIVIL-VDT"),   import_id=IMPORT_01, wbs_id=103, proj_id=1001,
                 wbs_name="Viaduct, Stations & TBM Tunnel",         wbs_short_name="P4-CIV-VDT",  parent_wbs_id=101,  seq_num=3),
            dict(id=sid("wbs","WBS-EM-ROOT"),      import_id=IMPORT_01, wbs_id=201, proj_id=1002,
                 wbs_name="DMRC Phase-IV E&M Systems",              wbs_short_name="P4-EM",        parent_wbs_id=None, seq_num=1),
            dict(id=sid("wbs","WBS-EM-TRAC"),      import_id=IMPORT_01, wbs_id=202, proj_id=1002,
                 wbs_name="Traction Power & OHE",                   wbs_short_name="P4-EM-TRC",    parent_wbs_id=201,  seq_num=2),
            dict(id=sid("wbs","WBS-EM-GEN"),       import_id=IMPORT_01, wbs_id=203, proj_id=1002,
                 wbs_name="General Services (Escalators, HVAC)",    wbs_short_name="P4-EM-GEN",    parent_wbs_id=201,  seq_num=3),
            dict(id=sid("wbs","WBS-SIG-ROOT"),     import_id=IMPORT_01, wbs_id=301, proj_id=1003,
                 wbs_name="DMRC Phase-IV Signalling & Telecom",     wbs_short_name="P4-SIG",       parent_wbs_id=None, seq_num=1),
            dict(id=sid("wbs","WBS-SIG-CBTC"),     import_id=IMPORT_01, wbs_id=302, proj_id=1003,
                 wbs_name="CBTC Signalling System",                  wbs_short_name="P4-SIG-CBTC",  parent_wbs_id=301,  seq_num=2),
            dict(id=sid("wbs","WBS-SIG-TELECOM"),  import_id=IMPORT_01, wbs_id=303, proj_id=1003,
                 wbs_name="Telecom & AFC",                           wbs_short_name="P4-SIG-TEL",   parent_wbs_id=301,  seq_num=3),
        ]:
            if not await _exists(db, WBS, WBS.id, w["id"]):
                db.add(WBS(**w))
                counts["wbs"] += 1
        await db.flush()

        # ----------------------------------------------------------------
        # 5. Resources
        # ----------------------------------------------------------------
        for r in [
            dict(id=RSC_CIVIL, import_id=IMPORT_01, rsrc_id=1, rsrc_name="Civil Engineer",        rsrc_short_name="CIV-ENG",  rsrc_type="Labor", email_addr=None,             parent_rsrc_id=None),
            dict(id=RSC_ELEC,  import_id=IMPORT_01, rsrc_id=2, rsrc_name="Electrical Engineer",   rsrc_short_name="ELEC-ENG", rsrc_type="Labor", email_addr=None,             parent_rsrc_id=None),
            dict(id=RSC_SIG,   import_id=IMPORT_01, rsrc_id=3, rsrc_name="Signalling Engineer",   rsrc_short_name="SIG-ENG",  rsrc_type="Labor", email_addr=None,             parent_rsrc_id=None),
            dict(id=RSC_QC,    import_id=IMPORT_01, rsrc_id=4, rsrc_name="QC Manager",            rsrc_short_name="QC-MGR",   rsrc_type="Labor", email_addr="piyer@dmrc.in",  parent_rsrc_id=None),
        ]:
            if not await _exists(db, Resource, Resource.id, r["id"]):
                db.add(Resource(**r))
                counts["resources"] += 1
        await db.flush()

        # ----------------------------------------------------------------
        # 6. Contracts
        # ----------------------------------------------------------------
        for ct in [
            dict(id=CTR_CIVIL, contract_number="DMRC/P4/CC-07/2023",
                 title="Civil Construction — Elevated Viaduct & Stations, Package CC-07",
                 description="Pile foundations, elevated viaduct U-girders, station structures, TBM tunnelling Ch. 0+000–17+000 for DMRC Phase IV Janakpuri–RK Ashram corridor.",
                 status=ContractStatus.ACTIVE, owner_id=None, contractor_id=None,
                 contract_standard=ContractStandard.FIDIC_RED,
                 contract_value=4_800_000_000.00, revised_value=4_956_000_000.00,
                 commencement_date=date(2024, 1, 15), completion_date=date(2027, 6, 30),
                 dlp_months=12, eot_methodology=EOTMethodology.WINDOWS,
                 ld_formula={"rate_per_day": 1_000_000, "cap_pct": 10},
                 notice_rules={"eot_notice_days": 28, "claim_notice_days": 28},
                 created_at=NOW - timedelta(days=500), updated_at=NOW - timedelta(days=30)),
            dict(id=CTR_EM, contract_number="DMRC/P4/CC-12/2023",
                 title="Electrical & Mechanical — Traction Power, OHE & General Services, Package CC-12",
                 description="25kV AC traction power, OHE catenary, TSS, escalators, HVAC, station lighting for DMRC Phase IV.",
                 status=ContractStatus.ACTIVE, owner_id=None, contractor_id=None,
                 contract_standard=ContractStandard.FIDIC_YELLOW,
                 contract_value=2_200_000_000.00, revised_value=None,
                 commencement_date=date(2025, 1, 1), completion_date=date(2027, 3, 31),
                 dlp_months=12, eot_methodology=EOTMethodology.WINDOWS,
                 ld_formula={"rate_per_day": 500_000, "cap_pct": 10},
                 notice_rules={"eot_notice_days": 28, "claim_notice_days": 28},
                 created_at=NOW - timedelta(days=400), updated_at=NOW - timedelta(days=60)),
            dict(id=CTR_SIG, contract_number="DMRC/P4/CC-23/2023",
                 title="Signalling & Telecom — CBTC System, AFC, PIS & Telecom, Package CC-23",
                 description="Alstom CBTC-based ATCS, interlocking, SCADA, AFC fare collection, PIS, and OCC for Phase IV.",
                 status=ContractStatus.ACTIVE, owner_id=None, contractor_id=None,
                 contract_standard=ContractStandard.FIDIC_YELLOW,
                 contract_value=1_800_000_000.00, revised_value=None,
                 commencement_date=date(2025, 4, 1), completion_date=date(2027, 3, 31),
                 dlp_months=24, eot_methodology=EOTMethodology.TIA,
                 ld_formula={"rate_per_day": 400_000, "cap_pct": 10},
                 notice_rules={"eot_notice_days": 21, "claim_notice_days": 21},
                 created_at=NOW - timedelta(days=350), updated_at=NOW - timedelta(days=90)),
        ]:
            existing = await db.execute(
                select(Contract).where(Contract.contract_number == ct["contract_number"])
            )
            if existing.scalar_one_or_none() is None:
                db.add(Contract(**ct))
                counts["contracts"] += 1
        await db.flush()

        # ----------------------------------------------------------------
        # 7. Corridors
        # ----------------------------------------------------------------
        for cor in [
            dict(id=COR_A, import_id=IMPORT_01, proj_id=1001, source_wbs_id=101,
                 corridor_name="Janakpuri West – R.K. Ashram Marg (28.92 km, 22 stations)",
                 corridor_code="P4-COR-JAN-RKA",
                 created_at=NOW - timedelta(days=90), updated_at=NOW - timedelta(days=30)),
            dict(id=COR_B, import_id=IMPORT_01, proj_id=1001, source_wbs_id=101,
                 corridor_name="Aerocity – Tughlakabad (20.2 km, 19 stations)",
                 corridor_code="P4-COR-AER-TUG",
                 created_at=NOW - timedelta(days=90), updated_at=NOW - timedelta(days=30)),
        ]:
            if not await _exists(db, Corridor, Corridor.id, cor["id"]):
                db.add(Corridor(**cor))
                counts["corridors"] += 1
        await db.flush()

        # ----------------------------------------------------------------
        # 8. Packages — IDs MUST match quality_seed PKG_* constants
        # ----------------------------------------------------------------
        for pkg in [
            dict(id=PKG_CIVIL, import_id=IMPORT_01, proj_id=1001,
                 corridor_id=COR_A, contract_id=CTR_CIVIL,
                 source_wbs_id=101, parent_wbs_id=None, parent_package_id=None,
                 package_name="Civil & Structural — Elevated Viaduct & TBM Tunnel (CC-07)",
                 package_code="PKG-CIVIL-001", status=PackageStatus.ACTIVE,
                 contractor_name="L&T Construction (ECC Division)",
                 description="Elevated viaduct piling, U-girder erection, Hauz Khas station civil, TBM tunnelling Ch. 0+000–17+000.",
                 created_at=NOW - timedelta(days=90), updated_at=NOW - timedelta(days=7)),
            dict(id=PKG_ELEC, import_id=IMPORT_01, proj_id=1002,
                 corridor_id=COR_A, contract_id=CTR_EM,
                 source_wbs_id=201, parent_wbs_id=None, parent_package_id=None,
                 package_name="Electrical & Mechanical — Traction Power & General Services (CC-12)",
                 package_code="PKG-ELEC-001", status=PackageStatus.ACTIVE,
                 contractor_name="L&T–Siemens JV (Traction Power)",
                 description="25kV AC traction power OHE, TSS RSS-1 & RSS-2, escalators, lifts, HVAC, station lighting.",
                 created_at=NOW - timedelta(days=90), updated_at=NOW - timedelta(days=14)),
            dict(id=PKG_SIG, import_id=IMPORT_01, proj_id=1003,
                 corridor_id=COR_A, contract_id=CTR_SIG,
                 source_wbs_id=301, parent_wbs_id=None, parent_package_id=None,
                 package_name="Signalling & Telecom — CBTC System (CC-23)",
                 package_code="PKG-SIG-001", status=PackageStatus.ACTIVE,
                 contractor_name="Alstom Transport India Ltd.",
                 description="CBTC ATCS, interlocking, OCC, AFC fare gates & TVMs, PIS, CCTV, PA, station telecom.",
                 created_at=NOW - timedelta(days=90), updated_at=NOW - timedelta(days=21)),
        ]:
            if not await _exists(db, Package, Package.id, pkg["id"]):
                db.add(Package(**pkg))
                counts["packages"] += 1
        await db.flush()

        # ----------------------------------------------------------------
        # 9. Baselines
        # ----------------------------------------------------------------
        for bl in [
            dict(id=BASELINE_01, package_id=PKG_CIVIL,
                 version=1, is_active=True, version_label="BL-2024-REV0",
                 supersedes_id=None, status=BaselineStatus.LOCKED,
                 baseline_type=BaselineType.ORIGINAL,
                 rebaseline_approved_by=None, rebaseline_reason=None,
                 approved_by=None, locked_at=NOW - timedelta(days=80),
                 source_file="/data/imports/DMRC_Phase4_P6_Export_2024.xer",
                 import_hash="a3f2b1c9d8e7f4a2b5c3d1e6f8a9b0c2",
                 created_at=NOW - timedelta(days=90)),
            dict(id=BASELINE_02, package_id=PKG_ELEC,
                 version=1, is_active=True, version_label="BL-ELEC-2024-REV0",
                 supersedes_id=None, status=BaselineStatus.APPROVED,
                 baseline_type=BaselineType.ORIGINAL,
                 rebaseline_approved_by=None, rebaseline_reason=None,
                 approved_by=None, locked_at=None,
                 source_file="/data/imports/DMRC_Phase4_P6_Export_2024.xer",
                 import_hash="b4c3d2e1f0a9b8c7d6e5f4a3b2c1d0e9",
                 created_at=NOW - timedelta(days=90)),
            dict(id=BASELINE_03, package_id=PKG_SIG,
                 version=1, is_active=False, version_label="BL-SIG-2024-DRAFT",
                 supersedes_id=None, status=BaselineStatus.DRAFT,
                 baseline_type=BaselineType.ORIGINAL,
                 rebaseline_approved_by=None, rebaseline_reason=None,
                 approved_by=None, locked_at=None,
                 source_file=None, import_hash=None,
                 created_at=NOW - timedelta(days=60)),
        ]:
            if not await _exists(db, Baseline, Baseline.id, bl["id"]):
                db.add(Baseline(**bl))
                counts["baselines"] += 1
        await db.flush()

        # ----------------------------------------------------------------
        # 10. Baseline History
        # ----------------------------------------------------------------
        for bh in [
            dict(id=sid("bl_hist","BH-CIVIL-SUBMIT"), baseline_id=BASELINE_01,
                 action="SUBMIT", from_status="DRAFT", to_status="SUBMITTED",
                 acted_by=None, remarks="Initial submission after P6 import review.",
                 created_at=NOW - timedelta(days=88)),
            dict(id=sid("bl_hist","BH-CIVIL-APPROVE"), baseline_id=BASELINE_01,
                 action="APPROVE", from_status="SUBMITTED", to_status="APPROVED",
                 acted_by=None, remarks="Approved by QC Manager after kick-off review meeting.",
                 created_at=NOW - timedelta(days=85)),
            dict(id=sid("bl_hist","BH-CIVIL-LOCK"), baseline_id=BASELINE_01,
                 action="LOCK", from_status="APPROVED", to_status="LOCKED",
                 acted_by=None, remarks="Locked as contract baseline BL-2024-REV0 per CPM directive.",
                 created_at=NOW - timedelta(days=80)),
            dict(id=sid("bl_hist","BH-ELEC-SUBMIT"), baseline_id=BASELINE_02,
                 action="SUBMIT", from_status="DRAFT", to_status="SUBMITTED",
                 acted_by=None, remarks="E&M baseline submitted for Engineering Manager review.",
                 created_at=NOW - timedelta(days=50)),
            dict(id=sid("bl_hist","BH-ELEC-APPROVE"), baseline_id=BASELINE_02,
                 action="APPROVE", from_status="SUBMITTED", to_status="APPROVED",
                 acted_by=None, remarks="Approved pending commencement and site access.",
                 created_at=NOW - timedelta(days=45)),
        ]:
            if not await _exists(db, BaselineHistory, BaselineHistory.id, bh["id"]):
                db.add(BaselineHistory(**bh))
                counts["baseline_history"] += 1
        await db.flush()

        # ----------------------------------------------------------------
        # 11. Activities (30 total)
        #     Original 6 IDs preserved for FK compatibility with module seeds.
        #     24 new IDs added for dashboard volume.
        # ----------------------------------------------------------------

        # Helper: base activity dict
        def act(*, id, task_id, p6id, name, status, subsystem, pct, bac_cr,
                pkg_id=PKG_CIVIL, proj=1001, wbs=102,
                clndr=1, resource=None, bl=BASELINE_01,
                dur=90.0, is_crit=False, float_days=5.0,
                ps_d=120, pf_d=-1, as_d=None, af_d=None):
            """
            ps_d/pf_d: days from NOW for planned_start/end (negative = past, positive = future).
            as_d/af_d: days from NOW for actual_start/end (None if not started).
            """
            ps = NOW - timedelta(days=ps_d) if ps_d >= 0 else NOW + timedelta(days=abs(ps_d))
            pf = NOW - timedelta(days=pf_d) if pf_d >= 0 else NOW + timedelta(days=abs(pf_d))
            as_ = (NOW - timedelta(days=as_d)) if as_d is not None else None
            af_ = (NOW - timedelta(days=af_d)) if af_d is not None and af_d >= 0 else (
                NOW + timedelta(days=abs(af_d)) if af_d is not None else None
            )
            return dict(
                id=id, import_id=IMPORT_01,
                task_id=task_id, p6_activity_id=p6id, activity_name=name,
                status=status, activity_type=ActivityType.TASK,
                subsystem_type=subsystem,
                is_critical=is_crit, is_near_critical=(float_days <= 10.0 and not is_crit),
                requires_rfi=True, requires_material=(subsystem == SubsystemType.CIVIL),
                duration=dur, total_float_hr_cnt=float_days * 10.0,
                free_float_hr_cnt=float_days * 5.0, float_days=float_days,
                phys_complete_pct=pct, bac=bac_cr * 10_000_000.0,
                early_start_date=ps, early_end_date=pf,
                late_start_date=ps if is_crit else (ps - timedelta(days=int(float_days))),
                late_end_date=pf if is_crit else (pf - timedelta(days=int(float_days))),
                act_start_date=as_, act_end_date=af_,
                planned_start=ps, planned_end=pf,
                wbs_id=wbs, wbs_path=f"P4-{'CIV' if proj==1001 else ('EM' if proj==1002 else 'SIG')} > WBS-{wbs}",
                clndr_id=clndr, proj_id=proj,
                package_id=pkg_id, baseline_id=bl,
            )

        ACTIVITIES = [
            # --- PKG_CIVIL: Foundation & Earthwork (WBS 102) ---
            # Original 3 foundation/bridge/earthwork IDs preserved
            act(id=ACT_FOUND,  task_id=10100, p6id="A1010",
                name="Foundation Works — Pile Caps & Raft Slab, Ch. 12+000–13+000",
                status=ActivityStatus.IN_PROGRESS, subsystem=SubsystemType.CIVIL,
                pct=65.0, bac_cr=180, is_crit=True, float_days=0.0,
                ps_d=120, pf_d=-2, as_d=118, af_d=None, dur=122),

            act(id=ACT_PILE_A, task_id=10101, p6id="A1011",
                name="Bored Piling — Pier P01–P15 (750mm dia.), Ch. 0+000–3+750",
                status=ActivityStatus.COMPLETED, subsystem=SubsystemType.CIVIL,
                pct=100.0, bac_cr=95, is_crit=False, float_days=8.0,
                ps_d=360, pf_d=260, as_d=355, af_d=262, dur=100),

            act(id=ACT_PILE_B, task_id=10102, p6id="A1012",
                name="Bored Piling — Pier P16–P35 (750mm dia.), Ch. 3+750–8+750",
                status=ActivityStatus.COMPLETED, subsystem=SubsystemType.CIVIL,
                pct=100.0, bac_cr=142, is_crit=False, float_days=6.0,
                ps_d=280, pf_d=160, as_d=275, af_d=163, dur=120),

            act(id=ACT_EARTH, task_id=10103, p6id="A1013",
                name="Subgrade Preparation & Earthwork Compaction (All Reaches)",
                status=ActivityStatus.COMPLETED, subsystem=SubsystemType.CIVIL,
                pct=100.0, bac_cr=38, is_crit=False, float_days=15.0,
                ps_d=400, pf_d=280, as_d=395, af_d=283, dur=120),

            act(id=ACT_PIERCAP_A, task_id=10104, p6id="A1014",
                name="Pier Cap Construction (M40 Concrete) — Piers P01–P15",
                status=ActivityStatus.COMPLETED, subsystem=SubsystemType.CIVIL,
                pct=100.0, bac_cr=68, is_crit=False, float_days=5.0,
                ps_d=270, pf_d=190, as_d=265, af_d=193, dur=80),

            act(id=ACT_PIERCAP_B, task_id=10105, p6id="A1015",
                name="Pier Cap Construction (M40 Concrete) — Piers P16–P35",
                status=ActivityStatus.IN_PROGRESS, subsystem=SubsystemType.CIVIL,
                pct=60.0, bac_cr=96, is_crit=True, float_days=0.0,
                ps_d=180, pf_d=-30, as_d=175, af_d=None, dur=210),

            # --- PKG_CIVIL: Viaduct, Stations & TBM (WBS 103) ---
            act(id=ACT_BRIDGE, task_id=10200, p6id="A1020",
                name="Precast U-Girder Erection — Spans S-01 to S-20, Ch. 0+000–5+000",
                status=ActivityStatus.IN_PROGRESS, subsystem=SubsystemType.BRIDGE,
                pct=40.0, bac_cr=320, is_crit=True, float_days=0.0,
                wbs=103,
                ps_d=90, pf_d=-90, as_d=85, af_d=None, dur=180),

            act(id=ACT_UGIRDER_CAST, task_id=10201, p6id="A1021",
                name="U-Girder Precast at Casting Yard Ch. 0+000 (160 nos.)",
                status=ActivityStatus.IN_PROGRESS, subsystem=SubsystemType.CIVIL,
                pct=45.0, bac_cr=85, is_crit=True, float_days=0.0,
                wbs=103,
                ps_d=110, pf_d=-80, as_d=105, af_d=None, dur=190),

            act(id=ACT_UGIRDER_S02, task_id=10202, p6id="A1022",
                name="U-Girder Erection — Spans S-21 to S-40, Ch. 5+000–10+000",
                status=ActivityStatus.NOT_STARTED, subsystem=SubsystemType.BRIDGE,
                pct=0.0, bac_cr=320, is_crit=True, float_days=0.0,
                wbs=103,
                ps_d=-30, pf_d=-210, as_d=None, af_d=None, dur=180),

            act(id=ACT_DECK_SLAB, task_id=10203, p6id="A1023",
                name="Deck Slab, Waterproofing & Crash Barrier — Ch. 0+000–5+000",
                status=ActivityStatus.NOT_STARTED, subsystem=SubsystemType.CIVIL,
                pct=0.0, bac_cr=48, is_crit=False, float_days=12.0,
                wbs=103,
                ps_d=-60, pf_d=-150, as_d=None, af_d=None, dur=90),

            act(id=ACT_STN_EXCV, task_id=10204, p6id="A1024",
                name="Station Box Excavation & Dewatering — Hauz Khas Underground Station",
                status=ActivityStatus.COMPLETED, subsystem=SubsystemType.CIVIL,
                pct=100.0, bac_cr=125, is_crit=False, float_days=10.0,
                wbs=103,
                ps_d=250, pf_d=150, as_d=245, af_d=153, dur=100),

            act(id=ACT_STN_STRUCT, task_id=10205, p6id="A1025",
                name="Station Structural Concrete — Concourse & Platform Slab, Hauz Khas",
                status=ActivityStatus.IN_PROGRESS, subsystem=SubsystemType.CIVIL,
                pct=55.0, bac_cr=185, is_crit=True, float_days=0.0,
                wbs=103,
                ps_d=160, pf_d=-60, as_d=155, af_d=None, dur=220),

            act(id=ACT_STN_ARCH, task_id=10206, p6id="A1026",
                name="Station Architectural Finishes & MEP Rough-in — Hauz Khas",
                status=ActivityStatus.NOT_STARTED, subsystem=SubsystemType.CIVIL,
                pct=0.0, bac_cr=92, is_crit=False, float_days=20.0,
                wbs=103,
                ps_d=-45, pf_d=-195, as_d=None, af_d=None, dur=150),

            act(id=ACT_TBM_SHAFT, task_id=10207, p6id="A1027",
                name="TBM Launch Shaft Construction & Cutter Head Assembly",
                status=ActivityStatus.COMPLETED, subsystem=SubsystemType.CIVIL,
                pct=100.0, bac_cr=68, is_crit=True, float_days=0.0,
                wbs=103,
                ps_d=200, pf_d=120, as_d=195, af_d=123, dur=80),

            act(id=ACT_TBM_DRIVE1, task_id=10208, p6id="A1028",  # reuse concept, new actual ID
                name="TBM Boring Drive-1 (CRCHI 6.68m TBM) — Ch. 10+000 to Ch. 14+000 [DELAYED +18d]",
                status=ActivityStatus.IN_PROGRESS, subsystem=SubsystemType.CIVIL,
                pct=30.0, bac_cr=280, is_crit=True, float_days=0.0,
                wbs=103,
                ps_d=80, pf_d=-160, as_d=80, af_d=None, dur=240,
                clndr=2),  # 7-day calendar for critical TBM

            act(id=ACT_TBM_DRIVE2, task_id=10209, p6id="A1029",
                name="TBM Boring Drive-2 — Ch. 14+000 to Ch. 17+000",
                status=ActivityStatus.NOT_STARTED, subsystem=SubsystemType.CIVIL,
                pct=0.0, bac_cr=210, is_crit=True, float_days=0.0,
                wbs=103,
                ps_d=-150, pf_d=-330, as_d=None, af_d=None, dur=180,
                clndr=2),

            act(id=ACT_TUNNEL_INVERT, task_id=10210, p6id="A1030",
                name="Tunnel Invert Concrete & Track Bed Formation",
                status=ActivityStatus.NOT_STARTED, subsystem=SubsystemType.CIVIL,
                pct=0.0, bac_cr=55, is_crit=True, float_days=0.0,
                wbs=103,
                ps_d=-320, pf_d=-410, as_d=None, af_d=None, dur=90),

            # --- PKG_ELEC: Traction Power (WBS 202) ---
            act(id=ACT_OHE_MAST, task_id=20100, p6id="A2010",
                name="OHE Mast Foundation & Erection — Ch. 0+000 to Ch. 10+000",
                status=ActivityStatus.COMPLETED, subsystem=SubsystemType.ELEC,
                pct=100.0, bac_cr=145, is_crit=False, float_days=18.0,
                pkg_id=PKG_ELEC, proj=1002, wbs=202, bl=BASELINE_02,
                ps_d=300, pf_d=180, as_d=295, af_d=183, dur=120),

            act(id=ACT_TRAC, task_id=20101, p6id="A2011",
                name="Catenary Wire Stringing & Registration — Full Corridor",
                status=ActivityStatus.IN_PROGRESS, subsystem=SubsystemType.ELEC,
                pct=40.0, bac_cr=88, is_crit=True, float_days=0.0,
                pkg_id=PKG_ELEC, proj=1002, wbs=202, bl=BASELINE_02,
                ps_d=120, pf_d=-60, as_d=115, af_d=None, dur=180),

            act(id=ACT_TSS_CIVIL, task_id=20102, p6id="A2012",
                name="Traction Substation RSS-1 Civil Works & Equipment Room",
                status=ActivityStatus.IN_PROGRESS, subsystem=SubsystemType.ELEC,
                pct=70.0, bac_cr=62, is_crit=False, float_days=15.0,
                pkg_id=PKG_ELEC, proj=1002, wbs=202, bl=BASELINE_02,
                ps_d=160, pf_d=10, as_d=155, af_d=None, dur=150),

            act(id=ACT_TSS_EM, task_id=20103, p6id="A2013",
                name="Traction Substation RSS-1 E&M Equipment Supply & Installation",
                status=ActivityStatus.NOT_STARTED, subsystem=SubsystemType.ELEC,
                pct=0.0, bac_cr=120, is_crit=True, float_days=0.0,
                pkg_id=PKG_ELEC, proj=1002, wbs=202, bl=BASELINE_02,
                ps_d=-5, pf_d=-125, as_d=None, af_d=None, dur=120),

            act(id=ACT_STN_LIGHT, task_id=20200, p6id="A2020",
                name="Station Lighting, Small Power & Emergency Systems",
                status=ActivityStatus.NOT_STARTED, subsystem=SubsystemType.ELEC,
                pct=0.0, bac_cr=45, is_crit=False, float_days=30.0,
                pkg_id=PKG_ELEC, proj=1002, wbs=203, bl=BASELINE_02,
                ps_d=-90, pf_d=-210, as_d=None, af_d=None, dur=120),

            act(id=ACT_ESCL_LIFT, task_id=20201, p6id="A2021",
                name="Escalator & Passenger Lift Installation (4 stations)",
                status=ActivityStatus.NOT_STARTED, subsystem=SubsystemType.ELEC,
                pct=0.0, bac_cr=115, is_crit=False, float_days=25.0,
                pkg_id=PKG_ELEC, proj=1002, wbs=203, bl=BASELINE_02,
                ps_d=-60, pf_d=-240, as_d=None, af_d=None, dur=180),

            act(id=ACT_TRACK, task_id=20202, p6id="A2022",
                name="Depot Track Laying & Ballasting (Depot Equipment Package)",
                status=ActivityStatus.IN_PROGRESS, subsystem=SubsystemType.ELEC,
                pct=25.0, bac_cr=72, is_crit=False, float_days=20.0,
                pkg_id=PKG_ELEC, proj=1002, wbs=203, bl=BASELINE_02,
                ps_d=90, pf_d=-60, as_d=85, af_d=None, dur=150),

            # --- PKG_SIG: Signalling CBTC (WBS 302) ---
            act(id=ACT_OFC_CABLE, task_id=30100, p6id="A3010",
                name="Optical Fibre Cable Laying — Wayside Backbone (Full Corridor)",
                status=ActivityStatus.COMPLETED, subsystem=SubsystemType.SIG,
                pct=100.0, bac_cr=42, is_crit=False, float_days=20.0,
                pkg_id=PKG_SIG, proj=1003, wbs=302, bl=BASELINE_03,
                ps_d=200, pf_d=100, as_d=195, af_d=103, dur=100),

            act(id=ACT_ATP_TRACKSIDE, task_id=30101, p6id="A3011",
                name="CBTC Trackside Equipment — ATP Balises & Transponders",
                status=ActivityStatus.IN_PROGRESS, subsystem=SubsystemType.SIG,
                pct=25.0, bac_cr=88, is_crit=True, float_days=0.0,
                pkg_id=PKG_SIG, proj=1003, wbs=302, bl=BASELINE_03,
                ps_d=90, pf_d=-120, as_d=85, af_d=None, dur=210),

            act(id=ACT_SIG, task_id=30102, p6id="A3012",
                name="CBTC Interlocking & Wayside ATP Equipment Rooms",
                status=ActivityStatus.NOT_STARTED, subsystem=SubsystemType.SIG,
                pct=0.0, bac_cr=132, is_crit=True, float_days=0.0,
                pkg_id=PKG_SIG, proj=1003, wbs=302, bl=BASELINE_03,
                ps_d=-60, pf_d=-240, as_d=None, af_d=None, dur=180),

            act(id=sid("activity","A-CBTC-OCC"), task_id=30103, p6id="A3013",
                name="CBTC OCC Servers, ATC System & Radio Infrastructure",
                status=ActivityStatus.NOT_STARTED, subsystem=SubsystemType.SIG,
                pct=0.0, bac_cr=165, is_crit=True, float_days=0.0,
                pkg_id=PKG_SIG, proj=1003, wbs=302, bl=BASELINE_03,
                ps_d=-120, pf_d=-360, as_d=None, af_d=None, dur=240),

            act(id=sid("activity","A-IST"), task_id=30104, p6id="A3014",
                name="Integrated System Test (IST) — All Subsystems",
                status=ActivityStatus.NOT_STARTED, subsystem=SubsystemType.SIG,
                pct=0.0, bac_cr=45, is_crit=True, float_days=0.0,
                pkg_id=PKG_SIG, proj=1003, wbs=302, bl=BASELINE_03,
                ps_d=-350, pf_d=-530, as_d=None, af_d=None, dur=180),

            act(id=ACT_AFC, task_id=30200, p6id="A3020",
                name="AFC System — Fare Gates, TVMs & Back Office Server",
                status=ActivityStatus.NOT_STARTED, subsystem=SubsystemType.SIG,
                pct=0.0, bac_cr=78, is_crit=False, float_days=30.0,
                pkg_id=PKG_SIG, proj=1003, wbs=303, bl=BASELINE_03,
                ps_d=-90, pf_d=-270, as_d=None, af_d=None, dur=180),

            act(id=ACT_STN_TELECOM, task_id=30201, p6id="A3021",
                name="Station Telecom — PA, CCTV, SCADA & PIS Installation",
                status=ActivityStatus.IN_PROGRESS, subsystem=SubsystemType.SIG,
                pct=20.0, bac_cr=55, is_crit=False, float_days=25.0,
                pkg_id=PKG_SIG, proj=1003, wbs=303, bl=BASELINE_03,
                ps_d=80, pf_d=-100, as_d=75, af_d=None, dur=180),

            act(id=sid("activity","A-TRIAL-RUN"), task_id=30202, p6id="A3022",
                name="Trial Run (Empty Revenue Service) — 90 Days",
                status=ActivityStatus.NOT_STARTED, subsystem=SubsystemType.SIG,
                pct=0.0, bac_cr=18, is_crit=True, float_days=0.0,
                pkg_id=PKG_SIG, proj=1003, wbs=303, bl=BASELINE_03,
                ps_d=-510, pf_d=-600, as_d=None, af_d=None, dur=90),
        ]

        for a in ACTIVITIES:
            if not await _exists(db, Activity, Activity.id, a["id"]):
                db.add(Activity(**a))
                counts["activities"] += 1
        await db.flush()

        # ----------------------------------------------------------------
        # 12. ActivityBaselineLinks (for EVM computation)
        # ----------------------------------------------------------------
        bl_links = [
            (ACT_FOUND, BASELINE_01, 65.0, 180_000_000.0),
            (ACT_BRIDGE, BASELINE_01, 40.0, 320_000_000.0),
            (ACT_EARTH, BASELINE_01, 100.0, 38_000_000.0),
            (ACT_PIERCAP_A, BASELINE_01, 100.0, 68_000_000.0),
            (ACT_PIERCAP_B, BASELINE_01, 60.0, 96_000_000.0),
            (ACT_STN_EXCV, BASELINE_01, 100.0, 125_000_000.0),
            (ACT_STN_STRUCT, BASELINE_01, 55.0, 185_000_000.0),
            (ACT_TBM_SHAFT, BASELINE_01, 100.0, 68_000_000.0),
            (ACT_TRAC, BASELINE_02, 40.0, 88_000_000.0),
            (ACT_TSS_CIVIL, BASELINE_02, 70.0, 62_000_000.0),
            (ACT_OFC_CABLE, BASELINE_03, 100.0, 42_000_000.0),
            (ACT_ATP_TRACKSIDE, BASELINE_03, 25.0, 88_000_000.0),
        ]
        for act_id, bl_id, pct, bac in bl_links:
            link_id = sid("bl_link", f"{act_id}-{bl_id}")
            if not await _exists(db, ActivityBaselineLink, ActivityBaselineLink.id, link_id):
                db.add(ActivityBaselineLink(
                    id=link_id, activity_id=act_id, baseline_id=bl_id,
                    bl_start_date=NOW - timedelta(days=90),
                    bl_end_date=NOW + timedelta(days=90),
                    bl_phys_complete_pct=pct, bl_bac=bac,
                ))
                counts["baseline_links"] += 1
        await db.flush()

        # ----------------------------------------------------------------
        # 13. EVM Snapshots — 6 monthly snapshots for PKG_CIVIL
        #     Simulates S-curve: slow start, ramp-up, slight delay
        # ----------------------------------------------------------------
        evm_data = [
            # month_offset, pv, ev, ac, spi, cpi
            (6, 0.08, 0.06, 0.07, 0.75, 0.86),  # Month 1 — mobilisation delay
            (5, 0.14, 0.11, 0.13, 0.79, 0.85),  # Month 2 — still behind
            (4, 0.24, 0.20, 0.23, 0.83, 0.87),  # Month 3 — recovering
            (3, 0.36, 0.31, 0.35, 0.86, 0.89),  # Month 4
            (2, 0.50, 0.44, 0.48, 0.88, 0.92),  # Month 5
            (1, 0.62, 0.57, 0.61, 0.92, 0.93),  # Month 6 (latest)
        ]
        total_bac = 1_700_000_000.0  # PKG_CIVIL total BAC
        for i, (mo, pv_pct, ev_pct, ac_pct, spi, cpi) in enumerate(evm_data):
            snap_id = sid("evm", f"PKG-CIVIL-M-{i+1}")
            snap_date = NOW - timedelta(days=mo * 30)
            if not await _exists(db, EVMSnapshot, EVMSnapshot.id, snap_id):
                pv = total_bac * pv_pct
                ev = total_bac * ev_pct
                ac = total_bac * ac_pct
                db.add(EVMSnapshot(
                    id=snap_id,
                    baseline_id=BASELINE_01,
                    package_id=PKG_CIVIL,
                    snapshot_date=snap_date.date(),
                    snapshot_type=EVMSnapshotType.MONTHLY,
                    period_type=EVMPeriodType.MONTHLY,
                    ev_source=EVSource.P6,
                    planned_value=pv,
                    earned_value=ev,
                    actual_cost=ac,
                    bac=total_bac,
                    eac=total_bac / cpi,
                    etc=(total_bac - ev) / cpi,
                    vac=total_bac - (total_bac / cpi),
                    sv=ev - pv,
                    cv=ev - ac,
                    spi=spi,
                    cpi=cpi,
                    tcpi=(total_bac - ev) / (total_bac - ac),
                    created_at=snap_date,
                ))
                counts["evm_snapshots"] += 1
        await db.flush()

        # ----------------------------------------------------------------
        # 14. Dependencies (key critical path links)
        # ----------------------------------------------------------------
        deps = [
            (ACT_EARTH, ACT_FOUND, DependencyType.FINISH_TO_START, 0),
            (ACT_FOUND, ACT_BRIDGE, DependencyType.FINISH_TO_START, 10),
            (ACT_PILE_B, ACT_PIERCAP_B, DependencyType.FINISH_TO_START, 5),
            (ACT_TBM_SHAFT, ACT_TBM_DRIVE1, DependencyType.FINISH_TO_START, 0),
            (ACT_TBM_DRIVE1, ACT_TBM_DRIVE2, DependencyType.FINISH_TO_START, 0),
            (ACT_OHE_MAST, ACT_TRAC, DependencyType.FINISH_TO_START, 5),
            (ACT_OFC_CABLE, ACT_ATP_TRACKSIDE, DependencyType.FINISH_TO_START, 0),
            (ACT_ATP_TRACKSIDE, ACT_SIG, DependencyType.FINISH_TO_START, 0),
        ]
        for i, (pred, succ, dtype, lag) in enumerate(deps):
            dep_id = sid("dep", f"DEP-{i:02d}")
            if not await _exists(db, Dependency, Dependency.id, dep_id):
                db.add(Dependency(
                    id=dep_id, import_id=IMPORT_01,
                    pred_activity_id=pred, succ_activity_id=succ,
                    dependency_type=dtype, lag_days=lag,
                ))
                counts["dependencies"] += 1
        await db.flush()

        await db.commit()

        print("\n=== Schedule Seed Complete (30 Activities) ===")
        for k, v in counts.items():
            if v:
                print(f"  {k:22s} {v:3d} inserted")
        print()
        print(f"  PKG_CIVIL  UUID: {PKG_CIVIL}")
        print(f"  PKG_ELEC   UUID: {PKG_ELEC}")
        print(f"  PKG_SIG    UUID: {PKG_SIG}")
        print(f"  BASELINE   UUID: {BASELINE_01}")
        print()


if __name__ == "__main__":
    asyncio.run(seed())
