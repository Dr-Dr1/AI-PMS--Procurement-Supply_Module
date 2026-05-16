"""
Seed procurement module: POs, POLineItems, GRNs, MaterialLinks.

Usage (from backend/ directory):
    python -m seeds.procurement_seed

Idempotent. Deterministic UUIDs via uuid5.
package_id values are placeholder UUIDs — no FK constraint on procurement tables.
"""
from __future__ import annotations

import asyncio
import uuid
from datetime import datetime, date, timezone, timedelta
from decimal import Decimal

from sqlalchemy import select

from app.core.database import async_session as async_session_factory
from app.models_v2.procurement import (
    PO, POLineItem,
    GoodsReceipt, MaterialScheduleLink,
)
from app.core.enums import POStatus, GRNStatus, RiskLevel, MaterialLinkStatus

NS = uuid.NAMESPACE_DNS


def prid(entity: str, code: str) -> uuid.UUID:
    return uuid.uuid5(NS, f"aipms.procurement.{entity}.{code}")


NOW = datetime.now(tz=timezone.utc)

# Placeholder package UUIDs (no FK constraint on procurement tables)
PKG_CIVIL = prid("package", "PKG-CIVIL-001")
PKG_ELEC  = prid("package", "PKG-ELEC-001")
PKG_SIG   = prid("package", "PKG-SIG-001")

# Activity ref strings (stored as String, no FK)
ACT_TBM     = "ACT-CC07-TBM-SOUTH"
ACT_STATION = "ACT-CC07-STN-BOX"
ACT_TRAC    = "ACT-CC12-TRACTION"
ACT_SIG     = "ACT-CC12-SIGNALLING"

# ---------------------------------------------------------------------------
# Purchase Orders
# ---------------------------------------------------------------------------

PO_SEEDS = [
    {
        "id":                    prid("po", "PO-2024-001"),
        "package_id":            PKG_CIVIL,
        "po_number":             "PO-2024-001",
        "vendor_name":           "Tata Steel Limited",
        "description":           "Fe-500D TMT Reinforcement Bar — 12mm, 16mm, 20mm, 25mm, 32mm dia",
        "total_amount":          Decimal("45000000.00"),
        "currency":              "INR",
        "status":                POStatus.DISPATCHED,
        "committed_delivery_date": date(2024, 5, 15),
        "is_overdue":            False,
    },
    {
        "id":                    prid("po", "PO-2024-002"),
        "package_id":            PKG_CIVIL,
        "po_number":             "PO-2024-002",
        "vendor_name":           "ACC Limited",
        "description":           "OPC Grade 53 Cement — bulk supply for tunnel segment casting",
        "total_amount":          Decimal("18500000.00"),
        "currency":              "INR",
        "status":                POStatus.ACKNOWLEDGED,
        "committed_delivery_date": date(2024, 6, 30),
        "is_overdue":            False,
    },
    {
        "id":                    prid("po", "PO-2024-003"),
        "package_id":            PKG_ELEC,
        "po_number":             "PO-2024-003",
        "vendor_name":           "Siemens Mobility GmbH",
        "description":           "25kV AC Traction Power Equipment — TSS transformers, OCBs, protection relays",
        "total_amount":          Decimal("320000000.00"),
        "currency":              "INR",
        "status":                POStatus.ISSUED,
        "committed_delivery_date": date(2024, 12, 31),
        "is_overdue":            False,
    },
    {
        "id":                    prid("po", "PO-2024-004"),
        "package_id":            PKG_CIVIL,
        "po_number":             "PO-2024-004",
        "vendor_name":           "Doka Formwork India Pvt Ltd",
        "description":           "Tunnel formwork system — sliding formwork for station box walls",
        "total_amount":          Decimal("8200000.00"),
        "currency":              "INR",
        "status":                POStatus.DRAFT,
        "committed_delivery_date": date(2024, 8, 31),
        "is_overdue":            False,
    },
    {
        "id":                    prid("po", "PO-2024-005"),
        "package_id":            PKG_SIG,
        "po_number":             "PO-2024-005",
        "vendor_name":           "Alstom Transport SA",
        "description":           "CBTC Signalling System — wayside equipment, OBU, ATS workstations",
        "total_amount":          Decimal("480000000.00"),
        "currency":              "INR",
        "status":                POStatus.ISSUED,
        "committed_delivery_date": date(2025, 3, 31),
        "is_overdue":            False,
    },
    {
        "id":                    prid("po", "PO-2024-006"),
        "package_id":            PKG_CIVIL,
        "po_number":             "PO-2024-006",
        "vendor_name":           "Fosroc Chemicals India Pvt Ltd",
        "description":           "Waterproofing membrane & joint sealing — HDPE membrane, hydrophilic strip",
        "total_amount":          Decimal("6800000.00"),
        "currency":              "INR",
        "status":                POStatus.CLOSED,
        "committed_delivery_date": date(2024, 4, 30),
        "is_overdue":            False,
    },
]

