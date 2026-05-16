# Feature Build Guide: Multi-Step PO Approval Chain

---

## Working Branch — `feat/po-approval-chain`

```bash
git checkout main
git pull origin main
git checkout -b feat/po-approval-chain
```

---

> **Status:** Planned
> **Branch:** `feat/po-approval-chain` (branch from `main`)
> **Target sub-module:** `po_sub_module/` (extend) + new `approval_sub_module/`
> **SRS refs:** FR-M08-001 (Critical), FR-M13-003 (Approval Chain Definition), NFR-16

---

## 1. Feature Summary

**Problem.** Today a `ProcurementPO` goes `DRAFT → ISSUED` on a single click by any Materials Engineer. There is no monetary-threshold approval, no reviewer/approver split, no audit of who recommended vs who finally approved. For POs above package-specific monetary ceilings the SRS (FR-M13-003) requires a configurable multi-step approval chain.

**Solution.** Introduce a `procurement_po_approvals` table (append-only, like `documentation_approvals`), an `ApprovalChain` config table keyed on `package_id + po_amount_band`, and four new endpoints (`submit`, `review`, `approve`, `reject`). POs above the configured threshold cannot move to `ISSUED` until the full chain signs off.

**In scope (MVP):**
- `ApprovalChain` config with up to 3 steps (Recommender → Reviewer → Approver).
- Monetary-band routing: ≤ ₹10 L self-approval, ₹10 L–₹1 Cr two-step, > ₹1 Cr three-step.
- Append-only approval trail.
- New frontend tab "Approvals" with pending-for-me queue.

**Out of scope:**
- Delegation / out-of-office routing.
- Parallel (multi-approver-at-same-level) approvals.

---

## 2. User Stories

| ID | As a … | I want … | So that … |
|---|---|---|---|
| US-1 | Materials Engineer | submit a DRAFT PO for approval | I don't issue beyond my limit |
| US-2 | Procurement Manager | see all POs pending my approval in one queue | I don't miss high-value approvals |
| US-3 | Auditor | replay every approval step with actor + timestamp + comment | I can attest the chain was followed |

---

## 3. Architecture Diagram

```
┌───────────────────────────────────────────────────────────────┐
│ Frontend                                                      │
│   POTab → Submit button (DRAFT only)                          │
│   New ApprovalsTab → my-queue + approve/reject panel          │
└──────────────────────┬────────────────────────────────────────┘
                       │ axios
┌──────────────────────▼────────────────────────────────────────┐
│ Backend  /api/v1/procurement/pos/...                          │
│   POST /pos/{id}/submit       → approval_service.submit()     │
│   POST /pos/{id}/review       → service.review()              │
│   POST /pos/{id}/approve      → service.approve() (final)     │
│   POST /pos/{id}/reject       → service.reject()              │
│   GET  /pos/{id}/approvals    → trail                         │
│   GET  /approvals/my-queue    → pending for current actor     │
│                                                               │
│   approval_sub_module/                                        │
│      service → repo → procurement_po_approvals               │
│                       + procurement_approval_chains          │
└──────────────────────┬────────────────────────────────────────┘
                       │
                       ▼
                  PostgreSQL
```

---

## 4. Backend Plan

### 4.1 ORM Models

```python
class ProcurementApprovalChain(Base):
    __tablename__ = "procurement_approval_chains"
    id: UUID PK
    package_id: UUID (indexed)
    amount_band_min: Numeric(15,2)
    amount_band_max: Numeric(15,2) | None  # NULL = no upper bound
    step_order: int  # 1..3
    role: str        # MATERIALS_ENGINEER | PROCUREMENT_MANAGER | PROJECT_MANAGER
    is_terminal: bool

class ProcurementPOApproval(Base):
    __tablename__ = "procurement_po_approvals"
    id: UUID PK
    po_id: UUID FK → procurement_pos (cascade)
    step_order: int
    action: SAEnum(POApprovalAction)  # SUBMITTED | REVIEWED | APPROVED | REJECTED
    actioned_by: str(200)
    comments: Text
    action_date: timestamptz default now()
```

Add to `ProcurementPO`:
- `current_approval_step: int | None` (NULL if no chain applies)
- `approval_chain_id: UUID | None`

New enum in `app/core/enums.py`:
```python
class POApprovalAction(str, Enum):
    SUBMITTED = "SUBMITTED"; REVIEWED = "REVIEWED"
    APPROVED = "APPROVED"; REJECTED = "REJECTED"
```

### 4.2 Sub-Module Layout
```
app/modules/procurement_module/approval_sub_module/
├── dtos/{request_dtos,response_dtos}.py
├── repositories/approval_repository.py
├── services/approval_service.py
└── routers/approval_router.py
```

### 4.3 DTOs
- `ApprovalActionDTO { comments: str }`
- `ApprovalTrailItemDTO { step_order, action, actioned_by, comments, action_date }`
- `MyQueueItemDTO { po_id, po_number, vendor_name, total_amount, current_step, role_required }`

### 4.4 API Endpoints

