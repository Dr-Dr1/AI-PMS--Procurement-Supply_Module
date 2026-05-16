# Feature Build Guide: Vendor Master + Performance Registry

---

## Working Branch — `feat/vendor-registry`

```bash
git checkout main
git pull origin main
git checkout -b feat/vendor-registry
```

---

> **Status:** Planned
> **Branch:** `feat/vendor-registry` (branch from `main`)
> **Target sub-module:** new `vendor_sub_module/`
> **SRS refs:** FR-M08-001 (linked vendor master), FR-M08-003 (vendor history feeds risk)

---

## 1. Feature Summary

**Problem.** `ProcurementPO.vendor_name` is a free-text string. The same vendor shows up as `"Salzgitter Rail"`, `"Salzgitter Rail Logistics"`, `"SR Logistics"`. No registered identifiers, no consolidated history, no performance scoring possible — which directly hurts FR-M08-003 risk computation.

**Solution.** New `Vendor` entity + master register. `ProcurementPO` gets a nullable `vendor_id` FK while `vendor_name` is kept as a denormalized snapshot. Existing rows backfill best-effort by fuzzy match (manual confirm). New POs use a typeahead picker; create-vendor inline flow allowed.

**In scope (MVP):**
- `procurement_vendors` table (id, legal_name, gst, pan, country, contact).
- `procurement_vendor_performance` rolling-30/90/365-day stats (on-time %, NCR count, avg slip days).
- Inline create from PO form.

**Out of scope:**
- Vendor onboarding workflow.
- Blacklist mechanics.

---

## 2. User Stories

| ID | As a … | I want … | So that … |
|---|---|---|---|
| US-1 | Materials Engineer | pick a registered vendor from a typeahead | I don't typo the name |
| US-2 | Procurement Manager | see lifetime on-time % per vendor | I award fairly |
| US-3 | Auditor | one canonical vendor row referenced by N POs | the books reconcile |

---

## 3. Architecture Diagram

```
PO create form → typeahead → /procurement/vendors?q=
                            ◄ list
PO POST → vendor_id (FK)
Nightly job → recompute procurement_vendor_performance per vendor
Dashboard vendor scorecard → reads performance table
```

---

## 4. Backend Plan

### 4.1 ORM Models
```python
class ProcurementVendor(Base):
    __tablename__ = "procurement_vendors"
    id: UUID PK
    legal_name: str(300) UNIQUE
    short_code: str(50) UNIQUE  # e.g. "SLZGT"
    gst: str(50) | None
    pan: str(50) | None
    country: str(50)
    contact_email: str(200) | None
    contact_phone: str(50) | None
    is_active: bool
    created_at, updated_at

class ProcurementVendorPerformance(Base):
    __tablename__ = "procurement_vendor_performance"
    id: UUID PK
    vendor_id: UUID FK
    window_days: int   # 30 | 90 | 365
    po_count: int
    on_time_pct: Numeric(5,2)
    avg_slip_days: Numeric(5,2)
    ncr_count: int
    computed_at: timestamptz
```

Add to `ProcurementPO`:
```python
vendor_id: Mapped[UUID | None] = mapped_column(ForeignKey("procurement_vendors.id"), index=True)
# vendor_name kept as denormalized snapshot
```

### 4.2 Sub-Module Layout
```
app/modules/procurement_module/vendor_sub_module/
├── dtos/{request_dtos,response_dtos}.py
├── services/
│   ├── vendor_service.py
│   └── performance_service.py
├── repositories/vendor_repository.py
└── routers/vendor_router.py
```

### 4.3 DTOs
`VendorCreateDTO`, `VendorUpdateDTO`, `VendorResponseDTO`, `VendorPerformanceDTO`.

