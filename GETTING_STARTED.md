# Intern D — Procurement-Supply Module Task Sheet
**Module:** `D:\AI-PMS--Procurement-Supply_Module`  
**Duration:** 1–2 months | **Port:** 8003 | **DB:** `aipms_dmrc` (shared with Quality + Documentation)

---

## Your Module in One Paragraph

Procurement tracks the movement of materials onto a construction site. The lifecycle is: **Purchase Order (PO)** raised for a vendor → vendor acknowledges → vendor dispatches → **Goods Receipt Note (GRN)** issued when materials arrive on site. **Material Links** map materials to specific construction activities and calculate supply **risk level** (LOW/MEDIUM/HIGH) based on whether enough material is available vs. what the activity schedule needs. The module has an MVP already built — your job is to harden it: add audit trails, pagination, soft-delete, and a richer dashboard.

---

## Phase 1 — Read & Understand (Week 1–2)
> Goal: Build mental model. No code yet.

### Reading List (in order)

1. `D:\AI-PMS--Procurement-Supply_Module\README.md`  
   → **Start here.** Full module overview, stack, start commands, seed instructions

2. **Key architecture rules to memorize (from README):**
   - Model import order (FK safety): `contract_schedule → schedule → structure → baseline → quality → procurement`
   - GRNs are immutable — no edit/delete endpoints, creation only
   - `activity_id` in MaterialLink stores P6 activity ID string (e.g. `"A1001"`), NOT a UUID
   - `echo=True` in `database.py` — SQLAlchemy prints all SQL to terminal (useful for debugging)

3. **PO state machine** — find it in code:
   `backend/app/modules/procurement_module/po_sub_module/service.py`  
   → Map out: DRAFT → ISSUED → ACKNOWLEDGED → DISPATCHED → CLOSED (what triggers each?)

4. **MaterialLink risk calculation** — find it in:
   `backend/app/modules/procurement_module/material_link_sub_module/service.py`  
   → How is risk_level (LOW/MEDIUM/HIGH) calculated?

5. `backend/app/models_v2/procurement.py` — read all 4 ORM models
6. `backend/app/routers/schedule_read_router.py` — understand how this module reads shared CDM tables (projects, corridors, packages, activities)

### Critical FK Import Order (from CLAUDE.md)
```
contract_schedule → schedule → structure → baseline → quality → procurement
```
This is the order models must be imported. Breaking it causes FK errors at startup.