# ---------------------------------------------------------------------------
# PO Line Items
# ---------------------------------------------------------------------------

PO_LINE_ITEM_SEEDS = [
    # PO-001: Tata Steel rebar
    {"id": prid("po_item","PO-001-I01"), "po_id": prid("po","PO-2024-001"),
     "item_code":"TSL/TMT/12", "description":"TMT Fe-500D 12mm dia",
     "unit":"MT", "quantity":Decimal("120"), "unit_rate":Decimal("72000"),
     "amount":Decimal("8640000")},
    {"id": prid("po_item","PO-001-I02"), "po_id": prid("po","PO-2024-001"),
     "item_code":"TSL/TMT/16", "description":"TMT Fe-500D 16mm dia",
     "unit":"MT", "quantity":Decimal("200"), "unit_rate":Decimal("71500"),
     "amount":Decimal("14300000")},
    {"id": prid("po_item","PO-001-I03"), "po_id": prid("po","PO-2024-001"),
     "item_code":"TSL/TMT/25", "description":"TMT Fe-500D 25mm dia",
     "unit":"MT", "quantity":Decimal("280"), "unit_rate":Decimal("78750"),
     "amount":Decimal("22050000")},

    # PO-002: ACC Cement
    {"id": prid("po_item","PO-002-I01"), "po_id": prid("po","PO-2024-002"),
     "item_code":"ACC/OPC53/BLK", "description":"OPC Grade 53 — bulk (per MT)",
     "unit":"MT", "quantity":Decimal("5000"), "unit_rate":Decimal("3700"),
     "amount":Decimal("18500000")},

    # PO-003: Siemens traction
    {"id": prid("po_item","PO-003-I01"), "po_id": prid("po","PO-2024-003"),
     "item_code":"SIE/TSS/XFMR", "description":"33/25kV Traction Transformer 12MVA (5 units)",
     "unit":"No.", "quantity":Decimal("5"), "unit_rate":Decimal("32000000"),
     "amount":Decimal("160000000")},
    {"id": prid("po_item","PO-003-I02"), "po_id": prid("po","PO-2024-003"),
     "item_code":"SIE/OCB/25KV", "description":"25kV Outdoor Circuit Breaker (10 units)",
     "unit":"No.", "quantity":Decimal("10"), "unit_rate":Decimal("8000000"),
     "amount":Decimal("80000000")},
    {"id": prid("po_item","PO-003-I03"), "po_id": prid("po","PO-2024-003"),
     "item_code":"SIE/RELAY/SET", "description":"Protection Relay Panel (10 panels)",
     "unit":"No.", "quantity":Decimal("10"), "unit_rate":Decimal("8000000"),
     "amount":Decimal("80000000")},

    # PO-005: Alstom CBTC
    {"id": prid("po_item","PO-005-I01"), "po_id": prid("po","PO-2024-005"),
     "item_code":"ALT/CBTC/WSY", "description":"Wayside Interlocking & Zone Controller units",
     "unit":"LS", "quantity":Decimal("1"), "unit_rate":Decimal("250000000"),
     "amount":Decimal("250000000")},
    {"id": prid("po_item","PO-005-I02"), "po_id": prid("po","PO-2024-005"),
     "item_code":"ALT/CBTC/ATS", "description":"ATS Workstations & OCC Software",
     "unit":"LS", "quantity":Decimal("1"), "unit_rate":Decimal("120000000"),
     "amount":Decimal("120000000")},
    {"id": prid("po_item","PO-005-I03"), "po_id": prid("po","PO-2024-005"),
     "item_code":"ALT/CBTC/OBU", "description":"On-Board Units (per rolling stock set)",
     "unit":"set", "quantity":Decimal("18"), "unit_rate":Decimal("6111111"),
     "amount":Decimal("110000000")},

    # PO-006: Fosroc waterproofing
    {"id": prid("po_item","PO-006-I01"), "po_id": prid("po","PO-2024-006"),
     "item_code":"FOS/HDPE/1.5", "description":"HDPE waterproofing membrane 1.5mm (per m²)",
     "unit":"m²", "quantity":Decimal("18000"), "unit_rate":Decimal("350"),
     "amount":Decimal("6300000")},
    {"id": prid("po_item","PO-006-I02"), "po_id": prid("po","PO-2024-006"),
     "item_code":"FOS/HYDRO/STR", "description":"Hydrophilic strip 20×10mm (per m)",
     "unit":"m", "quantity":Decimal("2000"), "unit_rate":Decimal("250"),
     "amount":Decimal("500000")},
]

