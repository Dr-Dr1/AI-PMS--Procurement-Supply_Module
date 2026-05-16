"""
Schedule V2 seed — DMRC Phase-IV realistic data.
Idempotent: safe to re-run.
"""
from __future__ import annotations

import uuid
from datetime import date, datetime, timezone

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import async_session
from app.core.enums import (
    ActivityStatus, ActivityType, BaselineStatus, BaselineType,
    ContractStandard, ContractStatus, DependencyType, EOTMethodology,
    EVMPeriodType, EVSource, EVMSnapshotType, PackageStatus, SubsystemType,
)
from app.models_v2.schedule import (
    XERImport, Project, WBS,
    Calendar, Resource,
    Activity, Relationship,
    ResourceAssignment, Dependency,
)
from app.models_v2.structure import Corridor, Package
from app.models_v2.contract_schedule import Contract

NS = uuid.NAMESPACE_DNS

def qid(entity: str, code: str) -> uuid.UUID:
    return uuid.uuid5(NS, f"aipms.quality.{entity}.{code}")

def sid(entity: str, code: str) -> uuid.UUID:
    return uuid.uuid5(NS, f"aipms.schedule.{entity}.{code}")

# ── Stable cross-module IDs ──────────────────────────────────────────────────
IMPORT_01   = sid("import",   "DMRC-P4-2024-EXPORT")
PROJ_01     = sid("project",  "DMRC-P4-MAIN")
CAL_6DAY    = sid("calendar", "CAL-6DAY")
CAL_7DAY    = sid("calendar", "CAL-7DAY")
WBS_ROOT    = sid("wbs",      "WBS-ROOT")
WBS_CIVIL   = sid("wbs",      "WBS-CIVIL")
WBS_ELEC    = sid("wbs",      "WBS-ELEC")
WBS_SIG     = sid("wbs",      "WBS-SIG")
RSRC_ENG    = sid("resource", "RSRC-CIVIL-ENG")
RSRC_ELEC   = sid("resource", "RSRC-ELEC-ENG")
CON_CIVIL   = sid("contract", "DMRC-P4-CC-2023-001")
CON_ELEC    = sid("contract", "DMRC-P4-EM-2023-002")
CON_SIG     = sid("contract", "DMRC-P4-SIG-2023-003")
COR_REDLINE = sid("corridor", "COR-REDLINE")
COR_BLUELINE= sid("corridor", "COR-BLUELINE")
PKG_CIVIL   = qid("package",  "PKG-CIVIL-001")
PKG_ELEC    = qid("package",  "PKG-ELEC-001")
PKG_SIG     = qid("package",  "PKG-SIG-001")
BASELINE_01 = qid("baseline", "BL-2024-REV0")
ACT_FOUND   = qid("activity", "ACT-CIVIL-FOUNDATION")
ACT_BRIDGE  = qid("activity", "ACT-CIVIL-BRIDGE")
ACT_EARTH   = qid("activity", "ACT-CIVIL-EARTHWORK")
ACT_TRAC    = qid("activity", "ACT-ELEC-TRACTION")
ACT_SIG     = qid("activity", "ACT-SIG-INSTALL")
ACT_TRACK   = qid("activity", "ACT-TRACK-ALIGN")

NOW = datetime.now(timezone.utc)

async def _exists(session: AsyncSession, model, pk_val) -> bool:
    row = await session.get(model, pk_val)
    return row is not None

async def seed(session: AsyncSession | None = None) -> None:
    if session is None:
        async with async_session() as s:
            await _seed(s)
    else:
        await _seed(session)

