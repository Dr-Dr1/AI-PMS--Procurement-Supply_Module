# Feature Build Guide: Predictive Material Risk Score (Procurement Agent A09)

---

## Working Branch — `feat/material-risk-ai`

```bash
git checkout main
git pull origin main
git checkout -b feat/material-risk-ai
```

---

> **Status:** Planned
> **Branch:** `feat/material-risk-ai` (branch from `main`)
> **Target sub-module:** `material_link_sub_module/` (replace risk engine) + new `agent_sub_module/`
> **SRS refs:** FR-M08-003 (Critical), NFR-34 (explainability), NFR-35 (HITL)

---

## 1. Feature Summary

**Problem.** `ProcurementMaterialLink.risk_score` is currently computed by a rule-based heuristic: `(days_overdue * weight) + (po_status == OVERDUE ? 50 : 0)`. It misses signal from vendor delivery history, lead-time variance, and seasonal patterns. SRS FR-M08-003 names a Procurement Agent (A09) Tier-2 that "shall populate `delay_risk_score` based on PO status, expected_delivery vs required_on_site, and historical vendor performance."

**Solution.** Replace the heuristic with a model-driven `RiskScoreService`. Pluggable backend: v1 uses Claude Sonnet 4.6 via Anthropic SDK with structured tool-use over a curated feature vector; v2 swaps in a gradient-boosted model trained on historical GRN-vs-PO actuals. Every score writes a `procurement_risk_findings` row with the feature snapshot and an `evidence_refs` JSON (NFR-34). UI surfaces the score with an "Explain" drawer.

**In scope (MVP):**
- `procurement_risk_findings` table (one row per refresh per link).
- LLM-based scorer with caching keyed on `(po_id, vendor_name, days_to_committed)`.
- Explain endpoint returning the feature vector + reasoning.
- HITL accept/dismiss on score before downstream alerts fire (NFR-35).

**Out of scope:**
- Online retraining loop.
- Cross-project vendor performance federation.

---

## 2. User Stories

| ID | As a … | I want … | So that … |
|---|---|---|---|
| US-1 | Procurement Manager | a learned risk score per material link | rule-of-thumb misses long-lead items |
| US-2 | Anyone | see *why* a score is HIGH | I trust the score (NFR-34) |
| US-3 | PM | accept/dismiss each high-risk finding | nothing escalates without sign-off (NFR-35) |

---

## 3. Architecture Diagram

```
┌──────────────────────────────────────────────────────────┐
│ Frontend                                                 │
│   MaterialLinksTab → RiskExplainDrawer (NEW)             │
└──────────────────┬───────────────────────────────────────┘
                   │ axios
┌──────────────────▼───────────────────────────────────────┐
│ Backend  /api/v1/procurement/agent/...                   │
│   POST /score          — recompute one link              │
│   POST /score/bulk     — package-scoped refresh          │
│   GET  /findings       — paginated inbox                 │
│   POST /findings/{id}/decision  — accept/dismiss         │
│                                                          │
│   agent_sub_module/services/                             │
│      risk_score_service.py  → LLM client + cache         │
│      llm_client.py          → Anthropic SDK              │
│      explain_service.py     → returns reasoning JSON     │
│   agent_sub_module/repositories/                         │
│      risk_findings_repository.py                         │
└──────────────────┬───────────────────────────────────────┘
                   │
                   ▼
        PostgreSQL  +  Anthropic API (Claude Sonnet 4.6)
```

---

## 4. Backend Plan

### 4.1 ORM Models
```python
class ProcurementRiskFinding(Base):
    __tablename__ = "procurement_risk_findings"
    id: UUID PK
    material_link_id: UUID FK → procurement_material_links
    risk_score: int
    risk_level: SAEnum(RiskLevel)
    feature_vector: JSON  # snapshot at scoring time
    evidence_refs: JSON   # source: vendor history GRN ids, lead-time samples
    reasoning: Text       # LLM-rendered explanation
    human_decision: SAEnum(FindingDecision) | None   # ACCEPTED | DISMISSED | None
    decided_by: str(200) | None
    decided_at: timestamptz | None
    created_at: timestamptz
```

New enum:
```python
class FindingDecision(str, Enum):
    ACCEPTED = "ACCEPTED"; DISMISSED = "DISMISSED"
```

### 4.2 Sub-Module Layout
```
app/modules/procurement_module/agent_sub_module/
├── dtos/{request_dtos,response_dtos}.py
├── services/
│   ├── risk_score_service.py
│   ├── llm_client.py
│   └── explain_service.py
├── repositories/risk_findings_repository.py
└── routers/agent_router.py
```

### 4.3 DTOs
- `RiskScoreRequestDTO { material_link_id, force_refresh: bool = false }`
- `RiskScoreResponseDTO { score, level, evidence_refs, reasoning, finding_id }`
- `BulkScoreRequestDTO { package_id }`
- `FindingDecisionDTO { decision: FindingDecision, comment: str | None }`

### 4.4 API Endpoints
| Method | Path | Notes |
|---|---|---|
| POST | `/procurement/agent/score` | refresh one link |
| POST | `/procurement/agent/score/bulk` | package-scoped fan-out |
| GET | `/procurement/agent/findings?package_id&decision=` | inbox |
| POST | `/procurement/agent/findings/{id}/decision` | accept/dismiss |
| GET | `/procurement/agent/findings/{id}/explain` | feature + reasoning |

