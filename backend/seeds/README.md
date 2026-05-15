# Database Seed Guide

Populates identity + procurement/supply module tables with realistic sample data for development and testing.

---

## Prerequisites

- PostgreSQL running and accessible
- `backend/.env` has a valid `DATABASE_URL`
- Database tables created (via Alembic migrations or `create_tables.py`)
- Python virtualenv activated

```bash
# from repo root
cd backend
source venv/bin/activate        # Linux/macOS
# or
.\venv\Scripts\Activate.ps1     # Windows PowerShell
```

---

## Run Seeds

### Option A — Full seed (recommended)

Runs identity then procurement module in dependency order.

```bash
cd backend
python -m seeds.seed_all
```

### Option B — Identity only

Orgs, roles, and persons only.

```bash
cd backend
python -m seeds.identity_seed
```

### Option C — Procurement module only

Run this **after** identity seed exists.

```bash
cd backend
python -m seeds.procurement_seed
```

> All three commands are **idempotent** — safe to re-run. Existing rows are skipped.

---

## What Gets Created

### Identity (`identity_seed.py`)

| Table | Count | Details |
|---|---|---|
| `organizations` | 4 | DMRC (Owner), L&T (Contractor), AECOM (PMC), MOHUA (Client) |
| `roles` | 27 | L1–L6 RBAC tiers, AI access levels FULL/PARTIAL/LIMITED |
| `persons` | 26 | One persona per role with email and org assignment |

### Procurement Module (`procurement_seed.py`)

| Table | Count | States covered |
|---|---|---|
| `procurement_pos` | 6 | Tata Steel, ACC Cement, Siemens, Doka, Alstom, Fosroc vendors |
| `procurement_po_line_items` | 12 | 2 line items per PO |
| `procurement_grns` | 4 | ACCEPTED (×2), PARTIALLY_ACCEPTED (×2) |
| `procurement_material_links` | 5 | ON_TRACK, AT_RISK (×2), OVERDUE (×2) |

PO statuses covered: APPROVED, PARTIALLY_DELIVERED, FULLY_DELIVERED, DRAFT, UNDER_REVIEW

---

## Testing with Personas

All person UUIDs are deterministic. Use them as `X-User-ID` headers to switch persona in API calls.

The seed prints the full list on each run. Quick reference for common roles:

| Role | Person | Email |
|---|---|---|
| Chief Contract Manager (Owner) | I. Bose | ibose@dmrc.in |
| Logistics Manager (Owner) | E. Das | edas@dmrc.in |
| Tender Manager (Owner) | Q. Bhatt | qbhatt@dmrc.in |
| Quantity Surveyor (Owner) | N. Rao | nrao@dmrc.in |
| Contractor PM | Y. Choudhury | ychoudhury@lntmetro.in |
| PMC Reviewer | J. Anderson | janderson@aecom.com |
| Super Admin | Admin (System) | admin@aipms.local |

**Get the UUID for any persona:**

```python
import uuid
NS = uuid.NAMESPACE_DNS

def person_id(role_code: str) -> uuid.UUID:
    return uuid.uuid5(NS, f"aipms.identity.person.{role_code}")

# Example
print(person_id("OWNER_CHIEF_CONTRACT_MGR"))
```

**Example API call:**

```bash
curl -H "X-User-ID: <person_uuid>" http://localhost:8000/api/v1/procurement/pos
```

---

## Placeholder IDs

Procurement records reference package UUIDs that are stable across environments.
These are derived deterministically — no schedule_v2 data needed.

| Placeholder | Code | UUID derivation |
|---|---|---|
| Civil Package | `PKG-CIVIL-001` | `uuid5(NS, "aipms.procurement.package.PKG-CIVIL-001")` |
| Electrical Package | `PKG-ELEC-001` | `uuid5(NS, "aipms.procurement.package.PKG-ELEC-001")` |
| Signalling Package | `PKG-SIG-001` | `uuid5(NS, "aipms.procurement.package.PKG-SIG-001")` |

---

## Resetting Seed Data

To wipe and re-seed:

```sql
-- Run in psql or any SQL client
TRUNCATE procurement_material_links, procurement_grns,
         procurement_po_line_items, procurement_pos CASCADE;

TRUNCATE persons, roles, organizations CASCADE;
```

Then re-run:

```bash
python -m seeds.seed_all
```

---

## Seed File Reference

```
backend/seeds/
├── seed_all.py           # Master runner (identity → procurement)
├── identity_seed.py      # Orgs, roles, persons
├── procurement_seed.py   # All procurement/supply module tables
└── README.md             # This file
```