async def _seed(s: AsyncSession) -> None:
    # 1. Import
    if not await _exists(s, XERImport, IMPORT_01):
        s.add(XERImport(
            id=IMPORT_01, file_path="uploads/dmrc_p4_2024_export.xer",
            total_projects=1, total_activities=6, total_resources=2,
            total_calendars=2, total_wbs=4, total_relationships=3,
            total_corridors=2, total_packages=3,
            parse_response={"status": "ok", "warnings": []},
            created_at=NOW,
        ))

    # 2. Project
    if not await _exists(s, Project, PROJ_01):
        s.add(Project(
            id=PROJ_01, import_id=IMPORT_01, proj_id=10001,
            proj_short_name="DMRC-P4", proj_name="DMRC Phase IV Metro Rail Project",
            scd_start_date="2023-01-01", scd_end_date="2026-12-31",
            last_recalc_date="2024-01-15",
            activity_count=6, completed=1, in_progress=3, not_started=2,
            created_at=NOW, updated_at=NOW,
        ))

    # 3. Calendars
    for cal_id, clndr_id, name, day_hr, week_hr in [
        (CAL_6DAY, 1001, "6-Day Work Week", 8.0, 48.0),
        (CAL_7DAY, 1002, "7-Day Work Week", 8.0, 56.0),
    ]:
        if not await _exists(s, Calendar, cal_id):
            s.add(Calendar(
                id=cal_id, import_id=IMPORT_01,
                clndr_id=clndr_id, clndr_name=name, clndr_type="Global",
                day_hr_cnt=day_hr, week_hr_cnt=week_hr,
                month_hr_cnt=day_hr * 26, year_hr_cnt=day_hr * 312,
                created_at=NOW,
            ))

    # 4. WBS
    wbs_rows = [
        (WBS_ROOT,  9001, "DMRC Phase IV",    "DMRC-P4",  None,        1),
        (WBS_CIVIL, 9002, "Civil Works",      "CW",       9001,        2),
        (WBS_ELEC,  9003, "Electrical Works", "EW",       9001,        3),
        (WBS_SIG,   9004, "Signalling",       "SG",       9001,        4),
    ]
    for wbs_id, wbs_int, name, short, parent_int, seq in wbs_rows:
        if not await _exists(s, WBS, wbs_id):
            s.add(WBS(
                id=wbs_id, import_id=IMPORT_01,
                wbs_id=wbs_int, wbs_name=name, wbs_short_name=short,
                parent_wbs_id=parent_int, proj_id=10001, seq_num=seq,
                created_at=NOW,
            ))

    # 5. Resources
    for rsrc_id, rsrc_int, name, short, rtype, email in [
        (RSRC_ENG,  2001, "Civil Engineering Team",    "CIVIL-ENG",  "Labor", "civil@ltconstruction.in"),
        (RSRC_ELEC, 2002, "Electrical Engineering Team","ELEC-ENG",  "Labor", "elec@alstom.com"),
    ]:
        if not await _exists(s, Resource, rsrc_id):
            s.add(Resource(
                id=rsrc_id, import_id=IMPORT_01,
                rsrc_id=rsrc_int, rsrc_name=name, rsrc_short_name=short,
                rsrc_type=rtype, email_addr=email, parent_rsrc_id=None,
                created_at=NOW,
            ))

    # 6. Contracts
    contracts = [
        (CON_CIVIL, "DMRC/P4/CC/2023/001",
         "Civil Construction Contract — Elevated Viaduct & Stations",
         "Construction of elevated viaduct, stations, and allied civil works for DMRC Phase IV corridors.",
         ContractStandard.FIDIC_RED, 4_250_000_000.0, EOTMethodology.WINDOWS),
        (CON_ELEC,  "DMRC/P4/EM/2023/002",
         "Electrical & Mechanical Systems Contract",
         "Supply, installation, testing and commissioning of E&M systems including traction power.",
         ContractStandard.FIDIC_YELLOW, 1_850_000_000.0, EOTMethodology.TIA),
        (CON_SIG,   "DMRC/P4/SIG/2023/003",
         "Signalling & Train Control System Contract",
         "Design, supply and commissioning of CBTC signalling and train control systems.",
         ContractStandard.FIDIC_YELLOW, 980_000_000.0, EOTMethodology.PROSPECTIVE),
    ]
    for con_id, num, title, desc, std, val, eot in contracts:
        if not await _exists(s, Contract, con_id):
            s.add(Contract(
                id=con_id, contract_number=num, title=title,
                description=desc,
                status=ContractStatus.ACTIVE,
                owner_id=None, contractor_id=None,
                contract_standard=std,
                contract_value=val, revised_value=None,
                commencement_date=date(2023, 4, 1),
                completion_date=date(2026, 3, 31),
                dlp_months=12, eot_methodology=eot,
                ld_formula={"rate": 0.001, "cap": 0.10},
                notice_rules={"notice_period_days": 28},
                created_at=NOW, updated_at=NOW,
            ))

    # 7. Corridors
    for cor_id, name, code in [
        (COR_REDLINE,  "Janakpuri West – RK Ashram Marg", "JW-RKA"),
        (COR_BLUELINE, "Inderlok – Indraprastha",          "IL-IP"),
    ]:
        if not await _exists(s, Corridor, cor_id):
            s.add(Corridor(
                id=cor_id, import_id=IMPORT_01, proj_id=10001,
                source_wbs_id=9001,
                corridor_name=name, corridor_code=code,
                created_at=NOW, updated_at=NOW,
            ))

    # 8. Packages
    packages = [
        (PKG_CIVIL, "Civil Construction Package",        "PKG-CIVIL-001", COR_REDLINE,  CON_CIVIL, 9002, None, SubsystemType.CIVIL),
        (PKG_ELEC,  "Electrical & Mechanical Package",   "PKG-ELEC-001",  COR_REDLINE,  CON_ELEC,  9003, None, SubsystemType.ELEC),
        (PKG_SIG,   "Signalling Package",                "PKG-SIG-001",   COR_BLUELINE, CON_SIG,   9004, None, SubsystemType.SIG),
    ]
    for pkg_id, name, code, cor_id, con_id, wbs_int, parent_pkg, subsystem in packages:
        if not await _exists(s, Package, pkg_id):
            s.add(Package(
                id=pkg_id, import_id=IMPORT_01, proj_id=10001,
                corridor_id=cor_id, contract_id=con_id,
                source_wbs_id=wbs_int, parent_wbs_id=9001,
                parent_package_id=parent_pkg,
                package_name=name, package_code=code,
                status=PackageStatus.ACTIVE,
                contractor_name="L&T Construction" if subsystem == SubsystemType.CIVIL else (
                    "Alstom Transport" if subsystem == SubsystemType.SIG else "Siemens India"
                ),
                description=f"Works package for {name}",
                created_at=NOW, updated_at=NOW,
            ))

    # 9. Activities
    # Note: clndr_id is an integer field (BigInteger) referencing clndr_id from Calendar
    activities = [
        (ACT_FOUND, 3001, "A1001", "Foundation Works — Pier P101 to P150",
         ActivityStatus.COMPLETED, ActivityType.TASK, SubsystemType.CIVIL,
         PKG_CIVIL, 9002, 10001, 1001, True, False, True,
         120.0, 0.0, 0.0, 100.0, 0.0,
         datetime(2023,4,1,tzinfo=timezone.utc), datetime(2023,8,31,tzinfo=timezone.utc),
         datetime(2023,4,1,tzinfo=timezone.utc), datetime(2023,8,31,tzinfo=timezone.utc),
         datetime(2023,4,1,tzinfo=timezone.utc), datetime(2023,8,28,tzinfo=timezone.utc)),
        (ACT_BRIDGE, 3002, "A1002", "Viaduct Superstructure — Spans 1-50",
         ActivityStatus.IN_PROGRESS, ActivityType.TASK, SubsystemType.CIVIL,
         PKG_CIVIL, 9002, 10001, 1001, True, False, True,
         180.0, 16.0, 8.0, 65.0, 52_000_000.0,
         datetime(2023,9,1,tzinfo=timezone.utc), datetime(2024,3,31,tzinfo=timezone.utc),
         datetime(2023,9,1,tzinfo=timezone.utc), datetime(2024,4,16,tzinfo=timezone.utc),
         datetime(2023,9,5,tzinfo=timezone.utc), None),
        (ACT_EARTH, 3003, "A1003", "Earthwork & Embankment — Ch. 0+000 to 5+500",
         ActivityStatus.IN_PROGRESS, ActivityType.TASK, SubsystemType.CIVIL,
         PKG_CIVIL, 9002, 10001, 1001, False, True, False,
         90.0, 32.0, 16.0, 40.0, 18_000_000.0,
         datetime(2023,9,15,tzinfo=timezone.utc), datetime(2023,12,31,tzinfo=timezone.utc),
         datetime(2023,9,15,tzinfo=timezone.utc), datetime(2024,1,16,tzinfo=timezone.utc),
         datetime(2023,9,20,tzinfo=timezone.utc), None),
        (ACT_TRAC, 3004, "A2001", "Traction Power Supply Installation",
         ActivityStatus.NOT_STARTED, ActivityType.TASK, SubsystemType.ELEC,
         PKG_ELEC, 9003, 10001, 1002, False, False, True,
         120.0, 48.0, 48.0, 0.0, 0.0,
         datetime(2024,1,1,tzinfo=timezone.utc), datetime(2024,5,31,tzinfo=timezone.utc),
         datetime(2024,1,1,tzinfo=timezone.utc), datetime(2024,7,18,tzinfo=timezone.utc),
         None, None),
        (ACT_SIG, 3005, "A3001", "CBTC Signalling Equipment Installation",
         ActivityStatus.NOT_STARTED, ActivityType.TASK, SubsystemType.SIG,
         PKG_SIG, 9004, 10001, 1001, False, False, True,
         150.0, 60.0, 60.0, 0.0, 0.0,
         datetime(2024,3,1,tzinfo=timezone.utc), datetime(2024,8,31,tzinfo=timezone.utc),
         datetime(2024,3,1,tzinfo=timezone.utc), datetime(2024,11,8,tzinfo=timezone.utc),
         None, None),
        (ACT_TRACK, 3006, "A1004", "Track Alignment & Ballasting",
         ActivityStatus.IN_PROGRESS, ActivityType.TASK, SubsystemType.TRACK,
         PKG_CIVIL, 9002, 10001, 1002, False, True, False,
         60.0, 8.0, 8.0, 55.0, 8_500_000.0,
         datetime(2023,11,1,tzinfo=timezone.utc), datetime(2024,1,15,tzinfo=timezone.utc),
         datetime(2023,11,1,tzinfo=timezone.utc), datetime(2024,1,23,tzinfo=timezone.utc),
         datetime(2023,11,3,tzinfo=timezone.utc), None),
    ]
    for (act_id, task_int, p6_id, name, status, atype, subsys, pkg_id,
         wbs_int, proj_int, cal_int, is_crit, is_near, req_rfi,
         dur, t_float, f_float, pct, bac,
         es, ee, ls, le, as_, ae) in activities:
        if not await _exists(s, Activity, act_id):
            s.add(Activity(
                id=act_id, import_id=IMPORT_01,
                task_id=task_int, p6_activity_id=p6_id, activity_name=name,
                status=status, activity_type=atype, subsystem_type=subsys,
                is_critical=is_crit, is_near_critical=is_near, requires_rfi=req_rfi,
                requires_material=False,
                duration=dur, total_float_hr_cnt=t_float, free_float_hr_cnt=f_float,
                float_days=t_float / 8.0,
                phys_complete_pct=pct, bac=bac,
                early_start_date=es, early_end_date=ee,
                late_start_date=ls, late_end_date=le,
                act_start_date=as_, act_end_date=ae,
                planned_start=es, planned_end=ee,
                wbs_id=wbs_int, proj_id=proj_int,
                clndr_id=cal_int,
                package_id=pkg_id, baseline_id=BASELINE_01,
                created_at=NOW, updated_at=NOW,
            ))

    # 10. Relationships
    rels = [
        (ACT_FOUND, ACT_BRIDGE, "FS", 0.0),
        (ACT_FOUND, ACT_EARTH,  "SS", 16.0),
        (ACT_EARTH, ACT_TRACK,  "FS", 0.0),
    ]
    for pred, succ, rtype, lag in rels:
        existing = await s.execute(
            select(Relationship).where(
                Relationship.pred_task_id == (
                    await s.execute(select(Activity.task_id).where(Activity.id == pred))
                ).scalar_one_or_none(),
                Relationship.task_id == (
                    await s.execute(select(Activity.task_id).where(Activity.id == succ))
                ).scalar_one_or_none(),
            )
        )
        if not existing.scalars().first():
            pred_task_int = (await s.execute(select(Activity.task_id).where(Activity.id == pred))).scalar_one_or_none()
            succ_task_int = (await s.execute(select(Activity.task_id).where(Activity.id == succ))).scalar_one_or_none()
            if pred_task_int and succ_task_int:
                s.add(Relationship(
                    id=sid("relationship", f"{pred_task_int}-{succ_task_int}"),
                    import_id=IMPORT_01,
                    task_pred_id=succ_task_int, task_id=succ_task_int,
                    pred_task_id=pred_task_int,
                    pred_type=rtype, lag_hr_cnt=lag,
                    created_at=NOW,
                ))

    # 11. Resource Assignments
    assignments = [
        (ACT_FOUND,  RSRC_ENG,  2001, 1200.0, 7_200_000.0,  1200.0, 7_200_000.0),
        (ACT_BRIDGE, RSRC_ENG,  2001,  900.0, 5_400_000.0,   585.0, 3_510_000.0),
        (ACT_TRAC,   RSRC_ELEC, 2002,  960.0, 8_640_000.0,     0.0,         0.0),
    ]
    for act_id, rsrc_id, rsrc_int, tgt_qty, tgt_cost, act_qty, act_cost in assignments:
        assign_uuid = sid("assignment", f"{act_id}-{rsrc_int}")
        if not await _exists(s, ResourceAssignment, assign_uuid):
            act_int = (await s.execute(select(Activity.task_id).where(Activity.id == act_id))).scalar_one_or_none()
            rsrc_name_val = (await s.execute(select(Resource.rsrc_name).where(Resource.id == rsrc_id))).scalar_one_or_none()
            act_name_val = (await s.execute(select(Activity.activity_name).where(Activity.id == act_id))).scalar_one_or_none()
            act_code_val = (await s.execute(select(Activity.p6_activity_id).where(Activity.id == act_id))).scalar_one_or_none()
            if act_int:
                s.add(ResourceAssignment(
                    id=assign_uuid, import_id=IMPORT_01,
                    taskrsrc_id=int(str(act_int) + str(rsrc_int)),
                    task_id=act_int, rsrc_id=rsrc_int,
                    task_code=act_code_val, activity_name=act_name_val,
                    rsrc_name=rsrc_name_val, rsrc_type="Labor",
                    target_qty=tgt_qty, target_cost=tgt_cost,
                    act_reg_qty=act_qty, act_reg_cost=act_cost,
                    act_ot_qty=0.0, act_ot_cost=0.0,
                    created_at=NOW,
                ))

    # 12. Dependencies
    dep_pairs = [
        (ACT_FOUND, ACT_BRIDGE, DependencyType.FS, 0.0,  False, False),
        (ACT_FOUND, ACT_EARTH,  DependencyType.SS, 2.0,  False, False),
        (ACT_EARTH, ACT_TRACK,  DependencyType.FS, 0.0,  False, False),
    ]
    for pred_id, succ_id, dtype, lag, cross_pkg, cross_sys in dep_pairs:
        dep_uuid = sid("dependency", f"{pred_id}-{succ_id}")
        if not await _exists(s, Dependency, dep_uuid):
            s.add(Dependency(
                id=dep_uuid, import_id=IMPORT_01,
                predecessor_id=pred_id, successor_id=succ_id,
                dep_type=dtype, lag_days=lag,
                is_cross_package=cross_pkg, is_cross_subsystem=cross_sys,
            ))

    await s.commit()
    print("  schedule_seed: done")
