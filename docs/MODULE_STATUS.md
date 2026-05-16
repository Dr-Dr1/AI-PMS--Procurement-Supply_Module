# Procurement & Supply Module — Status

> **Snapshot:** 2026-05-14 · `main` branch · backend port 8003 · frontend port 5176 (prod) / 5174 (Vite dev)

The AI-PMS Procurement & Supply Module covers SRS module **M08 (Procurement & Materials)** — PO tracking, delivery capture, material-schedule linking, and CP-impact alerts.

---

## 1. Built — Backend Sub-Modules

All under `backend/app/modules/procurement_module/`. Routes mounted at prefix `/api/v1`.

### 1.1 `po_sub_module/`
| Method | Path | Notes |
|---|---|---|
| `POST` | `/procurement/pos` | Create PO (status = DRAFT) |
| `GET` | `/procurement/pos` | List by `package_id` + status filter |
| `GET` | `/procurement/pos/{po_id}` | Detail |
| `PATCH` | `/procurement/pos/{po_id}` | Update metadata |
| `DELETE` | `/procurement/pos/{po_id}` | Delete (DRAFT only) |
| `POST` | `/procurement/pos/{po_id}/issue` | DRAFT → ISSUED |
| `POST` | `/procurement/pos/{po_id}/acknowledge` | ISSUED → ACKNOWLEDGED |
| `POST` | `/procurement/pos/{po_id}/dispatch` | ACKNOWLEDGED → DISPATCHED |
| `POST` | `/procurement/pos/{po_id}/close` | DISPATCHED → CLOSED |
| `POST` | `/procurement/pos/{po_id}/items` | Add line item |
| `GET` | `/procurement/pos/{po_id}/items` | List line items |
| `PATCH` | `/procurement/pos/{po_id}/items/{item_id}` | Update line item |
| `DELETE` | `/procurement/pos/{po_id}/items/{item_id}` | Delete line item |

Service: `POService` · Repository: `PORepository` · DTOs: `POCreateDTO`, `POUpdateDTO`, `POLineItemCreateDTO`, `POLineItemUpdateDTO`, `POResponseDTO`, `POLineItemResponseDTO`.

### 1.2 `goods_receipt_sub_module/`
| Method | Path | Notes |
|---|---|---|
| `POST` | `/procurement/grns` | Create GRN (immutable after) |
| `GET` | `/procurement/grns` | List by `package_id` + optional `po_id` + date filters |
| `GET` | `/procurement/grns/{grn_id}` | Detail |

Service: `GRNService` · Repository: `GRNRepository`.

### 1.3 `material_link_sub_module/`
| Method | Path | Notes |
|---|---|---|
| `POST` | `/procurement/material-links` | Create link |
| `GET` | `/procurement/material-links` | List with `risk_level`, `on_critical_path` filters |
| `GET` | `/procurement/material-links/{link_id}` | Detail |
| `PATCH` | `/procurement/material-links/{link_id}` | Update |
| `DELETE` | `/procurement/material-links/{link_id}` | Delete |
| `POST` | `/procurement/material-links/bulk-refresh` | Recompute `risk_score` across many |
| `GET` | `/procurement/material-links/risk-score/{link_id}` | Read latest score |

Service: `MaterialLinkService` · Repository: `MaterialLinkRepository`. Risk computation is **rule-based** (PO status + delivery delta + critical-path flag) — no AI yet. See [`features/MATERIAL_RISK_AI.md`](./features/MATERIAL_RISK_AI.md).

### 1.4 `dashboard_sub_module/`
| Method | Path | Notes |
|---|---|---|
| `GET` | `/procurement/dashboard?package_id=...` | KPI aggregation: PO status breakdown, GRN pending acceptance, risk distribution |

---

## 2. Built — Models

`backend/app/models_v2/procurement.py`:

| Class | Table | Key columns |
|---|---|---|
| `ProcurementPO` | `procurement_pos` | `id`, `package_id`, `po_number` (unique), `vendor_name`, `description`, `total_amount` (Numeric 15,2), `currency` (default INR), `status` (POStatus), `committed_delivery_date`, `is_overdue`, `created_at`, `updated_at` |
| `ProcurementPOLineItem` | `procurement_po_line_items` | `id`, `po_id` (FK cascade), `item_code`, `description`, `unit`, `quantity` (Numeric 14,4), `unit_rate`, `amount` |
| `ProcurementGRN` | `procurement_grns` | `id`, `po_id` (FK), `package_id`, `grn_number` (unique), `received_date`, `received_qty`, `ordered_qty`, `unit`, `status` (GRNStatus), `test_certificate_ref`, `inspector`, `remarks` |
| `ProcurementMaterialLink` | `procurement_material_links` | `id`, `package_id`, `material_name`, `activity_id` (P6 string), `po_id` (FK nullable), `is_critical_path`, `risk_score` (int), `risk_level` (RiskLevel), `status` (MaterialLinkStatus), `planned_delivery_date`, `actual_delivery_date`, `last_risk_refresh` |

Enums in `backend/app/core/enums.py`:
- `POStatus`: DRAFT, ISSUED, ACKNOWLEDGED, DISPATCHED, CLOSED
- `GRNStatus`: PENDING, ACCEPTED, PARTIALLY_ACCEPTED, REJECTED
- `RiskLevel`: LOW, MEDIUM, HIGH
- `MaterialLinkStatus`: ON_TRACK, AT_RISK, OVERDUE