| Method | Path | Notes |
|---|---|---|
| POST | `/procurement/pos/{po_id}/submit` | DRAFT → pending step 1; computes chain from amount band |
| POST | `/procurement/pos/{po_id}/review` | step N (non-terminal) — advances to step N+1 |
| POST | `/procurement/pos/{po_id}/approve` | terminal step → POStatus.ISSUED |
| POST | `/procurement/pos/{po_id}/reject` | any step → POStatus.DRAFT, comments required |
| GET | `/procurement/pos/{po_id}/approvals` | full trail |
| GET | `/procurement/approvals/my-queue?role=...` | pending-for-me queue |

Example request `POST /procurement/pos/{id}/review`:
```json
{ "comments": "Lead time acceptable; vendor previously delivered on time." }
```

### 4.5 Service Methods
| Method | Signature | Notes |
|---|---|---|
| `submit` | `(po_id, actor) -> POResponseDTO` | Looks up chain by `package_id + total_amount`, writes step-1 SUBMITTED row |
| `review` / `approve` / `reject` | `(po_id, actor, dto)` | Validates `current_approval_step == expected step`; appends row; advances or terminates |
| `get_my_queue` | `(actor_role) -> list[MyQueueItemDTO]` | JOIN pos × chains × approvals |

### 4.6 Repository Methods
| Method | Notes |
|---|---|
| `find_chain_for(package_id, amount)` | row(s) ordered by step_order |
| `append_approval(po_id, step, action, actor, comments)` | append-only |
| `list_trail(po_id)` | ordered by `action_date` |

### 4.7 Alembic Migration
```python
def upgrade():
    op.create_table("procurement_approval_chains", ...)
    op.create_table("procurement_po_approvals", ...)
    op.add_column("procurement_pos", sa.Column("current_approval_step", sa.Integer))
    op.add_column("procurement_pos", sa.Column("approval_chain_id", postgresql.UUID))
def downgrade():
    op.drop_column("procurement_pos", "approval_chain_id")
    op.drop_column("procurement_pos", "current_approval_step")
    op.drop_table("procurement_po_approvals")
    op.drop_table("procurement_approval_chains")
```

### 4.8 `main.py` Wiring
```python
from app.modules.procurement_module.approval_sub_module.routers.approval_router import router as approval_router
app.include_router(approval_router, prefix="/api/v1")
```

---

## 5. Frontend Plan

### 5.1 API Client (`frontend/src/apis/procurementApi.js`)
Add: `submitPO`, `reviewPO`, `approvePO`, `rejectPO`, `listPOApprovals`, `getMyApprovalQueue`.

### 5.2 Wireframes
```
┌─ Approvals Tab ──────────────────────────────────────┐
│ Role: [Procurement Manager ▼]   Refresh             │
│ ──────────────────────────────────────────────────── │
│ PO-OHE-241 · ₹4,82,00,000 · Salzgitter   [Review]   │
│ PO-CIV-118 · ₹17,50,000   · UltraTech    [Review]   │
└──────────────────────────────────────────────────────┘
```

### 5.3 New Components
| File | Role |
|---|---|
| `ApprovalsTab.jsx` | Queue + action panel |
| `ApprovalTrailModal.jsx` | Trail viewer |

### 5.4 Integration Points
`POTab.jsx` — disable Issue button when chain applies; show **Submit** instead.

### 5.5 Styling
Reuse `ProcurementBadge` for action states; `ProcurementModal` for trail.

---

## 6. End-to-End Sequence
```
ME submits PO → step 1 row → status=SUBMITTED, current_step=1
PMgr reviews → step 2 row
PM approves → terminal → POStatus.ISSUED, current_step=NULL
```

---

## 7. Edge Cases & Error Handling

| Case | Behavior |
|---|---|
| PO below smallest band | Auto-issue on submit (no chain needed) |
| Reject at any step | Status returns to DRAFT, comments required |
| PO edited after submit | Block PATCH while `current_approval_step != NULL` |
| Chain config missing for package | 422 with explicit message |

---

## 8. Verification / Acceptance Criteria

**Backend:**
1. `alembic upgrade head` succeeds; 2 new tables present.
2. Create chain config; submit ₹50 L PO → goes to step 1; approve → ISSUED.
3. Reject without comments → 422.

**Frontend:**
4. ApprovalsTab shows pending POs for selected role.
5. Trail modal renders ordered actions.

---

## 9. File Touch List

**New files:**
```
backend/app/modules/procurement_module/approval_sub_module/
├── __init__.py
├── dtos/{__init__,request_dtos,response_dtos}.py
├── repositories/{__init__,approval_repository}.py
├── services/{__init__,approval_service}.py
└── routers/{__init__,approval_router}.py

backend/alembic/versions/003_create_procurement_approvals.py
frontend/src/components/procurement/ApprovalsTab.jsx
frontend/src/components/procurement/ApprovalTrailModal.jsx
```

**Modified files:**
| File | Change |
|---|---|
| `backend/app/models_v2/procurement.py` | add `current_approval_step`, `approval_chain_id` + 2 new classes |
| `backend/app/core/enums.py` | add `POApprovalAction` |
| `backend/app/main.py` | mount `approval_router` |
| `frontend/src/apis/procurementApi.js` | + 6 helpers |
| `frontend/src/pages/procurement.jsx` | add Approvals tab |
| `frontend/src/components/procurement/POTab.jsx` | swap Issue → Submit when chain applies |
