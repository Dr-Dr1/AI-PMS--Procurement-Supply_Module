# Procurement & Supply Module (M08) — Introduction

Brief on what this module is, what it does, and why it matters. Source: AI-PMS SRS v1.0 §3.8 / §F08, CDM v1.2, Backend KT v1.0.

## What it is

Procurement and material-supply backbone for AI-PMS. Tracks every Purchase Order (PO) issued against a project package, every Goods Receipt Note (GRN) recorded against those POs, and every material-to-activity link that ties a piece of steel, cable, or panel to a scheduled construction activity. Backbone for cash-flow forecasting (M03), critical-path protection (M01), and on-site delivery audit (M12).

## Core features (FR-M08)

| FR ID | Feature | Priority |
|---|---|---|
| FR-M08-001 | PO Tracking — full lifecycle DRAFT → ISSUED → ACKNOWLEDGED → DISPATCHED → CLOSED with vendor, currency, total amount, committed delivery date. | Critical |
| FR-M08-002 | Delivery Capture — GRN records what arrived, when, in what quantity, with what test certificate; immutable after creation. | Critical |
| FR-M08-003 | Material-Schedule Linking — every material tied to a P6 `activity_id` so a slip in delivery surfaces as a schedule risk. Procurement Agent (A09) populates `delay_risk_score`. | Critical |
| FR-M08-004 | CP-Impact Material Alert — if a critical-path activity depends on a material with high `delay_risk_score`, raise Tier-0 alert to PM + Planning Manager + Procurement Manager simultaneously. | Critical |

## Extended scope (per-feature build guides under `features/`)

- **PO approval chain** — multi-step approval for high-value POs (currently single-state issue).
- **GRN ↔ QC integration** — auto-link GRN's `test_certificate_ref` to Quality Module ITP / RFI verification.
- **Material risk AI** — replace rule-based `risk_score` with predictive model trained on vendor history + lead times.
- **CP-impact alerts** — wire FR-M08-004 from `is_critical_path` flag through to notification fan-out.
- **Vendor registry** — vendor master table + historical performance (currently free-text `vendor_name`).
- **Delivery photo evidence** — mobile capture of arrival photo + GPS per FR-M12-003 / NFR-24.
- **Audit trail logging** — immutable audit on PO + GRN state changes (NFR-16).
- **Pagination + soft delete** — list APIs.
- **Procurement Agent (A09)** — reorder-point suggestions, overdue detection, delivery-slip forecast.

## Why useful

1. **Schedule protection** — every PO links to a package; every material to an activity. A delayed PO triggers a downstream schedule alert, not a surprise three weeks later when the crew can't pour.
2. **Cash-flow grounding** — M03 cash-flow projections pull from PO `total_amount` + `committed_delivery_date` + GRN actuals. No re-keying.
3. **Audit-ready GRNs** — once created, a GRN is immutable. The inspector and test-certificate reference are captured at receipt time, satisfying NFR-16 and giving QA a clean evidence trail.
4. **CP-impact early warning** — `is_critical_path` flag on `ProcurementMaterialLink` is the hook for FR-M08-004 Tier-0 alerts; when wired to a notification fan-out the PM finds out about a 3-day rebar slip on the same morning, not at the next coordination meeting.
5. **API-first** — OpenAPI 3.x, paginated lists planned, integrates with ERP vendor masters and external e-Procurement portals (Phase 2 / M23).
6. **Shared `aipms_dmrc` DB** — same Postgres instance as Quality (M02) and Cost (M03); cross-module FKs let one query span PO → GRN → RFI verification → RA Bill claim.

## Users (key roles touching M08)

| Role | Tier | What they do here |
|---|---|---|
| Procurement Manager | L2 | Approves POs, monitors vendor performance, reviews CP-impact alerts. |
| Planning Manager | L2 | Receives CP-impact alerts; cross-references material slip vs schedule float. |
| Materials Engineer | L3 | Creates POs, raises GRNs at site stores, maintains material-activity links. |
| Site Storekeeper | L4 | Records actual receipts, attaches test certificates, photographs deliveries. |
| QA/QC Engineer | L3 | Reads GRN's `test_certificate_ref` from incoming consignment; links to ITP/RFI. |
| Finance / Accounts | L3 | Reads PO + GRN to certify RA Bill claims (M03 integration). |
| Procurement Agent (A09) | AI | Auto-computes `risk_score`, suggests reorder points, flags impending CP slip. |

