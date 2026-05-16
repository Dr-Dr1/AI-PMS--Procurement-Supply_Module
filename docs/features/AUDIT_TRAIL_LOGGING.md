# Feature Build Guide: Immutable Audit Trail (NFR-16)

---

## Working Branch — `feat/audit-trail-logging`

```bash
git checkout main
git pull origin main
git checkout -b feat/audit-trail-logging
```

---

> **Status:** Planned
> **Branch:** `feat/audit-trail-logging` (branch from `main`)
> **Target sub-module:** new `audit_sub_module/`
> **SRS refs:** NFR-16 (immutable audit), FR-M08-001 (PO state transitions)

---

## 1. Feature Summary

**Problem.** Every PO state transition (DRAFT → ISSUED → ACKNOWLEDGED → DISPATCHED → CLOSED), every GRN create, every material-link update happens silently. NFR-16: *"All state transitions of critical entities shall be recorded in an append-only audit log."* Without this the auditor cannot reconstruct who did what when.

**Solution.** New `procurement_audit_events` table (append-only — no UPDATE, no DELETE). A small middleware / decorator captures every mutating service call and emits `{actor, action, entity_type, entity_id, old_value, new_value, source_ip, session_id, event_category, timestamp}` rows. Read-only audit viewer exposed for L1/L2.

**In scope (MVP):**
- Append-only table with check constraint forbidding update.
- Decorator `@audited(event_category)` on service-layer methods.
- Read API with filters: entity, actor, date range.

**Out of scope:**
- Cryptographic chain (Merkle / blockchain) — see Documentation module's BLOCKCHAIN_ATTESTATION.md pattern, not in M08 MVP.

---

## 2. User Stories

| ID | As a … | I want … | So that … |
|---|---|---|---|
| US-1 | Auditor | replay every state change of a PO | reconstruct the timeline |
| US-2 | L1 admin | filter by actor across all entities | investigate a person's actions |

---

## 3. Architecture Diagram

```
@audited decorator
   │
   ▼
ServiceMethod(old, new) → return value
   │
   ▼
AuditWriter.emit(actor, action, entity, old, new, category)
   │
   ▼
INSERT procurement_audit_events  (append-only)
   ◄── Read API: GET /procurement/audit?entity=PO&from=…
```

---

## 4. Backend Plan

### 4.1 ORM Models
```python
class ProcurementAuditEvent(Base):
    __tablename__ = "procurement_audit_events"
    id: UUID PK
    actor: str(200)
    action: str(50)         # e.g. "ISSUE", "ACKNOWLEDGE"
    entity_type: str(50)    # "PO", "GRN", "MATERIAL_LINK"
    entity_id: UUID
    old_value: JSON | None
    new_value: JSON | None
    event_category: SAEnum(AuditCategory)
    source_ip: str(50) | None
    session_id: str(100) | None
    created_at: timestamptz
    __table_args__ = (
        Index("ix_audit_entity", "entity_type", "entity_id"),
        Index("ix_audit_actor_at", "actor", "created_at"),
    )
```

New enum:
```python
class AuditCategory(str, Enum):
    DATA_CHANGE = "DATA_CHANGE"
    WORKFLOW_TRANSITION = "WORKFLOW_TRANSITION"
    AI_ACTION = "AI_ACTION"
    CONFIG_CHANGE = "CONFIG_CHANGE"
```

DB-level guard:
```sql
CREATE OR REPLACE FUNCTION forbid_audit_update() RETURNS trigger AS $$ BEGIN
  RAISE EXCEPTION 'procurement_audit_events is append-only'; END $$ LANGUAGE plpgsql;
CREATE TRIGGER no_update BEFORE UPDATE OR DELETE ON procurement_audit_events
  FOR EACH ROW EXECUTE FUNCTION forbid_audit_update();
```

### 4.2 Sub-Module Layout
```
app/modules/procurement_module/audit_sub_module/
├── dtos/response_dtos.py
├── services/audit_service.py
├── repositories/audit_repository.py
├── routers/audit_router.py
└── decorator.py   # @audited
```

### 4.3 DTOs
`AuditEventResponseDTO`.