# ---------------------------------------------------------------------------
# GRNs
# ---------------------------------------------------------------------------

GRN_SEEDS = [
    {
        "id":              prid("grn", "GRN-2024-001"),
        "po_id":           prid("po", "PO-2024-001"),
        "package_id":      PKG_CIVIL,
        "grn_number":      "GRN-2024-001",
        "received_date":   date(2024, 5, 12),
        "received_qty":    Decimal("400"),
        "ordered_qty":     Decimal("600"),
        "unit":            "MT",
        "status":          GRNStatus.ACCEPTED,
        "test_certificate_ref": "TC-TATASTEEL-2024-0512",
        "inspector":       "M. Singh (Site Inspector)",
        "remarks":         "First delivery 400MT accepted. Balance 200MT to follow in GRN-002.",
    },
    {
        "id":              prid("grn", "GRN-2024-002"),
        "po_id":           prid("po", "PO-2024-001"),
        "package_id":      PKG_CIVIL,
        "grn_number":      "GRN-2024-002",
        "received_date":   date(2024, 5, 28),
        "received_qty":    Decimal("175"),
        "ordered_qty":     Decimal("200"),
        "unit":            "MT",
        "status":          GRNStatus.PARTIALLY_ACCEPTED,
        "test_certificate_ref": "TC-TATASTEEL-2024-0528",
        "inspector":       "M. Singh (Site Inspector)",
        "remarks":         "25MT 32mm dia rejected — surface corrosion exceeds IS 1786 limit. "
                           "Vendor to replace.",
    },
    {
        "id":              prid("grn", "GRN-2024-003"),
        "po_id":           prid("po", "PO-2024-002"),
        "package_id":      PKG_CIVIL,
        "grn_number":      "GRN-2024-003",
        "received_date":   date(2024, 6, 18),
        "received_qty":    Decimal("2000"),
        "ordered_qty":     Decimal("5000"),
        "unit":            "MT",
        "status":          GRNStatus.ACCEPTED,
        "test_certificate_ref": "TC-ACC-2024-0618",
        "inspector":       "M. Singh (Site Inspector)",
        "remarks":         "First cement delivery accepted. Compressive strength @ 28 days: 56 N/mm².",
    },
    {
        "id":              prid("grn", "GRN-2024-004"),
        "po_id":           prid("po", "PO-2024-006"),
        "package_id":      PKG_CIVIL,
        "grn_number":      "GRN-2024-004",
        "received_date":   date(2024, 4, 22),
        "received_qty":    Decimal("18000"),
        "ordered_qty":     Decimal("18000"),
        "unit":            "m²",
        "status":          GRNStatus.ACCEPTED,
        "test_certificate_ref": "TC-FOSROC-2024-0422",
        "inspector":       "P. Iyer (QC Manager)",
        "remarks":         "Full delivery accepted. Third-party test certificate attached.",
    },
]

# ---------------------------------------------------------------------------
# Material Links
# ---------------------------------------------------------------------------