Example response `/score`:
```json
{
  "score": 78,
  "level": "HIGH",
  "evidence_refs": {
    "vendor_avg_lead_time_days": 62,
    "this_po_committed_lead_time_days": 48,
    "historical_slip_p75_days": 11,
    "grn_samples": ["uuid-...", "uuid-..."]
  },
  "reasoning": "Vendor Salzgitter has p75 slip of 11 days; committed lead time 48 d is 22% below historical median…",
  "finding_id": "uuid-..."
}
```

### 4.5 Service Methods
| Method | Signature | Notes |
|---|---|---|
| `score_link` | `(link_id, force=False) -> RiskScoreResponseDTO` | cache key `(po_id, days_to_committed)`; TTL 12 h |
| `bulk_score` | `(package_id) -> int` | async fan-out via FastAPI BackgroundTasks |
| `decide_finding` | `(finding_id, dto, actor)` | writes decision; suppresses CP-impact alert if DISMISSED |

### 4.6 Repository Methods
| Method | Notes |
|---|---|
| `insert_finding(...)` | append |
| `latest_for_link(link_id)` | most recent row |
| `list_inbox(package_id, decision)` | paginated |

### 4.7 Alembic Migration
```python
def upgrade():
    op.create_table("procurement_risk_findings", ...)
    op.execute("CREATE TYPE finding_decision_enum AS ENUM ('ACCEPTED','DISMISSED')")
def downgrade():
    op.drop_table("procurement_risk_findings")
    op.execute("DROP TYPE finding_decision_enum")
```

### 4.8 `main.py` Wiring
```python
from app.modules.procurement_module.agent_sub_module.routers.agent_router import router as agent_router
app.include_router(agent_router, prefix="/api/v1")
```

---

## 5. Frontend Plan

### 5.1 API Client
Add: `scoreMaterialLink`, `bulkScorePackage`, `listFindings`, `decideFinding`, `explainFinding`.

### 5.2 Wireframes
```
┌─ Material Link row ──────────────────────────────────┐
│ OHE cantilever masts · A1147 · HIGH (78)             │
│   [Explain]  [Accept]  [Dismiss]                     │
│ ──── Explain drawer ─────                            │
│ Vendor lead-time p75 = 62 d; committed = 48 d        │
│ Source GRNs: TC-SAL-2024-…, TC-SAL-2025-…            │
└──────────────────────────────────────────────────────┘
```

### 5.3 New Components
| File | Role |
|---|---|
| `RiskExplainDrawer.jsx` | reasoning + evidence |
| `FindingsInbox.jsx` | global inbox panel on ProcurementDashboard |

### 5.4 Integration Points
`MaterialLinksTab.jsx` — replace static badge with score from latest finding; `ProcurementDashboard.jsx` — add inbox card.

---

## 6. End-to-End Sequence
```
PM clicks bulk-refresh → /score/bulk
Backend loops links, calls LLM with feature vector
Each link → finding row inserted
UI inbox lists HIGH; PM clicks Explain → reasoning
PM Accepts → downstream CP-impact alert fires (see CP_IMPACT_ALERTS.md)
PM Dismisses → suppressed
```

---

## 7. Edge Cases & Error Handling

| Case | Behavior |
|---|---|
| LLM timeout | Fall back to rule-based score; mark `reasoning = "FALLBACK_HEURISTIC"` |
| Empty vendor history | Score range capped at MEDIUM; reasoning notes "cold-start" |
| Same link scored twice in <12 h | Return cached |

---

## 8. Verification / Acceptance Criteria

1. Migration creates table + enum.
2. POST `/score` for a link returns 200 with reasoning.
3. POST `/score/bulk` for a package writes N findings.
4. Explain drawer shows feature vector verbatim.
5. Dismissing a HIGH finding suppresses the CP-impact notification (verified against CP_IMPACT_ALERTS.md flow).

---

## 9. File Touch List

**New files:**
```
backend/app/modules/procurement_module/agent_sub_module/
├── __init__.py
├── dtos/{__init__,request_dtos,response_dtos}.py
├── services/{__init__,risk_score_service,llm_client,explain_service}.py
├── repositories/{__init__,risk_findings_repository}.py
└── routers/{__init__,agent_router}.py

backend/alembic/versions/005_create_risk_findings.py
frontend/src/components/procurement/RiskExplainDrawer.jsx
frontend/src/components/procurement/FindingsInbox.jsx
```

**Modified files:**
| File | Change |
|---|---|
| `backend/app/models_v2/procurement.py` | + `ProcurementRiskFinding` |
| `backend/app/core/enums.py` | + `FindingDecision` |
| `backend/app/main.py` | mount `agent_router` |
| `backend/requirements.txt` | + `anthropic` |
| `frontend/src/apis/procurementApi.js` | + 5 helpers |
| `frontend/src/components/procurement/MaterialLinksTab.jsx` | render score from finding |
| `frontend/src/components/procurement/ProcurementDashboard.jsx` | + FindingsInbox |
