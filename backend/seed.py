"""
Seed script — inserts realistic DMRC procurement demo data.
Run: venv\\Scripts\\python seed.py

Inserts:
  1 import record
  1 project (CC-21)
  2 corridors (Line 8, Line 7)
  4 packages (2 per corridor)
  8 activities (2 per package)
  6 POs (3 for pkg1, 2 for pkg2, 1 for pkg3) with varied statuses
  12 line items across POs
  3 GRNs
  11 material links
"""

import uuid
from datetime import datetime

import psycopg2

DSN = "host=localhost port=5432 dbname=aipms_dmrc user=postgres password=#Lokesh123"


def uid():
    return str(uuid.uuid4())


def main():
    conn = psycopg2.connect(DSN)
    cur = conn.cursor()

    # Idempotency check
    cur.execute("SELECT id FROM schedule_v2_projects WHERE proj_short_name = 'CC-21' LIMIT 1")
    if cur.fetchone():
        print("Seed data already present (CC-21 project found). Run with --reset to re-seed.")
        cur.close()
        conn.close()
        return

    now = datetime.utcnow()

    # ── 1. Import record ───────────────────────────────────────────────────────
    import_id = uid()
    cur.execute(
        """
        INSERT INTO xer_imports
            (id, file_path, total_projects, total_activities, total_resources,
             total_calendars, total_wbs, total_relationships, total_corridors,
             total_packages, parse_response, created_at)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s::jsonb,%s)
        """,
        (import_id, "/seed/cc21_seed.xer", 1, 8, 0, 0, 0, 0, 2, 4, "{}", now),
    )

    # ── 2. Project ─────────────────────────────────────────────────────────────
    project_id = uid()
    proj_id_int = 1001
    cur.execute(
        """
        INSERT INTO schedule_v2_projects
            (id, import_id, proj_id, proj_short_name, proj_name,
             scd_start_date, scd_end_date, activity_count, completed, in_progress, not_started)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """,
        (
            project_id, import_id, proj_id_int,
            "CC-21",
            "DMRC Contract CC-21 — Janakpuri West to RK Ashram Marg",
            "01-Apr-2023", "31-Mar-2027",
            8, 1, 4, 3,
        ),
    )

    # ── 3. Corridors ───────────────────────────────────────────────────────────
    corr1 = uid()
    corr2 = uid()
    cur.execute(
        "INSERT INTO corridors (id,import_id,proj_id,corridor_name,corridor_code,created_at) VALUES (%s,%s,%s,%s,%s,%s)",
        (corr1, import_id, proj_id_int, "Line 8 — Magenta Line", "L8-MG", now),
    )
    cur.execute(
        "INSERT INTO corridors (id,import_id,proj_id,corridor_name,corridor_code,created_at) VALUES (%s,%s,%s,%s,%s,%s)",
        (corr2, import_id, proj_id_int, "Line 7 — Pink Line Extension", "L7-PK", now),
    )

    # ── 4. Packages ────────────────────────────────────────────────────────────
    pkg1 = uid()   # L8 Civil
    pkg2 = uid()   # L8 E&M
    pkg3 = uid()   # L7 Civil
    pkg4 = uid()   # L7 E&M

    pkgs = [
        (pkg1, corr1, "CC-21-CIV-01 Civil Works — Janakpuri West Station", "CC21-CIV-01", "Afcons Infrastructure Ltd"),
        (pkg2, corr1, "CC-21-EM-01 E&M Works — Janakpuri West Station",   "CC21-EM-01",  "BEML Ltd"),
        (pkg3, corr2, "CC-21-CIV-02 Civil Works — Moti Nagar Station",    "CC21-CIV-02", "L&T Construction"),
        (pkg4, corr2, "CC-21-EM-02 E&M Works — Moti Nagar Station",       "CC21-EM-02",  "Siemens Ltd"),
    ]
    for pid, cid, pname, pcode, cname in pkgs:
        cur.execute(
            """
            INSERT INTO packages
                (id,import_id,proj_id,corridor_id,package_name,package_code,contractor_name,created_at)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
            """,
            (pid, import_id, proj_id_int, cid, pname, pcode, cname, now),
        )

    # ── 5. Activities ──────────────────────────────────────────────────────────
    activities = [
        (pkg1, "A1001", "Pile Foundation Works"),
        (pkg1, "A1002", "Raft Foundation Casting"),
        (pkg2, "A2001", "Platform Screen Door Installation"),
        (pkg2, "A2002", "Escalator & Travelator Installation"),
        (pkg3, "A3001", "Diaphragm Wall Construction"),
        (pkg3, "A3002", "Concourse Slab Casting"),
        (pkg4, "A4001", "HVAC Ducting Installation"),
        (pkg4, "A4002", "Electrical Cabling — Station"),
    ]
    for pkg_id, p6id, aname in activities:
        cur.execute(
            """
            INSERT INTO activities
                (id,import_id,p6_activity_id,activity_name,package_id,proj_id,
                 is_critical,is_near_critical,requires_rfi,requires_material)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """,
            (uid(), import_id, p6id, aname, pkg_id, proj_id_int,
             False, False, False, True),
        )

    # ── 6. Purchase Orders ─────────────────────────────────────────────────────
    po1 = uid(); po2 = uid(); po3 = uid()
    po4 = uid(); po5 = uid(); po6 = uid()

    pos_data = [
        # (id, pkg, po_number, vendor, description, amount, currency, status, delivery_date, is_overdue)
        (po1, pkg1, "PO-CC21-001", "Tata Steel Ltd",
         "Supply of HYSD Reinforcement Steel Bars (Fe 500D)",
         18050000, "INR", "DRAFT", "2026-06-30", False),

        (po2, pkg1, "PO-CC21-002", "ACC Concrete Ltd",
         "Ready Mix Concrete Supply M30 Grade with Pump",
         2850000, "INR", "ISSUED", "2026-03-15", True),   # delivery date past → overdue

        (po3, pkg1, "PO-CC21-003", "SL Formwork Pvt Ltd",
         "Formwork Ply Board & Scaffolding Material",
         1200000, "INR", "DISPATCHED", "2026-04-30", False),

        (po4, pkg2, "PO-CC21-004", "Faiveley Transport India Ltd",
         "Full-Height Platform Screen Door Units (48 leaves)",
         18500000, "INR", "ACKNOWLEDGED", "2026-09-30", False),

        (po5, pkg2, "PO-CC21-005", "Mitsubishi Electric India Pvt Ltd",
         "Escalator & Moving Walkway Units",
         22000000, "INR", "ISSUED", "2026-10-31", False),

        (po6, pkg3, "PO-CC21-006", "JSW Steel Ltd",
         "Structural Steel — Wide Flange Beams & Plates",
         25850000, "INR", "CLOSED", "2026-03-31", False),
    ]

    for row in pos_data:
        pid, pkg_id, po_num, vendor, desc, amt, curr, status, del_date, overdue = row
        cur.execute(
            """
            INSERT INTO purchase_orders
                (id,package_id,po_number,vendor_name,description,total_amount,currency,
                 status,committed_delivery_date,is_overdue,created_at,updated_at)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """,
            (pid, pkg_id, po_num, vendor, desc, amt, curr, status, del_date, overdue, now, now),
        )

    # ── 7. Line Items ──────────────────────────────────────────────────────────
    line_items = [
        # PO-CC21-001 Steel
        (po1, "STL-001", "HYSD Bars 16mm Dia Fe500D",          "MT",  120,  72500,  8700000),
        (po1, "STL-002", "HYSD Bars 20mm Dia Fe500D",          "MT",   80,  73000,  5840000),
        (po1, "STL-003", "HYSD Bars 25mm Dia Fe500D",          "MT",   45,  78000,  3510000),
        # PO-CC21-002 Concrete
        (po2, "CON-001", "RMC M30 Grade with Pump",            "m³",  500,   5700,  2850000),
        # PO-CC21-003 Formwork
        (po3, "FW-001",  "Ply Board Shuttering 18mm",          "m²", 2000,    280,   560000),
        (po3, "FW-002",  "Steel Props & Cup-Lock Scaffolding", "MT",    8,  80000,   640000),
        # PO-CC21-004 PSD
        (po4, "PSD-001", "Full-Height PSD Unit 1500mm Wide",   "Nos",  48, 375000, 18000000),
        (po4, "PSD-002", "Emergency Access Door",              "Nos",   2, 250000,   500000),
        # PO-CC21-005 Escalators
        (po5, "ESC-001", "Escalator 800mm Rise 1:1.5",         "Nos",   4, 4500000, 18000000),
        (po5, "ESC-002", "Travelator / Moving Walkway 800mm",  "Nos",   2, 2000000,  4000000),
        # PO-CC21-006 Structural Steel (CLOSED)
        (po6, "SS-001",  "Wide Flange Beams (Various Sec.)",   "MT",  200,  76000, 15200000),
        (po6, "SS-002",  "Steel Plates 12mm & 20mm",           "MT",  150,  71000, 10650000),
    ]

    for po_id, icode, idesc, unit, qty, rate, amt in line_items:
        cur.execute(
            """
            INSERT INTO po_line_items
                (id,po_id,item_code,description,unit,quantity,unit_rate,amount,created_at)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """,
            (uid(), po_id, icode, idesc, unit, qty, rate, amt, now),
        )

    # ── 8. GRNs ────────────────────────────────────────────────────────────────
    grns_data = [
        # Against PO3 (DISPATCHED) — formwork partial delivery
        (po3, pkg1, "GRN-CC21-001", "2026-04-10", 1800, None,  "m²",
         "ACCEPTED", "TC-FW-2026-001", "Ramesh Kumar", "Partial delivery per site programme"),
        # Against PO6 (CLOSED) — steel deliveries
        (po6, pkg3, "GRN-CC21-002", "2026-03-10", 195.5, 200.0, "MT",
         "ACCEPTED", "TC-SS-2026-001", "S. Venkatesh", "Lot 1 verified and stacked at yard"),
        (po6, pkg3, "GRN-CC21-003", "2026-03-25", 148.2, 150.0, "MT",
         "PARTIALLY_ACCEPTED", "TC-SS-2026-002", "S. Venkatesh", "1.8 MT rejected due to surface corrosion"),
    ]

    for po_id, pkg_id, grn_num, rec_date, recv_qty, ord_qty, unit, status, tc, inspector, remarks in grns_data:
        cur.execute(
            """
            INSERT INTO goods_receipts
                (id,po_id,package_id,grn_number,received_date,received_qty,ordered_qty,
                 unit,status,test_certificate_ref,inspector,remarks,created_at)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """,
            (uid(), po_id, pkg_id, grn_num, rec_date, recv_qty, ord_qty,
             unit, status, tc, inspector, remarks, now),
        )

    # ── 9. Material Links ──────────────────────────────────────────────────────
    # (pkg_id, material_name, activity_id, po_id, is_cp, risk_score, risk_level, status, plan_date, actual_date)
    ml_rows = [
        # Package 1 — Civil
        (pkg1, "Steel Reinforcement Bars Fe500D",   "A1001", po1, True,  65, "HIGH",   "AT_RISK",  "2026-04-30", None),
        (pkg1, "Ready Mix Concrete M30 Grade",      "A1002", po2, True,  85, "HIGH",   "OVERDUE",  "2026-03-15", None),
        (pkg1, "Shuttering Ply & Formwork Material","A1001", po3, False, 40, "MEDIUM", "ON_TRACK", "2026-05-15", "2026-04-10"),
        (pkg1, "Binding Wire & Accessories",         None,    None,False, 10, "LOW",    "ON_TRACK", "2026-06-30", None),
        # Package 2 — E&M
        (pkg2, "Platform Screen Door Units",         "A2001", po4, True,  30, "MEDIUM", "ON_TRACK", "2026-09-30", None),
        (pkg2, "Escalator & Travelator Units",       "A2002", po5, True,  25, "MEDIUM", "ON_TRACK", "2026-10-31", None),
        (pkg2, "Station Lighting Fixtures LED",      "A2002", None, False, 15, "LOW",   "ON_TRACK", "2026-11-30", None),
        # Package 3 — Civil
        (pkg3, "Structural Steel Members",           "A3001", po6, True,   0, "LOW",    "ON_TRACK", "2026-03-31", "2026-03-25"),
        (pkg3, "Concrete Admixtures & Waterproofing","A3002", None, False, 15, "LOW",   "ON_TRACK", "2026-06-15", None),
        # Package 4 — E&M
        (pkg4, "HVAC Ducting Material",              "A4001", None, False, 20, "LOW",   "ON_TRACK", "2026-07-31", None),
        (pkg4, "MV & LV Power Cables",              "A4002", None, True,  50, "HIGH",  "AT_RISK",  "2026-06-30", None),
    ]

    for pkg_id, mname, act_id, po_id, is_cp, risk_score, risk_level, status, plan_date, actual_date in ml_rows:
        cur.execute(
            """
            INSERT INTO material_links
                (id,package_id,material_name,activity_id,po_id,is_critical_path,
                 risk_score,risk_level,status,planned_delivery_date,actual_delivery_date,
                 created_at,updated_at)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """,
            (uid(), pkg_id, mname, act_id, po_id, is_cp,
             risk_score, risk_level, status, plan_date, actual_date, now, now),
        )

    conn.commit()
    cur.close()
    conn.close()

    print("Seed complete!")
    print("  Import   : 1")
    print("  Project  : CC-21 (proj_id=1001)")
    print("  Corridors: L8-MG, L7-PK")
    print("  Packages : CC21-CIV-01, CC21-EM-01, CC21-CIV-02, CC21-EM-02")
    print("  Activities: 8")
    print("  POs      : 6 (DRAFT/ISSUED/DISPATCHED/ACKNOWLEDGED/CLOSED)")
    print("  Line items: 12")
    print("  GRNs     : 3")
    print("  Mat links: 11")


if __name__ == "__main__":
    import sys
    if "--reset" in sys.argv:
        conn = psycopg2.connect(DSN)
        cur = conn.cursor()
        cur.execute("DELETE FROM material_links")
        cur.execute("DELETE FROM goods_receipts")
        cur.execute("DELETE FROM po_line_items")
        cur.execute("DELETE FROM purchase_orders")
        cur.execute("DELETE FROM activities WHERE import_id IN (SELECT id FROM xer_imports WHERE file_path='/seed/cc21_seed.xer')")
        cur.execute("DELETE FROM packages WHERE import_id IN (SELECT id FROM xer_imports WHERE file_path='/seed/cc21_seed.xer')")
        cur.execute("DELETE FROM corridors WHERE import_id IN (SELECT id FROM xer_imports WHERE file_path='/seed/cc21_seed.xer')")
        cur.execute("DELETE FROM schedule_v2_projects WHERE proj_short_name='CC-21'")
        cur.execute("DELETE FROM xer_imports WHERE file_path='/seed/cc21_seed.xer'")
        conn.commit()
        cur.close()
        conn.close()
        print("Reset done. Re-running seed...")
    main()