### 4.4 API Endpoints
| Method | Path | Notes |
|---|---|---|
| GET | `/procurement/audit?entity_type&entity_id&actor&from&to` | paginated |

### 4.5 Service Methods
| Method | Signature | Notes |
|---|---|---|
| `emit(event)` | service-side append | no business logic |
| `list(filters)` | read API |

### 4.6 Repository Methods
| Method | Notes |
|---|---|
| `insert(event)` | bare insert |
| `query(filters, page)` | filters above |

### 4.7 Alembic Migration
```python
def upgrade():
    op.execute("CREATE TYPE audit_category AS ENUM ('DATA_CHANGE','WORKFLOW_TRANSITION','AI_ACTION','CONFIG_CHANGE')")
    op.create_table("procurement_audit_events", ...)
    op.execute("""CREATE OR REPLACE FUNCTION forbid_audit_update() ...""")
    op.execute("CREATE TRIGGER no_update BEFORE UPDATE OR DELETE ON procurement_audit_events ...")
def downgrade():
    op.execute("DROP TRIGGER no_update ON procurement_audit_events")
    op.execute("DROP FUNCTION forbid_audit_update")
    op.drop_table("procurement_audit_events")
    op.execute("DROP TYPE audit_category")
```

### 4.8 `main.py` Wiring
```python
from app.modules.procurement_module.audit_sub_module.routers.audit_router import router as audit_router
app.include_router(audit_router, prefix="/api/v1")
```

Decorate every mutating service method (`POService.issue`, `acknowledge`, …, `GRNService.create`, …).

---

## 5. Frontend Plan

### 5.1 API Client
Add: `listAuditEvents(filters)`.

### 5.2 Wireframes
```
┌─ Audit Viewer ────────────────────────────────────────────┐
│ Entity [PO ▼]  Actor [______]  From [____] To [____]      │
│ ────────────────────────────────────────────────────────── │
│ 11:04  Anita  ISSUE   PO-OHE-241   {status:DRAFT→ISSUED}  │
│ 11:38  Vivek  ACK     PO-OHE-241   {status:ISSUED→ACK}    │
└───────────────────────────────────────────────────────────┘
```

### 5.3 New Components
| File | Role |
|---|---|
| `AuditViewerPage.jsx` | full-page viewer |

### 5.4 Integration Points
Add route in `App.jsx` (admin-only); link from `ProcurementDashboard.jsx`.

---

## 6. End-to-End Sequence
```
PM calls /issue → @audited captures (old=DRAFT, new=ISSUED)
INSERT row with WORKFLOW_TRANSITION
Audit viewer fetches; renders timeline
DB trigger refuses UPDATE/DELETE
```

---

## 7. Edge Cases & Error Handling

| Case | Behavior |
|---|---|
| Service raises mid-transaction | audit row not written (same TX) |
| `old_value == new_value` | row still written; auditor can filter no-ops |
| Audit table grows large | partition by month (Phase 2) |

---

## 8. Verification / Acceptance Criteria

1. Issuing a PO writes 1 audit row.
2. `UPDATE procurement_audit_events SET …` raises exception.
3. Read API filters by actor + date.

---

## 9. File Touch List

**New files:**
```
backend/app/modules/procurement_module/audit_sub_module/
├── __init__.py
├── decorator.py
├── dtos/{__init__,response_dtos}.py
├── services/{__init__,audit_service}.py
├── repositories/{__init__,audit_repository}.py
└── routers/{__init__,audit_router}.py

backend/alembic/versions/009_create_audit.py
frontend/src/pages/AuditViewerPage.jsx
```

**Modified files:**
| File | Change |
|---|---|
| `backend/app/models_v2/procurement.py` | + `ProcurementAuditEvent` |
| `backend/app/core/enums.py` | + `AuditCategory` |
| `backend/app/main.py` | mount `audit_router` |
| All mutating service files (PO, GRN, MaterialLink) | apply `@audited` |
| `frontend/src/apis/procurementApi.js` | + `listAuditEvents` |
| `frontend/src/App.jsx` | route for AuditViewerPage |
