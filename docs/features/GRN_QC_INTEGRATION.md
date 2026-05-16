# Feature Build Guide: GRN ↔ Quality (ITP/RFI) Integration

---

## Working Branch — `feat/grn-qc-integration`

```bash
git checkout main
git pull origin main
git checkout -b feat/grn-qc-integration
```

---

> **Status:** Planned
> **Branch:** `feat/grn-qc-integration` (branch from `main`)
> **Target sub-module:** `goods_receipt_sub_module/` (extend)
> **SRS refs:** FR-M08-002, FR-M02-009 (ITP), FR-M02-001 (RFI), NFR-11

---

## 1. Feature Summary

**Problem.** GRN model already carries `test_certificate_ref: str(200)` — free text. QA engineers re-enter the same certificate number into the Quality module's ITP / RFI verification fields. Two systems, two truths; no traceable link.

**Solution.** Make `test_certificate_ref` resolve to a Quality `ITPCheckpoint` or `RFI` evidence record. On GRN create, optionally pass `linked_itp_id` / `linked_rfi_id`. The Quality module exposes a read endpoint to look up a test certificate; the Procurement module queries it. Bi-directional link is then established.

**In scope (MVP):**
- New optional FKs on `ProcurementGRN`: `linked_itp_id`, `linked_rfi_id` (soft refs — cross-module FK validation at service layer, not DB).
- `GET /procurement/grns/by-test-cert?ref=...` reverse lookup.
- Frontend GRN create form: type-ahead on test-cert ref hits Quality module `/quality/rfis?test_cert=...`.

**Out of scope:**
- Auto-create ITP checkpoint from GRN.
- Cross-database transactional integrity (single shared DB `aipms_dmrc` makes this pragmatic).

---

## 2. User Stories

| ID | As a … | I want … | So that … |
|---|---|---|---|
| US-1 | Storekeeper | type a test-cert ref and see if QA already verified it | I attach the right one |
| US-2 | QA Engineer | jump from an RFI to the source GRN | I see what arrived, when, in what qty |

---

## 3. Architecture Diagram

```
GRN create form ─► GET /quality/rfis?test_cert=TC-...  (Quality API)
                ◄─ list of RFIs with that cert
GRN saved with linked_rfi_id
GET /procurement/grns/by-test-cert ─► joins → GRN + RFI snapshot
```

---

## 4. Backend Plan

### 4.1 ORM Models
Add to `ProcurementGRN`:
```python
linked_itp_id: Mapped[UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True, index=True)
linked_rfi_id: Mapped[UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True, index=True)
```
No hard FK — Quality entities live in shared `aipms_dmrc` but module owns its own ORM; soft ref.

### 4.2 Sub-Module Layout
Extend `goods_receipt_sub_module/`. No new sub-module.

### 4.3 DTOs
- `GRNCreateDTO` — add `linked_itp_id: UUID | None`, `linked_rfi_id: UUID | None`.
- `GRNResponseDTO` — expose both.
- New `GRNByCertResponseDTO { grn: GRNResponseDTO, rfi_snapshot: dict | None }`.

### 4.4 API Endpoints
| Method | Path | Notes |
|---|---|---|
| GET | `/procurement/grns/by-test-cert?ref=...` | reverse lookup |

### 4.5 Service Methods
| Method | Signature | Notes |
|---|---|---|
| `find_by_test_cert` | `(ref: str)` | repository call + cross-module HTTP read of Quality RFI |
| `validate_linked_refs` | `(itp_id, rfi_id)` | optional cross-module check before insert |

### 4.6 Repository Methods
| Method | Notes |
|---|---|
| `get_by_test_cert(ref)` | `WHERE test_certificate_ref = :ref` |

### 4.7 Alembic Migration
```python
def upgrade():
    op.add_column("procurement_grns", sa.Column("linked_itp_id", postgresql.UUID))
    op.add_column("procurement_grns", sa.Column("linked_rfi_id", postgresql.UUID))
    op.create_index("ix_grns_linked_itp_id", "procurement_grns", ["linked_itp_id"])
    op.create_index("ix_grns_linked_rfi_id", "procurement_grns", ["linked_rfi_id"])
def downgrade():
    op.drop_index("ix_grns_linked_rfi_id")
    op.drop_index("ix_grns_linked_itp_id")
    op.drop_column("procurement_grns", "linked_rfi_id")
    op.drop_column("procurement_grns", "linked_itp_id")
```

### 4.8 `main.py` Wiring
No change.

---

## 5. Frontend Plan

### 5.1 API Client
Add: `getGRNByTestCert(ref)`, plus a thin call to Quality module's `/quality/rfis?test_cert=` (use `VITE_QUALITY_API_URL`).

### 5.2 Wireframes
```
┌─ GRN Create ────────────────────────────────────────┐
│ PO #PO-OHE-241                                       │
│ Received qty 40   Unit nos.                          │
│ Test cert ref [TC-SAL-2026-0941__________]           │
│   ↳ Match found: RFI-OHE-074 (Inspected ✓)  [Link]  │
└──────────────────────────────────────────────────────┘
```

### 5.3 New Components
| File | Role |
|---|---|
| `TestCertLookup.jsx` | Type-ahead inside GRN form |

### 5.4 Integration Points
`GRNTab.jsx` — inject TestCertLookup in create form.

---

## 6. End-to-End Sequence
```
User types cert ref → fetch /quality/rfis?test_cert=
Match → User picks; linked_rfi_id set
GRN POST includes linked_rfi_id
QA, later: GET /procurement/grns/by-test-cert?ref=TC-... → context
```

---

## 7. Edge Cases & Error Handling

| Case | Behavior |
|---|---|
| Quality module offline | Lookup degrades to plain text entry; warning shown |
| Cert exists on 2+ RFIs | List all; user picks |
| Linked RFI later deleted | GRN keeps the UUID; reverse-lookup returns 404 with stale-ref warning |

---

## 8. Verification / Acceptance Criteria

1. Migration adds two nullable UUID cols with indexes.
2. Create GRN with `linked_rfi_id` → persisted.
3. `GET /procurement/grns/by-test-cert?ref=TC-SAL-2026-0941` returns GRN + RFI snapshot.
4. Frontend type-ahead resolves real Quality RFI when both servers running.

---

## 9. File Touch List

**New files:**
```
frontend/src/components/procurement/TestCertLookup.jsx
backend/alembic/versions/004_grn_qc_link_columns.py
```

**Modified files:**
| File | Change |
|---|---|
| `backend/app/models_v2/procurement.py` | + 2 cols on `ProcurementGRN` |
| `backend/app/modules/procurement_module/goods_receipt_sub_module/dtos/request_dtos.py` | extend `GRNCreateDTO` |
| `backend/app/modules/procurement_module/goods_receipt_sub_module/dtos/response_dtos.py` | extend `GRNResponseDTO`, add `GRNByCertResponseDTO` |
| `backend/app/modules/procurement_module/goods_receipt_sub_module/services/service.py` | + `find_by_test_cert` |
| `backend/app/modules/procurement_module/goods_receipt_sub_module/repositories/repository.py` | + `get_by_test_cert` |
| `backend/app/modules/procurement_module/goods_receipt_sub_module/routers/grn_router.py` | + GET endpoint |
| `frontend/src/apis/procurementApi.js` | + `getGRNByTestCert`, Quality cross-call |
| `frontend/src/components/procurement/GRNTab.jsx` | wire `TestCertLookup` |
