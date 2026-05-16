# Feature Build Guides

One markdown file per planned feature. Each guide includes the full design (models, API contract, frontend wireframes, file-touch list) **and the branch name** to use when building it.

## Conventions

- **Branch naming:** `feat/<kebab-case-feature-name>` — branch from `main`, PR back to `main`.
- **One feature per branch.** Do not combine unrelated features.
- **Commit incrementally** following the §File Touch List inside each guide; do not squash the whole feature into one commit.
- **Update the guide** if the implementation diverges from the plan — the guide is the source of truth for "how we built it."
- **Do not commit on `main` directly.**

## Index

> **Always work on the listed branch.** Branch from `main`, PR back to `main`.

| Feature | Working Branch | Doc | Status |
|---|---|---|---|
| Multi-step PO approval chain | **`feat/po-approval-chain`** | [`PO_APPROVAL_CHAIN.md`](./PO_APPROVAL_CHAIN.md) | Planned |
| GRN ↔ Quality (ITP/RFI) integration | **`feat/grn-qc-integration`** | [`GRN_QC_INTEGRATION.md`](./GRN_QC_INTEGRATION.md) | Planned |
| Predictive material risk score (A09) | **`feat/material-risk-ai`** | [`MATERIAL_RISK_AI.md`](./MATERIAL_RISK_AI.md) | Planned |
| CP-impact alert notification fan-out (FR-M08-004) | **`feat/cp-impact-alerts`** | [`CP_IMPACT_ALERTS.md`](./CP_IMPACT_ALERTS.md) | Planned |
| Vendor master + performance registry | **`feat/vendor-registry`** | [`VENDOR_REGISTRY.md`](./VENDOR_REGISTRY.md) | Planned |
| Delivery photo + GPS evidence (NFR-24) | **`feat/delivery-photo-evidence`** | [`DELIVERY_PHOTO_EVIDENCE.md`](./DELIVERY_PHOTO_EVIDENCE.md) | Planned |
| Immutable audit trail (NFR-16) | **`feat/audit-trail-logging`** | [`AUDIT_TRAIL_LOGGING.md`](./AUDIT_TRAIL_LOGGING.md) | Planned |
| Pagination + soft-delete on list endpoints | **`feat/pagination-soft-delete`** | [`PAGINATION_AND_SOFT_DELETE.md`](./PAGINATION_AND_SOFT_DELETE.md) | Planned |
| Procurement Agent (A09) — AI reorder / slip forecast | **`feat/procurement-agent-ai`** | [`PROCUREMENT_AGENT_AI.md`](./PROCUREMENT_AGENT_AI.md) | Planned |

## How to add a new feature guide

1. Branch from `main` for the doc itself: `git checkout -b docs/<feature-name>-guide`.
2. Copy [`_TEMPLATE.md`](./_TEMPLATE.md) — it is the canonical 9-section template (status block, branch instructions, ASCII wireframes, attribute tables, endpoint contracts with example payloads, file touch list).
3. Fill the top-of-file status block:
   ```
   > **Status:** Planned / In progress / Built
   > **Branch:** `feat/<feature-name>` (branch from `main`)
   > **Target sub-module:** <which sub-module this extends, or "new">
   ```
4. Fill the **Working Branch** section's `git checkout -b feat/<feature-name>` block.
5. Add the row to the Index table above.
6. Add an entry to [`../MODULE_STATUS.md`](../MODULE_STATUS.md) §5 Known Gaps (or §6 Reference traceability) pointing at the new guide.
7. Commit the doc on `docs/<feature-name>-guide`; open PR; merge before starting implementation work on the `feat/` branch.

## Related

- [`../MODULE_STATUS.md`](../MODULE_STATUS.md) — overall module status + roadmap.
- [`../README.md`](../README.md) — top-level docs index + reference inputs (CDM/SRS).
