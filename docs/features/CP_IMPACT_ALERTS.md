# Feature Build Guide: CP-Impact Material Alert (FR-M08-004 Fan-Out)

---

## Working Branch — `feat/cp-impact-alerts`

```bash
git checkout main
git pull origin main
git checkout -b feat/cp-impact-alerts
```

---

> **Status:** Planned
> **Branch:** `feat/cp-impact-alerts` (branch from `main`)
> **Target sub-module:** new `alert_sub_module/`
> **SRS refs:** FR-M08-004 (Critical), NFR-04 (response time), NFR-22 (alerting)

---

## 1. Feature Summary

**Problem.** FR-M08-004: *"If a material required for a Critical Path activity shows delay_risk_score above threshold, the system shall raise a Tier 0 alert to the Project Manager, Planning Manager, and Procurement Manager simultaneously."* Today `is_critical_path` is captured on `ProcurementMaterialLink`, and `risk_score` is computed, but no notification fan-out exists. The alert is silent — a flag column with no consumer.

**Solution.** New `alert_sub_module/` that listens on score-write events (from the agent / rule engine) and writes a `procurement_cp_alerts` row + dispatches an in-app notification, email, and SMS to the three named roles, deduplicated on `(material_link_id, current_score_band)`.

**In scope (MVP):**
- `procurement_cp_alerts` table.
- Trigger from `RiskScoreService.score_link()` when `is_critical_path && score >= threshold`.
- Channels: in-app (DB), email (SMTP via env), SMS (placeholder — log only in dev).
- Threshold configurable per package via env `PROCUREMENT_CP_ALERT_THRESHOLD` (default 60).

**Out of scope:**
- Mobile push.
- Quiet-hours suppression.

---

## 2. User Stories

| ID | As a … | I want … | So that … |
|---|---|---|---|
| US-1 | Project Manager | a Tier-0 alert when a critical-path material is at risk | I can act same-day |
| US-2 | Procurement Manager | the alert to deduplicate per material until score band changes | I'm not spammed |

---

## 3. Architecture Diagram

```
RiskScoreService.score_link()
   │ (post-write hook)
   ▼
alert_service.evaluate(link, finding)
   │  if is_critical_path && score >= threshold
   │  && no existing OPEN alert in same band
   ▼
write row → procurement_cp_alerts (status=OPEN)
   ├─► in-app  (DB only; FE polls)
   ├─► email   (SMTP)
   └─► sms     (stub)
```

---

## 4. Backend Plan

### 4.1 ORM Models
```python
class ProcurementCPAlert(Base):
    __tablename__ = "procurement_cp_alerts"
    id: UUID PK
    material_link_id: UUID FK
    triggering_finding_id: UUID FK → procurement_risk_findings
    score_at_trigger: int
    band_at_trigger: SAEnum(RiskLevel)
    recipients: JSON   # ["pm@…", "planning@…", "proc@…"]
    channels_dispatched: JSON  # {"in_app": true, "email": true, "sms": false}
    status: SAEnum(CPAlertStatus)  # OPEN | ACK | RESOLVED
    acknowledged_by: str(200) | None
    acknowledged_at: timestamptz | None
    resolved_at: timestamptz | None
    created_at: timestamptz
```

New enum:
```python
class CPAlertStatus(str, Enum):
    OPEN = "OPEN"; ACK = "ACK"; RESOLVED = "RESOLVED"
```

### 4.2 Sub-Module Layout
```
app/modules/procurement_module/alert_sub_module/
├── dtos/{request_dtos,response_dtos}.py
├── services/
│   ├── alert_service.py
│   └── channels/{email_channel,sms_channel,inapp_channel}.py
├── repositories/alert_repository.py
└── routers/alert_router.py
```

### 4.3 DTOs
- `CPAlertResponseDTO`
- `AcknowledgeDTO { comment }`

### 4.4 API Endpoints
| Method | Path | Notes |
|---|---|---|
| GET | `/procurement/alerts/cp` | list OPEN/ACK alerts |
| POST | `/procurement/alerts/cp/{id}/ack` | acknowledge |
| POST | `/procurement/alerts/cp/{id}/resolve` | resolve |

