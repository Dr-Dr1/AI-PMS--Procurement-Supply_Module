# AI-PMS Procurement & Supply Module — Docs

Project-wide documentation for the AI-PMS Procurement & Supply Module (M08 of the AI-PMS suite).

## Index

| File | Purpose |
|---|---|
| [`INTRO.md`](./INTRO.md) | Brief intro to the Procurement Module (M08): what it does, core features, why useful. Start here. |
| [`MODULE_STATUS.md`](./MODULE_STATUS.md) | What is built today (backend sub-modules, models, migrations, frontend tabs, known gaps) + roadmap. |
| [`features/README.md`](./features/README.md) | Index of per-feature build guides. Conventions for branch naming and PR flow. |
| [`features/_TEMPLATE.md`](./features/_TEMPLATE.md) | 9-section template every new feature guide must follow. |

## Reference inputs (read-only — do not modify)

These docs in `C:\Users\lokesh\Documents\ai-pms-documents\` are the source of truth for what to build:

- `AIPMS_CDM_Schema_v1 (5).txt` / `AIPMS_CDM_v1.1 (4).txt` — Conceptual Data Model entities + fields
- `AIPMS_SRS_v1_0_Definitive_29APR2026 (1).txt` — Software Requirements Spec (FR/NFR IDs)
- `AIPMS_SRS_Elicitation_Guide (3).txt`
- `AIPMS_KT_Backend_Lokesh (2).txt` — Backend KT
- `AIPMS_Unified_Complete_Expert_Reviewed (1)_sheets.txt`

## Quick start for a new contributor

1. Read [`MODULE_STATUS.md`](./MODULE_STATUS.md) to see what already exists.
2. Pick a feature from [`features/README.md`](./features/README.md).
3. Open the feature's md file — it tells you exactly which `feat/<name>` branch to create, which files to touch, and how to verify.
4. `git checkout -b feat/<name>` from `main`. Implement. PR back to `main`.