ML_SEEDS = [
    {
        "id":                   prid("ml", "ML-2024-001"),
        "package_id":           PKG_CIVIL,
        "material_name":        "Fe-500D TMT Rebar — all dia",
        "activity_id":          ACT_TBM,
        "po_id":                prid("po", "PO-2024-001"),
        "is_critical_path":     True,
        "risk_score":           25,
        "risk_level":           RiskLevel.LOW,
        "status":               MaterialLinkStatus.ON_TRACK,
        "planned_delivery_date": date(2024, 5, 15),
        "actual_delivery_date": date(2024, 5, 12),
        "last_risk_refresh":    NOW - timedelta(days=1),
    },
    {
        "id":                   prid("ml", "ML-2024-002"),
        "package_id":           PKG_CIVIL,
        "material_name":        "OPC Grade 53 Cement",
        "activity_id":          ACT_TBM,
        "po_id":                prid("po", "PO-2024-002"),
        "is_critical_path":     True,
        "risk_score":           30,
        "risk_level":           RiskLevel.LOW,
        "status":               MaterialLinkStatus.ON_TRACK,
        "planned_delivery_date": date(2024, 6, 30),
        "actual_delivery_date": None,
        "last_risk_refresh":    NOW - timedelta(days=1),
    },
    {
        "id":                   prid("ml", "ML-2024-003"),
        "package_id":           PKG_ELEC,
        "material_name":        "25kV Traction Power Equipment (Transformers + OCBs)",
        "activity_id":          ACT_TRAC,
        "po_id":                prid("po", "PO-2024-003"),
        "is_critical_path":     True,
        "risk_score":           65,
        "risk_level":           RiskLevel.MEDIUM,
        "status":               MaterialLinkStatus.AT_RISK,
        "planned_delivery_date": date(2024, 12, 31),
        "actual_delivery_date": None,
        "last_risk_refresh":    NOW - timedelta(days=2),
    },
    {
        "id":                   prid("ml", "ML-2024-004"),
        "package_id":           PKG_CIVIL,
        "material_name":        "Precast PSC Girder — 40m spans",
        "activity_id":          ACT_STATION,
        "po_id":                None,
        "is_critical_path":     True,
        "risk_score":           85,
        "risk_level":           RiskLevel.HIGH,
        "status":               MaterialLinkStatus.OVERDUE,
        "planned_delivery_date": date(2024, 5, 31),
        "actual_delivery_date": None,
        "last_risk_refresh":    NOW - timedelta(hours=6),
    },
    {
        "id":                   prid("ml", "ML-2024-005"),
        "package_id":           PKG_SIG,
        "material_name":        "CBTC Wayside & Onboard Equipment",
        "activity_id":          ACT_SIG,
        "po_id":                prid("po", "PO-2024-005"),
        "is_critical_path":     True,
        "risk_score":           55,
        "risk_level":           RiskLevel.MEDIUM,
        "status":               MaterialLinkStatus.AT_RISK,
        "planned_delivery_date": date(2025, 3, 31),
        "actual_delivery_date": None,
        "last_risk_refresh":    NOW - timedelta(days=1),
    },
]


# ---------------------------------------------------------------------------
# Seed runner
# ---------------------------------------------------------------------------

async def _exists(db, model, pk_col, pk_val) -> bool:
    return (await db.execute(select(model).where(pk_col == pk_val))).scalar_one_or_none() is not None


async def seed() -> None:
    async with async_session_factory() as db:
        counts = {k: 0 for k in ["pos", "po_items", "grns", "material_links"]}

        for po in PO_SEEDS:
            if not await _exists(db, PO, PO.id, po["id"]):
                db.add(PO(**{k: v for k, v in po.items() if k not in ("created_at","updated_at")},
                                     created_at=NOW - timedelta(days=60),
                                     updated_at=NOW))
                counts["pos"] += 1
        await db.flush()

        for li in PO_LINE_ITEM_SEEDS:
            if not await _exists(db, POLineItem, POLineItem.id, li["id"]):
                db.add(POLineItem(**{k: v for k, v in li.items() if k != "created_at"},
                                             created_at=NOW - timedelta(days=60)))
                counts["po_items"] += 1
        await db.flush()

        for grn in GRN_SEEDS:
            if not await _exists(db, GoodsReceipt, GoodsReceipt.id, grn["id"]):
                db.add(GoodsReceipt(**{k: v for k, v in grn.items() if k != "created_at"},
                                      created_at=NOW - timedelta(days=30)))
                counts["grns"] += 1
        await db.flush()

        for ml in ML_SEEDS:
            if not await _exists(db, MaterialScheduleLink, MaterialScheduleLink.id, ml["id"]):
                db.add(MaterialScheduleLink(**{k: v for k, v in ml.items() if k not in ("created_at","updated_at")},
                                               created_at=NOW - timedelta(days=60),
                                               updated_at=NOW))
                counts["material_links"] += 1
        await db.flush()

        await db.commit()

        print("\n=== Seeded Procurement Module ===")
        for k, v in counts.items():
            print(f"  {k:20s} {v} new")

        print("\n--- PO IDs ---")
        for po in PO_SEEDS:
            print(f"  {po['po_number']}  {po['status'].value:15s}  {po['id']}")

        print("\n--- Material Links (risk status) ---")
        for ml in ML_SEEDS:
            print(f"  {ml['material_name'][:40]:42s} {ml['status'].value:10s}  {ml['risk_level'].value}")
        print()


if __name__ == "__main__":
    asyncio.run(seed())