### 4.5 Service Methods
| Method | Signature | Notes |
|---|---|---|
| `evaluate(link, finding)` | called from RiskScoreService | dedup logic + dispatch |
| `dispatch(alert)` | fans to channels | logs every send |
| `acknowledge(id, actor)` | OPEN → ACK |

### 4.6 Repository Methods
| Method | Notes |
|---|---|
| `find_open_for_link(link_id)` | dedup support |
| `list(package_id, status)` | paginated |

### 4.7 Alembic Migration
```python
def upgrade():
    op.execute("CREATE TYPE cp_alert_status AS ENUM ('OPEN','ACK','RESOLVED')")
    op.create_table("procurement_cp_alerts", ...)
def downgrade():
    op.drop_table("procurement_cp_alerts")
    op.execute("DROP TYPE cp_alert_status")
```

### 4.8 `main.py` Wiring
```python
from app.modules.procurement_module.alert_sub_module.routers.alert_router import router as alert_router
app.include_router(alert_router, prefix="/api/v1")
```

Add env vars: `PROCUREMENT_CP_ALERT_THRESHOLD`, `SMTP_HOST`, `SMTP_USER`, `SMTP_PASS`, `ALERT_RECIPIENTS_PM`, `ALERT_RECIPIENTS_PLAN`, `ALERT_RECIPIENTS_PROC`.

---

## 5. Frontend Plan

### 5.1 API Client
Add: `listCPAlerts`, `ackCPAlert`, `resolveCPAlert`.

### 5.2 Wireframes
```
┌─ ProcurementDashboard — CP Alerts panel ──────────────┐
│ 🔴 OHE cantilever masts · A1147 · HIGH (78)           │
│    Score band CRITICAL since 2026-05-14 11:04         │
│    [Acknowledge]  [Resolve]                           │
└───────────────────────────────────────────────────────┘
```

### 5.3 New Components
| File | Role |
|---|---|
| `CPAlertsPanel.jsx` | dashboard card |

### 5.4 Integration Points
`ProcurementDashboard.jsx` — add `<CPAlertsPanel />` above existing KPI cards.

---

## 6. End-to-End Sequence
```
score_link writes finding
  → alert_service.evaluate
  → INSERT procurement_cp_alerts (OPEN)
  → dispatch to channels
PM opens dashboard → CPAlertsPanel polls every 30 s
PM clicks Acknowledge → status=ACK
Once score drops below threshold → alert_service.resolve() called by next score refresh
```

---

## 7. Edge Cases & Error Handling

| Case | Behavior |
|---|---|
| SMTP down | log warning; in-app still recorded |
| Same link, same band, prior OPEN | suppress dispatch |
| Risk recomputed lower band | auto-resolve OPEN |
| Finding dismissed in HITL | suppress |

---

## 8. Verification / Acceptance Criteria

1. Migration creates table + enum.
2. With threshold=60, scoring a critical-path link to 78 fires an alert; second score in same band does not duplicate.
3. Email channel logs to console in dev with full message body.
4. Acknowledge moves status to ACK; resolve sets `resolved_at`.

---

## 9. File Touch List

**New files:**
```
backend/app/modules/procurement_module/alert_sub_module/
├── __init__.py
├── dtos/{__init__,request_dtos,response_dtos}.py
├── services/
│   ├── __init__.py
│   ├── alert_service.py
│   └── channels/{__init__,email_channel,sms_channel,inapp_channel}.py
├── repositories/{__init__,alert_repository}.py
└── routers/{__init__,alert_router}.py

backend/alembic/versions/006_create_cp_alerts.py
frontend/src/components/procurement/CPAlertsPanel.jsx
```

**Modified files:**
| File | Change |
|---|---|
| `backend/app/models_v2/procurement.py` | + `ProcurementCPAlert` |
| `backend/app/core/enums.py` | + `CPAlertStatus` |
| `backend/app/main.py` | mount `alert_router` |
| `backend/app/modules/procurement_module/agent_sub_module/services/risk_score_service.py` | call `alert_service.evaluate` post-write |
| `frontend/src/apis/procurementApi.js` | + 3 helpers |
| `frontend/src/components/procurement/ProcurementDashboard.jsx` | mount panel |
