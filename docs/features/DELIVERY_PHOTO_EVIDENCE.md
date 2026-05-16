# Feature Build Guide: Delivery Photo + GPS Evidence on GRN

---

## Working Branch — `feat/delivery-photo-evidence`

```bash
git checkout main
git pull origin main
git checkout -b feat/delivery-photo-evidence
```

---

> **Status:** Planned
> **Branch:** `feat/delivery-photo-evidence` (branch from `main`)
> **Target sub-module:** `goods_receipt_sub_module/` (extend)
> **SRS refs:** FR-M12-003 (GPS + Photo Evidence), NFR-11 (SHA-256), NFR-24 (offline)

---

## 1. Feature Summary

**Problem.** A GRN today is a row of numbers — it asserts that 40 cantilever masts arrived, but there is no proof. FR-M12-003 demands GPS + photo evidence on field records. NFR-11 demands SHA-256 hashing for tamper-evidence. Today neither is captured for procurement.

**Solution.** Extend `ProcurementGRN` with `photos: JSON` (list of `{storage_uri, sha256, captured_at, lat, lon}`). Mobile capture goes through a small PWA upload endpoint that stores blobs in MinIO (matching the CV module pattern). Hash is computed server-side on ingestion; mismatch on retrieval raises an integrity alert.

**In scope (MVP):**
- Multipart photo upload endpoint per GRN.
- MinIO storage; bucket `procurement-grn-evidence`.
- SHA-256 on every blob; verify on retrieval.
- Lat/lon captured from browser geolocation or EXIF.
- Offline queue in PWA (IndexedDB → sync on reconnect).

**Out of scope:**
- Image OCR on test certificates (separate feature).
- Video evidence.

---

## 2. User Stories

| ID | As a … | I want … | So that … |
|---|---|---|---|
| US-1 | Storekeeper | snap 2-3 photos when goods arrive | the inspector can audit later |
| US-2 | Field worker | record GRN even without signal | submission isn't blocked at site |
| US-3 | Auditor | be sure photos haven't been swapped | NFR-11 |

---

## 3. Architecture Diagram

```
Mobile/PWA ─► POST /procurement/grns/{id}/photos (multipart)
            ▲
            └ offline → IndexedDB queue → sync
Backend: photo_service → storage.minio_client.put_object()
       │ hashlib.sha256 stream → photos JSON appended
       ▼
GRN row updated; integrity check on GET /photos
```

---

## 4. Backend Plan

### 4.1 ORM Models
Add to `ProcurementGRN`:
```python
photos: Mapped[list | None] = mapped_column(JSON, default=list)
# shape: [{ "storage_uri": "...", "sha256": "...", "captured_at": "...", "lat": 28.56, "lon": 77.21 }]
```

### 4.2 Sub-Module Layout
Extend existing `goods_receipt_sub_module/`. New helper module:
```
app/modules/procurement_module/goods_receipt_sub_module/
└── storage/
    ├── __init__.py
    ├── minio_client.py
    └── hash_utils.py
```

### 4.3 DTOs
`PhotoAddResponseDTO { sha256, storage_uri, captured_at }`
`GRNResponseDTO` — extend with `photos: list[PhotoEntryDTO]`.

### 4.4 API Endpoints
| Method | Path | Notes |
|---|---|---|
| POST | `/procurement/grns/{grn_id}/photos` | multipart, multiple files |
| GET | `/procurement/grns/{grn_id}/photos` | list with signed URLs |
| GET | `/procurement/grns/{grn_id}/photos/{idx}/verify` | re-hash + compare |

### 4.5 Service Methods
| Method | Signature | Notes |
|---|---|---|
| `add_photos(grn_id, files, lat, lon)` | streams to MinIO, hashes, appends to JSON column |
| `verify_photo(grn_id, idx)` | re-hash stored bytes; raise on mismatch |

### 4.6 Repository Methods
| Method | Notes |
|---|---|
| `append_photo_entry(grn_id, entry)` | atomic JSONB update |

### 4.7 Alembic Migration
```python
def upgrade():
    op.add_column("procurement_grns", sa.Column("photos", postgresql.JSON, server_default="[]"))
def downgrade():
    op.drop_column("procurement_grns", "photos")
```

### 4.8 `main.py` Wiring
None.

Env: `MINIO_ENDPOINT`, `MINIO_ACCESS_KEY`, `MINIO_SECRET_KEY`, `MINIO_BUCKET_GRN=procurement-grn-evidence`.

---

## 5. Frontend Plan

### 5.1 API Client
Add: `uploadGRNPhotos`, `listGRNPhotos`, `verifyGRNPhoto`.

### 5.2 Wireframes
```
┌─ GRN Detail · Photos ─────────────────────────────┐
│ [📷 Add]                                          │
│ 1.  IMG_001.jpg   28.56°, 77.21°  ✓ hash ok       │
│ 2.  IMG_002.jpg   28.56°, 77.21°  ✓ hash ok       │
└───────────────────────────────────────────────────┘
```

### 5.3 New Components
| File | Role |
|---|---|
| `GRNPhotoUploader.jsx` | camera input + lat/lon |
| `GRNPhotoGallery.jsx` | thumbnails with verify |
| `offline/syncQueue.js` | IndexedDB queue |

### 5.4 Integration Points
`GRNTab.jsx` — add Photos tab inside GRN detail modal.

---

## 6. End-to-End Sequence
```
Storekeeper opens GRN → Add photo → camera + geolocation → upload
Backend streams to MinIO; computes sha256; appends entry
GET /photos → list with signed URLs; auditor opens verify → re-hash → ok
```

---

## 7. Edge Cases & Error Handling

| Case | Behavior |
|---|---|
| Geolocation denied | photo saved with `lat=null, lon=null`; warning shown |
| MinIO down | 503 with retry guidance; PWA queues |
| Hash mismatch on verify | response 422 with `"integrity_error"` |
| File >10 MB | 413 |

---

## 8. Verification / Acceptance Criteria

1. Upload 2 photos to a GRN → JSON column has 2 entries with hashes.
2. Verify endpoint passes; flipping a byte in MinIO blob → 422.
3. PWA queue replays after reconnect (manual test).

---

## 9. File Touch List

**New files:**
```
backend/app/modules/procurement_module/goods_receipt_sub_module/storage/
├── __init__.py
├── minio_client.py
└── hash_utils.py

backend/alembic/versions/008_grn_photos.py
frontend/src/components/procurement/GRNPhotoUploader.jsx
frontend/src/components/procurement/GRNPhotoGallery.jsx
frontend/src/offline/syncQueue.js
```

**Modified files:**
| File | Change |
|---|---|
| `backend/app/models_v2/procurement.py` | + `photos` column |
| `backend/app/modules/procurement_module/goods_receipt_sub_module/dtos/response_dtos.py` | + `PhotoEntryDTO` |
| `backend/app/modules/procurement_module/goods_receipt_sub_module/services/service.py` | + `add_photos`, `verify_photo` |
| `backend/app/modules/procurement_module/goods_receipt_sub_module/routers/grn_router.py` | + 3 endpoints |
| `backend/requirements.txt` | + `minio` |
| `frontend/src/apis/procurementApi.js` | + 3 helpers |
| `frontend/src/components/procurement/GRNTab.jsx` | mount uploader + gallery |