## Walkthrough — a real story on our project

**Scenario: "OHE cantilever delivery on Phase-1 Metro Viaduct."**

**Day 1 — PO creation (FR-M08-001)**
Anita (Materials Engineer) opens AI-PMS → Procurement → POs → New. Vendor = `Salzgitter Rail Logistics`. Total = `INR 4,82,00,000`. Currency = `INR`. Committed delivery = `2026-06-20`. Two line items: 120 nos. cantilever masts @ INR 3.2 L, 480 nos. cross-arms @ INR 22 K. Status = `DRAFT`.

She clicks **Issue**. Status → `ISSUED`. A `ProcurementMaterialLink` is created automatically: `material_name = "OHE cantilever masts"`, `activity_id = "A1147"` (P6 ID for OHE erection between km 8.2–10.6), `planned_delivery_date = 2026-06-20`. Critical-path flag pulled from M01 baseline: `is_critical_path = true`.

**Day 14 — Vendor acknowledgement (FR-M08-001)**
Salzgitter emails MRT confirming order. Anita clicks **Acknowledge**. Status → `ACKNOWLEDGED`. Procurement Agent A09 begins watching `committed_delivery_date - today` and refreshes `risk_score` nightly.

**Day 45 — Dispatch (FR-M08-001)**
Vendor sends pre-shipment notice. Status → `DISPATCHED`. Expected at site stores by `2026-06-18`.

**Day 50 — Goods receipt (FR-M08-002)**
First 40 cantilever masts arrive at the Mukundpur site stores. Storekeeper Ramesh creates a GRN: `received_qty = 40`, `unit = nos.`, `received_date = 2026-06-18`, `test_certificate_ref = "TC-SAL-2026-0941"`, `inspector = "Ramesh / Site Stores"`, `status = ACCEPTED`. GRN is immutable from this point. QA picks up `TC-SAL-2026-0941`, attaches it to ITP-OHE-014, marks the material verified.

**Day 52 — Risk shift (FR-M08-003)**
Salzgitter notifies a 12-day delay on the remaining 80 masts. Anita updates the `ProcurementMaterialLink.planned_delivery_date`. Procurement Agent A09 recomputes: `risk_score = 78`, `risk_level = HIGH`, `status = AT_RISK`. Because `is_critical_path = true` and `risk_score > 60`, **CP-Impact Alert (FR-M08-004)** fires.

**Day 52 — CP-impact alert (FR-M08-004)**
Notification fan-out: PM (Geeta), Planning Manager (Suresh), Procurement Manager (Vivek) — all get an in-app + email + SMS at 11:04 AM IST. Subject: *"OHE cantilever PO #PO-OHE-241 — 12-day delivery slip on critical-path activity A1147. Risk = HIGH. Open: [link]."* Suresh reviews schedule float in M01: 4 days. He recommends a rolling 60-mast partial install to absorb the slip. Geeta approves. No quiet escalation later.

**Day 90 — PO close (FR-M08-001)**
All 120 masts received across 3 GRNs. Total received qty equals total ordered. Anita clicks **Close**. Status → `CLOSED`. Finance pulls PO + GRNs to certify the next RA Bill (M03 reads `received_qty * unit_rate` to validate the contractor's billing claim).

**Why this matters** — Anita, Ramesh, Vivek don't chase delivery status over WhatsApp. The PM hears about a slip the same hour it's known, not on day 60 when activity A1147 stalls. The GRN test certificate is one click from the QA ITP record. The RA Bill claim cross-checks against actual receipts. The auditor can trace every paisa to a PO line item, a GRN, and a test certificate.

## Reading order to study deeper

1. `AIPMS_SRS_v1_0_Definitive_29APR2026` — §3.8 M08 and §F08.
2. `AIPMS_CDM_v1.1` — `PurchaseOrder`, `GRN`, `MaterialScheduleLink` entities.
3. `AIPMS_CDM_Schema_v1` — table-level columns and FKs.
4. `AIPMS_KT_Backend_Lokesh` — §5.x Procurement section.
5. [`features/`](./features/) — per-feature build guides drafted in this repo.

## Related docs in this repo

- [`README.md`](./README.md) — repo doc index.
- [`MODULE_STATUS.md`](./MODULE_STATUS.md) — what is built today + roadmap.
- [`features/README.md`](./features/README.md) — feature build guide index.