### Week 1 Deliverable
Write a 1-page summary answering:
- What are the 5 PO states and what triggers each transition?
- How does MaterialLink risk calculation work (what inputs → what output)?
- What makes GRNs immutable (why can't they be edited after creation)?
- What shared CDM tables does this module read from?

**Submit to your mentor by end of Day 5.**

---

## Phase 2 — Run & Explore (Week 2)
> Goal: Run the system with real seed data, test it, read the code.

### Setup Steps
```bash
cd D:\AI-PMS--Procurement-Supply_Module
docker-compose up
python seed.py   # loads: 1 project, 2 corridors, 4 packages, 8 activities, 6 POs, 12 line items, 3 GRNs
# Swagger UI: http://localhost:8003/docs
```

### Exploration Tasks (do in order)

**E1 — Full PO lifecycle via Postman:**
1. `GET /api/v1/procurement/schedule/packages` — list packages from seed data
2. `POST /api/v1/procurement/pos` — create a new PO (pick a `package_id` from step 1)
3. Transition the PO through all 5 states (find the status endpoint in Swagger)
4. `POST /api/v1/procurement/grns` — create GRN linked to that PO
5. `GET /api/v1/procurement/dashboard` — view KPI cards

**E2 — Material link risk refresh:**
1. `POST /api/v1/procurement/material-links` — create a material link
2. `POST /api/v1/procurement/material-links/bulk-refresh` — refresh risk calculations
3. Observe how risk_level changes

**E3 — Code trace (PO state transition):**
```
po_sub_module/router.py     → find the status transition endpoint
po_sub_module/service.py    → find the transition method (state machine logic)
po_sub_module/repository.py → find the DB update
models_v2/procurement.py    → ProcurementPO model fields
```
Answer: What HTTP status code is returned when you try to transition a PO to CLOSED from DRAFT (invalid transition)?

---

## Phase 3 — Starter Dev Tasks (Week 3–4)
> Goal: Small, bounded changes. Get comfortable with the pattern.

---

### Task D3-1: Pagination on PO List and GRN List

**What to build:**  
`GET /api/v1/procurement/pos` and `GET /api/v1/procurement/grns` return all records. Add pagination.

**Acceptance criteria (same for both):**
- Accept `?page=1&page_size=20` query params
- Default: `page=1`, `page_size=20`, max `page_size=100`
- Response shape:
```json
{
  "items": [...],
  "total": 45,
  "page": 1,
  "page_size": 20,
  "pages": 3
}
```
- Filters still work alongside pagination (e.g., `?package_id=pkg_001&page=2`)

**Files to modify:**
```
po_sub_module/router.py      → add query params
po_sub_module/service.py     → pass to repository
po_sub_module/repository.py  → add .offset().limit() + count query
```

---

### Task D3-2: Soft-Delete on ProcurementPO

**Files:**
- `backend/app/models_v2/procurement.py` → `ProcurementPO` model
- `po_sub_module/` → router + service + repository

**What to build:**  
Replace hard-delete on POs with soft-delete. Only DRAFT POs can be deleted.

**Acceptance criteria:**
- Add two columns to `ProcurementPO`:
  ```python
  is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
  deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
  ```
- Write Alembic migration
- `DELETE /api/v1/procurement/pos/{id}`:
  - If status is not DRAFT → return 400: `"Only DRAFT POs can be deleted"`
  - If status is DRAFT → set `is_deleted=True`, `deleted_at=now()`
- All PO list endpoints add `WHERE is_deleted = false`
- GRNs referencing a soft-deleted PO are still accessible (don't cascade delete)

**Run migration:**
```bash
cd backend
alembic revision --autogenerate -m "add_soft_delete_to_procurement_po"
alembic upgrade head
```

---

## Phase 4 — Feature Dev Tasks (Week 5–8)
> Goal: Build real features that harden the existing MVP.

---

### Task D4-1: Audit Trail Wiring

**Reference implementation:** `D:\the-energy-lab-projects\AI-PMS--prototype\backend\app\services\audit.py`

**What to build:**  
Every state change in this module creates an `AuditEvent` record.

**Events to capture:**

| Entity | Action | When |
|--------|--------|------|
| `ProcurementPO` | `STATE_CHANGE` | Every status transition (DRAFT→ISSUED, etc.) |
| `ProcurementPO` | `SOFT_DELETE` | When PO is soft-deleted |
| `GRN` | `CREATED` | When GRN is created (GRNs are immutable — creation is the only event) |
| `MaterialLink` | `RISK_REFRESHED` | After bulk risk refresh |

**AuditEvent payload structure:**
```json
{
  "entity_type": "ProcurementPO",
  "entity_id": "po_abc123",
  "action": "STATE_CHANGE",
  "from_state": "DRAFT",
  "to_state": "ISSUED",
  "actor_id": "user_001",
  "timestamp": "2026-05-26T10:30:00Z",
  "metadata": {}
}
```

**Implementation steps:**
1. Read the prototype's `audit.py` — understand `AuditEvent` ORM model and `create_audit_event()` helper
2. Import or replicate that function in this module
3. Call it from the **service layer** (not router, not repository) after every state change
4. Add read endpoint: `GET /api/v1/procurement/audit?entity_id=&entity_type=`

**Hard rule:** `AuditEvent` rows are NEVER soft-deleted or modified.

---

### Task D4-2: Enhanced PO Dashboard Endpoint

**Current:** `GET /api/v1/procurement/dashboard` returns basic KPI cards.  
**Goal:** Add a richer summary endpoint.

**New endpoint:** `GET /api/v1/procurement/dashboard/summary?package_id={id}`

**Response shape:**
```json
{
  "package_id": "pkg_001",
  "as_of_date": "2026-05-26",
  "po_counts_by_status": {
    "DRAFT": 2,
    "ISSUED": 5,
    "ACKNOWLEDGED": 3,
    "DISPATCHED": 1,
    "CLOSED": 8
  },
  "total_po_value": 12500000.00,
  "total_grn_value": 8750000.00,
  "outstanding_value": 3750000.00,
  "overdue_pos": [
    {
      "po_id": "po_xyz",
      "po_number": "PO-2026-005",
      "status": "DISPATCHED",
      "dispatched_at": "2026-04-01T00:00:00Z",
      "days_overdue": 55
    }
  ],
  "material_risk_distribution": {
    "LOW": 12,
    "MEDIUM": 4,
    "HIGH": 2
  }
}
```

**Business rules:**
- `overdue_pos`: POs in DISPATCHED status for more than 30 days without moving to CLOSED
- `outstanding_value`: `total_po_value` minus `total_grn_value`
- Only non-deleted POs are included in all counts
- Return 404 if `package_id` not found

---

## Architecture Rules (Must Follow)

| Rule | What it means |
|------|---------------|
| No raw SQL in routers | All DB access through repository layer |
| FK import order | MUST follow: `contract_schedule → schedule → structure → baseline → quality → procurement` |
| SQLAlchemy 2.0 typed | Use `Mapped[...]` and `mapped_column(...)` |
| Pydantic v2 | Use `model_config = ConfigDict(from_attributes=True)` |
| Soft-delete only | Never hard-delete POs |
| GRNs are immutable | No PATCH/PUT on GRN — creation only |
| Audit every state change | Call `create_audit_event()` after every PO transition |
| Shared DB read-only | Other modules' tables in `aipms_dmrc` — read only, never write |

---

## Review Checkpoints

| Date | What you demo |
|------|---------------|
| End of Week 1 | 1-page module summary to mentor |
| End of Week 2 | Live Postman demo: full PO lifecycle + GRN creation with seed data |
| End of Week 4 | Code review: pagination + soft-delete PRs |
| End of Week 6 | Functional demo: audit events appearing on PO state transitions |
| End of Week 8 | Functional demo: enhanced dashboard with overdue POs |

---

## Questions to Ask Your Mentor

- Where is the `AIPMS_KT_Backend_Lokesh.pdf` file? Read it before writing any code.
- Which PostgreSQL host/port/password should I use for `aipms_dmrc`?
- Should I copy `audit.py` from the prototype, or import it as a shared library?
- Is there a `po_number` format convention (e.g., `PO-2026-001`)?
