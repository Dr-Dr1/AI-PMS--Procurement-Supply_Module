# Feature Build Guide: <FEATURE NAME>

---

## Working Branch — `feat/<feature-name>`

**All implementation work for this feature MUST be done on branch `feat/<feature-name>`.**
Branch from `main`. PR back to `main`. Do not commit this feature's code on `main` directly, and do not combine it with unrelated work on the same branch.

```bash
git checkout main
git pull origin main
git checkout -b feat/<feature-name>
# follow §9 File Touch List below, commit incrementally
```

---

> **Status:** Planned
> **Branch:** `feat/<feature-name>` (branch from `main`)
> **Target sub-module:** <existing sub-module folder under `app/modules/procurement_module/`, or "new">
> **Companion docs:** [`../MODULE_STATUS.md`](../MODULE_STATUS.md)

---

## 1. Feature Summary

**Problem.** <one paragraph stating the user pain or the missing capability — quote SRS FR/NFR ID where possible>

**Solution.** <one paragraph describing the proposed approach>

**In scope (MVP):**
- <bullet>
- <bullet>

**Out of scope:**
- <bullet>

---

## 2. User Stories

| ID | As a … | I want to … | So that … |
|---|---|---|---|
| US-1 | | | |
| US-2 | | | |

---

## 3. Architecture Diagram

```
<ASCII diagram showing layers: frontend component → axios → backend route → service → repo → DB / external service>
```

---

## 4. Backend Plan

### 4.1 ORM Models
<new columns or tables; show class skeleton in code block>

### 4.2 Sub-Module Layout
<routers / services / repositories / dtos folder tree>

### 4.3 DTOs
<request_dtos.py and response_dtos.py snippets>

### 4.4 API Endpoints
| Method | Path | Notes |
|---|---|---|
| | | |

Include request/response example JSON for every endpoint.

### 4.5 Service Methods
| Method | Signature | Notes |
|---|---|---|

### 4.6 Repository Methods
| Method | Notes |
|---|---|

### 4.7 Alembic Migration
```python
def upgrade(): ...
def downgrade(): ...
```

### 4.8 `main.py` Wiring
```python
from app.modules.procurement_module.<sub_module>.routers.<router> import router as <name>_router
app.include_router(<name>_router, prefix="/api/v1")
```

---

## 5. Frontend Plan

### 5.1 API Client (`frontend/src/apis/procurementApi.js`)
<axios helpers>

### 5.2 Wireframes
```
<ASCII wireframes per screen>
```

### 5.3 New Components
| File | Role |
|---|---|

### 5.4 Integration Points
<which existing tab/component is modified, with code snippet>

### 5.5 Styling
<reuse existing claymorphism modal shells, badges, etc.>

---

## 6. End-to-End Sequence

```
User    Frontend    Backend    DB / external
 │ ───────► │ ─────────► │ ────────────► │
```

---

## 7. Edge Cases & Error Handling

| Case | Behavior |
|---|---|
| | |

---

## 8. Verification / Acceptance Criteria

**Backend:**
1. `alembic upgrade head` succeeds.
2. Swagger UI shows new endpoints.
3. `curl` flow works end-to-end.

**Frontend:**
4. <UI flow validated in browser>
5. <visual parity with existing tabs>

---

## 9. File Touch List

**New files:**
```
backend/app/modules/procurement_module/<sub_module>/
├── __init__.py
├── dtos/
│   ├── __init__.py
│   ├── request_dtos.py
│   └── response_dtos.py
├── repositories/
│   ├── __init__.py
│   └── <name>_repository.py
├── services/
│   ├── __init__.py
│   └── <name>_service.py
└── routers/
    ├── __init__.py
    └── <name>_router.py

backend/alembic/versions/<rev>_<slug>.py

frontend/src/components/procurement/<NewComponent>.jsx
```

**Modified files:**
| File | Change |
|---|---|
| `backend/app/models_v2/procurement.py` | |
| `backend/app/main.py` | |
| `frontend/src/apis/procurementApi.js` | |
| `frontend/src/pages/procurement.jsx` | |