### 4.4 API Endpoints
| Method | Path | Notes |
|---|---|---|
| POST | `/procurement/vendors` | create |
| GET | `/procurement/vendors?q=` | list / search |
| GET | `/procurement/vendors/{id}` | detail with performance windows |
| PATCH | `/procurement/vendors/{id}` | update |
| POST | `/procurement/vendors/{id}/recompute-performance` | force refresh |

### 4.5 Service Methods
| Method | Signature | Notes |
|---|---|---|
| `search` | `(q, limit=20)` | ILIKE on legal_name + short_code |
| `recompute_performance` | `(vendor_id)` | runs 3 windows |

### 4.6 Repository Methods
| Method | Notes |
|---|---|
| `find_by_short_code` | unique |
| `upsert_performance(vendor_id, window, metrics)` | unique on (vendor_id, window_days) |

### 4.7 Alembic Migration
```python
def upgrade():
    op.create_table("procurement_vendors", ...)
    op.create_table("procurement_vendor_performance", ...)
    op.add_column("procurement_pos", sa.Column("vendor_id", postgresql.UUID))
    op.create_foreign_key(None, "procurement_pos", "procurement_vendors", ["vendor_id"], ["id"])
def downgrade(): ...
```

### 4.8 `main.py` Wiring
```python
from app.modules.procurement_module.vendor_sub_module.routers.vendor_router import router as vendor_router
app.include_router(vendor_router, prefix="/api/v1")
```

---

## 5. Frontend Plan

### 5.1 API Client
Add: `searchVendors`, `createVendor`, `getVendor`, `updateVendor`, `recomputeVendorPerformance`.

### 5.2 Wireframes
```
┌─ PO Create — Vendor ─────────────────────────────────┐
│ Vendor [Salzgi________] ▼                            │
│  • Salzgitter Rail Logistics (SLZGT)  On-time 87% ★  │
│  • Salzgitter Mannesmann GmbH         (no history)   │
│  + Add new vendor                                    │
└──────────────────────────────────────────────────────┘
```

### 5.3 New Components
| File | Role |
|---|---|
| `VendorPicker.jsx` | typeahead |
| `VendorScorecard.jsx` | dashboard widget |

### 5.4 Integration Points
`POTab.jsx` — replace plain text vendor field with `VendorPicker`. Dashboard — optional `VendorScorecard` for top-N.

---

## 6. End-to-End Sequence
```
ME types → searchVendors → list
ME picks SLZGT → PO POST { vendor_id: ... }
Nightly cron → performance_service.recompute_for_all()
Dashboard → reads performance rows
```

---

## 7. Edge Cases & Error Handling

| Case | Behavior |
|---|---|
| Vendor not found | inline create flow |
| Vendor inactive | hide from picker; existing PO references read-only |
| Recompute with zero POs | writes 0% on-time, 0 slips |

---

## 8. Verification / Acceptance Criteria

1. Migration adds tables + FK.
2. Search returns ILIKE matches.
3. Create PO with `vendor_id` persists; legacy POs without vendor_id still readable.
4. Recompute populates 3 window rows.

---

## 9. File Touch List

**New files:**
```
backend/app/modules/procurement_module/vendor_sub_module/
├── __init__.py
├── dtos/{__init__,request_dtos,response_dtos}.py
├── services/{__init__,vendor_service,performance_service}.py
├── repositories/{__init__,vendor_repository}.py
└── routers/{__init__,vendor_router}.py

backend/alembic/versions/007_create_vendors.py
frontend/src/components/procurement/VendorPicker.jsx
frontend/src/components/procurement/VendorScorecard.jsx
```

**Modified files:**
| File | Change |
|---|---|
| `backend/app/models_v2/procurement.py` | + 2 classes + col on PO |
| `backend/app/main.py` | mount router |
| `frontend/src/apis/procurementApi.js` | + 5 helpers |
| `frontend/src/components/procurement/POTab.jsx` | use `VendorPicker` |
| `frontend/src/components/procurement/ProcurementDashboard.jsx` | optional scorecard widget |
