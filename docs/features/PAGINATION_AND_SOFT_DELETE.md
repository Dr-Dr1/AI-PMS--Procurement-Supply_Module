# Feature Build Guide: Pagination + Soft Delete

---

## Working Branch — `feat/pagination-soft-delete`

```bash
git checkout main
git pull origin main
git checkout -b feat/pagination-soft-delete
```

---

> **Status:** Planned
> **Branch:** `feat/pagination-soft-delete` (branch from `main`)
> **Target sub-module:** `po_sub_module/`, `material_link_sub_module/`, `goods_receipt_sub_module/` (read-only filter)
> **SRS refs:** NFR-04 (response time), NFR-19 (data lifecycle)

---

## 1. Feature Summary

**Problem.** All list endpoints (`GET /procurement/pos`, `/grns`, `/material-links`) return the full result set. With 1000+ POs per project the FE renders sluggishly and the network payload is large. Separately, deleting a PO (allowed in DRAFT) is hard-delete — no audit recovery path. GRN is correctly immutable; material-links and POs need soft-delete.

**Solution.** Add `limit / offset` query params (default 50, max 200) with a `total_count` header. Add `is_deleted` boolean on `ProcurementPO` and `ProcurementMaterialLink` (default false, indexed). DELETE endpoints set `is_deleted=true` instead of removing; list endpoints filter `is_deleted=false` unless explicit `include_deleted=true` is passed.

**In scope (MVP):**
- Query params: `limit`, `offset`, `include_deleted`.
- New `X-Total-Count` response header.
- Soft-delete on PO + MaterialLink (GRN remains hard immutable per FR-M08-002).
- Frontend tables paginate; rows with `is_deleted=true` render strike-through in admin view.

**Out of scope:**
- Cursor pagination.
- Auto-purge after N days.

---

## 2. User Stories

| ID | As a … | I want … | So that … |
|---|---|---|---|
| US-1 | Materials Engineer | first 50 POs load fast | I scroll, not wait |
| US-2 | Admin | recover an accidentally deleted PO | mistakes happen |

---

## 3. Architecture Diagram

```
GET /procurement/pos?limit=50&offset=0[&include_deleted=true]
   → repository.list(filters, limit, offset)
   → returns rows + total_count
   → router sets X-Total-Count header
```

---

## 4. Backend Plan

### 4.1 ORM Models
Add to `ProcurementPO` and `ProcurementMaterialLink`:
```python
is_deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, index=True)
deleted_at: Mapped[datetime | None]
deleted_by: Mapped[str | None] = mapped_column(String(200))
```

### 4.2 Sub-Module Layout
Extend existing sub-modules. No new directories.

### 4.3 DTOs
- `PaginatedResponseDTO[T] { items: list[T], total: int, limit: int, offset: int }` (utility).

### 4.4 API Endpoints
Modify existing:
| Method | Path | Query |
|---|---|---|
| GET | `/procurement/pos` | `+ limit, offset, include_deleted` |
| GET | `/procurement/grns` | `+ limit, offset` (no soft-delete) |
| GET | `/procurement/material-links` | `+ limit, offset, include_deleted` |
| DELETE | `/procurement/pos/{id}` | now soft (DRAFT-only condition retained) |
| DELETE | `/procurement/material-links/{id}` | soft |

### 4.5 Service Methods
Replace `delete()` with `soft_delete(id, actor)`; `list()` accepts `include_deleted: bool`.

### 4.6 Repository Methods
| Method | Notes |
|---|---|
| `list(filters, limit, offset, include_deleted)` | returns (rows, total) tuple |
| `soft_delete(id, actor)` | sets fields, returns row |

### 4.7 Alembic Migration
```python
def upgrade():
    for table in ("procurement_pos", "procurement_material_links"):
        op.add_column(table, sa.Column("is_deleted", sa.Boolean, nullable=False, server_default=sa.false()))
        op.add_column(table, sa.Column("deleted_at", sa.DateTime(timezone=True)))
        op.add_column(table, sa.Column("deleted_by", sa.String(200)))
        op.create_index(f"ix_{table}_is_deleted", table, ["is_deleted"])
def downgrade(): ...
```

### 4.8 `main.py` Wiring
None.

---

## 5. Frontend Plan

### 5.1 API Client
Modify list helpers to pass `limit/offset`; read `X-Total-Count` header.

### 5.2 Wireframes
```
┌─ POs ─────────────────────────────────────────────┐
│ … 50 rows …                                       │
│ ◄ Prev   Page 1 of 9 (424 total)   Next ►        │
│ ☐ Show deleted                                    │
└───────────────────────────────────────────────────┘
```

### 5.3 New Components
| File | Role |
|---|---|
| `Paginator.jsx` | reusable |

### 5.4 Integration Points
`POTab.jsx`, `MaterialLinksTab.jsx`, `GRNTab.jsx` — wrap tables.

---

## 6. End-to-End Sequence
```
FE mounts → list(limit=50, offset=0)
User clicks Next → offset += 50
Admin toggles include_deleted → re-fetch
```

---

## 7. Edge Cases & Error Handling

| Case | Behavior |
|---|---|
| offset > total | empty list + total in header |
| limit > 200 | 422 |
| Soft-delete a non-DRAFT PO | 422 (existing rule retained) |
| Restore | `PATCH /pos/{id}` with `is_deleted=false` permitted by admin only |

---

## 8. Verification / Acceptance Criteria

1. `GET /pos?limit=10&offset=0` returns 10 rows + `X-Total-Count` header.
2. Soft-deleting a PO removes it from default list but `include_deleted=true` shows it.
3. Frontend paginator advances; deleted toggle works.

---

## 9. File Touch List

**New files:**
```
backend/alembic/versions/010_pagination_softdelete.py
frontend/src/components/common/Paginator.jsx
```

**Modified files:**
| File | Change |
|---|---|
| `backend/app/models_v2/procurement.py` | + 3 cols on PO + MaterialLink |
| All affected `services/service.py` files | accept limit/offset/include_deleted; soft delete |
| All affected `repositories/repository.py` files | rewrite list() and delete() |
| All affected `routers/*.py` files | add query params; set header |
| `frontend/src/apis/procurementApi.js` | pass limit/offset; read header |
| `frontend/src/components/procurement/POTab.jsx` | use `Paginator` |
| `frontend/src/components/procurement/GRNTab.jsx` | use `Paginator` |
| `frontend/src/components/procurement/MaterialLinksTab.jsx` | use `Paginator` |
