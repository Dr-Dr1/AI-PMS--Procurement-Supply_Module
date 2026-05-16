# Feature Build Guide: Procurement Agent (A09) — Reorder, Slip Forecast, Vendor Scoring

---

## Working Branch — `feat/procurement-agent-ai`

```bash
git checkout main
git pull origin main
git checkout -b feat/procurement-agent-ai
```

---

> **Status:** Planned
> **Branch:** `feat/procurement-agent-ai` (branch from `main`)
> **Target sub-module:** `agent_sub_module/` (extend after `MATERIAL_RISK_AI.md` merges) — adds tool-using ReAct loop
> **SRS refs:** FR-M08-003, FR-M08-004, NFR-34 (explainability), NFR-35 (HITL invariant)

---

## 1. Feature Summary

**Problem.** `MATERIAL_RISK_AI.md` adds a single-shot scorer. A09 in SRS is a broader Tier-2 agent that should *converse*: "Which packages have at-risk OHE materials right now?" "Should I reorder cantilever masts given current lead time?" "Forecast cash-out vs PO schedule for July." Today there's no conversational entry-point.

**Solution.** Build a ReAct-style agent on Claude Sonnet 4.6 with thin function-call tools over the existing endpoints. State persists in `procurement_agent_sessions`. Every response carries `citations` referencing source rows (NFR-34); state-changing tool calls require explicit user confirm (NFR-35).

**In scope (MVP):**
- Chat endpoint with session memory.
- 6 tools (read-only): `find_pos`, `list_overdue`, `vendor_scorecard`, `risk_summary`, `cash_out_forecast`, `cp_alerts`.
- 1 state-changing tool: `propose_reorder` (writes to a draft suggestions table; never auto-creates PO).
- System prompt enforces evidence citation + HITL confirmations.

**Out of scope:**
- Multi-agent supervisor (handoff to Schedule / Cost agents).
- Voice input.

---

## 2. User Stories

| ID | As a … | I want … | So that … |
|---|---|---|---|
| US-1 | Procurement Manager | ask "what is at risk this week" in plain English | I don't click 8 filters |
| US-2 | Anyone | every numeric answer cite its source rows | I trust the answer (NFR-34) |
| US-3 | PM | confirm before any state-changing action | NFR-35 |

---

## 3. Architecture Diagram

```
┌──────────────────────────────────────────────────────┐
│ Frontend: AgentChatPanel (ProcurementDashboard)      │
└──────────────────┬───────────────────────────────────┘
                   │ axios
┌──────────────────▼───────────────────────────────────┐
│ /procurement/agent/chat                              │
│   agent_service.chat(session, msg)                   │
│   ├─ load system prompt + tools schema               │
│   ├─ Claude Sonnet 4.6 tool_use loop                 │
│   │   ├─ find_pos / list_overdue / …                 │
│   │   └─ propose_reorder (needs HITL confirm)        │
│   └─ assemble reply + citations[]                    │
│                                                      │
│   repositories/agent_sessions_repo.py                │
└──────────────────┬───────────────────────────────────┘
                   ▼
       PostgreSQL (sessions + suggestions)
       Anthropic API (Claude)
```

---

## 4. Backend Plan

### 4.1 ORM Models
```python
class ProcurementAgentSession(Base):
    __tablename__ = "procurement_agent_sessions"
    id: UUID PK
    session_key: str(100) UNIQUE
    actor: str(200)
    messages: JSON   # [{role, content, ts}]
    created_at, updated_at

class ProcurementReorderSuggestion(Base):
    __tablename__ = "procurement_reorder_suggestions"
    id: UUID PK
    session_id: UUID FK
    material_link_id: UUID FK
    suggested_qty: Numeric
    suggested_lead_time_days: int
    reasoning: Text
    evidence_refs: JSON
    status: SAEnum(SuggestionStatus)  # PROPOSED | CONFIRMED | DISMISSED
    decided_by: str | None
    decided_at: timestamptz | None
    created_at
```

### 4.2 Sub-Module Layout
```
app/modules/procurement_module/agent_sub_module/
├── chat/
│   ├── agent_service.py
│   ├── system_prompt.py
│   └── tools/
│       ├── find_pos.py
│       ├── list_overdue.py
│       ├── vendor_scorecard.py
│       ├── risk_summary.py
│       ├── cash_out_forecast.py
│       ├── cp_alerts.py
│       └── propose_reorder.py
├── repositories/agent_sessions_repo.py
└── routers/chat_router.py
```

### 4.3 DTOs
- `ChatRequestDTO { session_key, message }`
- `ChatResponseDTO { reply, citations, suggestion_id?, tool_calls }`
- `SuggestionDecisionDTO { decision: SuggestionStatus }`