CDM fields **not yet in the model** (deferred to feature branches):
- Vendor master FK (currently free-text `vendor_name`) → [`features/VENDOR_REGISTRY.md`](./features/VENDOR_REGISTRY.md)
- Photo + GPS evidence on GRN → [`features/DELIVERY_PHOTO_EVIDENCE.md`](./features/DELIVERY_PHOTO_EVIDENCE.md)
- Soft-delete column → [`features/PAGINATION_AND_SOFT_DELETE.md`](./features/PAGINATION_AND_SOFT_DELETE.md)
- Approval chain reference on PO → [`features/PO_APPROVAL_CHAIN.md`](./features/PO_APPROVAL_CHAIN.md)

---

## 3. Migrations

| Revision | File | Creates |
|---|---|---|
| `afa3fc3d28c5` | `backend/alembic/versions/afa3fc3d28c5_add_new_module_tables.py` | Shared schedule_v2 + quality tables (read-only deps) |
| `002` | `backend/alembic/versions/002_create_procurement_module_tables.py` | 4 procurement tables + 4 enums (`po_status_enum`, `grn_status_enum`, `risk_level_enum`, `material_link_status_enum`) + indexes |
| `8442c332232d` | `backend/alembic/versions/8442c332232d_create_procurement_table.py` | Legacy — superseded by `002`. Do not run. |

---

## 4. Built — Frontend

`frontend/src/pages/procurement.jsx` — tabbed shell with cascading Project → Corridor → Package selectors and 4 tabs.

| Tab | Component | Status |
|---|---|---|
| Dashboard | `ProcurementDashboard.jsx` | Built |
| POs | `POTab.jsx` | Built (CRUD + 5-button workflow + line items) |
| GRNs | `GRNTab.jsx` | Built (create + read-only after) |
| Material Links | `MaterialLinksTab.jsx` | Built (CRUD + risk refresh) |

Shared: `ProcurementModal.jsx`, `ProcurementBadge.jsx`.

API client: `frontend/src/apis/procurementApi.js` — axios helpers per endpoint, base URL `${VITE_PROCUREMENT_API_URL}/api/v1`.

---

## 5. Known Gaps

| Gap | Affects | Tracked in |
|---|---|---|
| Single-step PO issue (no approval chain) | `po_sub_module` | [`features/PO_APPROVAL_CHAIN.md`](./features/PO_APPROVAL_CHAIN.md) |
| GRN `test_certificate_ref` not linked to Quality ITP/RFI | `goods_receipt_sub_module` | [`features/GRN_QC_INTEGRATION.md`](./features/GRN_QC_INTEGRATION.md) |
| Rule-based risk score — no predictive model (FR-M08-003 A09) | `material_link_sub_module` | [`features/MATERIAL_RISK_AI.md`](./features/MATERIAL_RISK_AI.md) |
| CP-impact alert (FR-M08-004) — flag exists, notification fan-out missing | new sub-module | [`features/CP_IMPACT_ALERTS.md`](./features/CP_IMPACT_ALERTS.md) |
| No vendor master — `vendor_name` is free text | `po_sub_module` + new | [`features/VENDOR_REGISTRY.md`](./features/VENDOR_REGISTRY.md) |
| No photo + GPS evidence on GRN (FR-M12-003 / NFR-24) | `goods_receipt_sub_module` | [`features/DELIVERY_PHOTO_EVIDENCE.md`](./features/DELIVERY_PHOTO_EVIDENCE.md) |
| No immutable audit log (NFR-16) | All mutating endpoints | [`features/AUDIT_TRAIL_LOGGING.md`](./features/AUDIT_TRAIL_LOGGING.md) |
| List endpoints lack pagination; no soft-delete on PO | All list endpoints | [`features/PAGINATION_AND_SOFT_DELETE.md`](./features/PAGINATION_AND_SOFT_DELETE.md) |
| No Procurement Agent (A09) — reorder, slip forecast, vendor scoring | new sub-module | [`features/PROCUREMENT_AGENT_AI.md`](./features/PROCUREMENT_AGENT_AI.md) |

---

## 6. Reference traceability

| SRS / CDM ref | Status |
|---|---|
| FR-M08-001 (PO tracking + lifecycle) | Built |
| FR-M08-002 (delivery capture / GRN) | Built (basic — no photo/GPS, no QC link) |
| FR-M08-003 (material-schedule link) | Built (rule-based risk; A09 AI not built) |
| FR-M08-004 (CP-impact alert) | Partial (flag captured; notification fan-out **not built**) |
| FR-M12-003 (GPS + photo evidence) | **Not built** |
| NFR-11 (tamper-evidence on GRN test cert) | **Not built** |
| NFR-16 (immutable audit) | **Not built** |
| NFR-24 (offline mobile capture) | **Not built** |
| NFR-34 (explainability — risk score) | **Not built** |
| NFR-35 (HITL on AI recommendations) | N/A until A09 built |

---

## 7. How to extend this module

1. Find the feature in [`features/README.md`](./features/README.md). If missing, copy [`features/_TEMPLATE.md`](./features/_TEMPLATE.md) and add a row to the index.
2. The feature md file names the working branch — `git checkout -b feat/<name>` from `main`.
3. Implement per the **§9 File Touch List** in that feature md.
4. PR back to `main`. Update the feature's status block (`Planned` → `In progress` → `Built`) and §5 above.

## 8. Future Work

See [`features/README.md`](./features/README.md) for the full list of planned feature build guides.