### 4.4 API Endpoints
| Method | Path | Notes |
|---|---|---|
| POST | `/procurement/agent/chat` | converse |
| DELETE | `/procurement/agent/sessions/{key}` | clear history |
| GET | `/procurement/agent/suggestions?status=PROPOSED` | inbox |
| POST | `/procurement/agent/suggestions/{id}/decision` | confirm/dismiss |

### 4.5 Service Methods
| Method | Signature | Notes |
|---|---|---|
| `chat(session_key, msg, actor)` | runs ReAct loop | up to 6 tool hops per turn |
| `confirm_suggestion(id, actor)` | promotes to draft PO | calls PO service |
| `dismiss_suggestion(id, actor)` | marks dismissed |

### 4.6 System Prompt Sketch
```
You are the AI-PMS Procurement assistant for a metro project.
- Only answer using results returned by the listed tools.
- Every numeric claim must cite the source row id (PO, GRN, MaterialLink, RiskFinding).
- For state-changing actions, propose them as a Suggestion and require user confirm.
- Format: TL;DR / Details / Evidence.
```

### 4.7 Alembic Migration
```python
def upgrade():
    op.execute("CREATE TYPE suggestion_status AS ENUM ('PROPOSED','CONFIRMED','DISMISSED')")
    op.create_table("procurement_agent_sessions", ...)
    op.create_table("procurement_reorder_suggestions", ...)
def downgrade(): ...
```

### 4.8 `main.py` Wiring
```python
from app.modules.procurement_module.agent_sub_module.routers.chat_router import router as chat_router
app.include_router(chat_router, prefix="/api/v1")
```

---

## 5. Frontend Plan

### 5.1 API Client
Add: `agentChat`, `clearAgentSession`, `listSuggestions`, `decideSuggestion`.

### 5.2 Wireframes
```
┌─ ProcurementDashboard — Agent panel ───────────────┐
│ You: which materials are at risk this week         │
│ ──────────────────────────────────────────────────  │
│ A09: 3 links AT_RISK (HIGH):                       │
│   • OHE cantilever masts  PO-OHE-241  78           │
│   • Track ballast         PO-TRK-019  74           │
│   • Signalling cabinets   PO-SIG-002  66           │
│ Citations: link-uuid-…, link-uuid-…, link-uuid-…   │
│ [Type message…]                                    │
└───────────────────────────────────────────────────┘
```

### 5.3 New Components
| File | Role |
|---|---|
| `AgentChatPanel.jsx` | conversation UI |
| `SuggestionsInbox.jsx` | proposed reorders |

### 5.4 Integration Points
Add to `ProcurementDashboard.jsx`.

---

## 6. End-to-End Sequence
```
User asks → /chat → Claude → tool_use(list_overdue) → tool_use(risk_summary)
                                → assistant reply with citations
User asks "reorder cantilever masts" → propose_reorder → Suggestion row PROPOSED
PM clicks Confirm → suggestion → CONFIRMED → POService creates DRAFT PO seeded from suggestion
```

---

## 7. Edge Cases & Error Handling

| Case | Behavior |
|---|---|
| Anthropic timeout | return 504; session unchanged |
| Tool exception | surfaced as "tool_error" in transcript; agent retries up to 2× |
| Confirm a suggestion whose link is deleted | 422 |

---

## 8. Verification / Acceptance Criteria

1. Migration creates 2 tables + 1 enum.
2. Chat returns answer with `citations` array.
3. State-changing turn produces a Suggestion row, not a PO.
4. Confirm creates a DRAFT PO; dismiss marks dismissed.

---

## 9. File Touch List

**New files:**
```
backend/app/modules/procurement_module/agent_sub_module/
├── chat/{__init__,agent_service,system_prompt}.py
├── chat/tools/{__init__,find_pos,list_overdue,vendor_scorecard,risk_summary,cash_out_forecast,cp_alerts,propose_reorder}.py
├── repositories/{__init__,agent_sessions_repo}.py
└── routers/{__init__,chat_router}.py

backend/alembic/versions/011_create_agent_sessions.py
frontend/src/components/procurement/AgentChatPanel.jsx
frontend/src/components/procurement/SuggestionsInbox.jsx
```

**Modified files:**
| File | Change |
|---|---|
| `backend/app/models_v2/procurement.py` | + 2 classes |
| `backend/app/core/enums.py` | + `SuggestionStatus` |
| `backend/app/main.py` | mount `chat_router` |
| `backend/requirements.txt` | + `anthropic` (if not already) |
| `frontend/src/apis/procurementApi.js` | + 4 helpers |
| `frontend/src/components/procurement/ProcurementDashboard.jsx` | mount Agent + Inbox |
