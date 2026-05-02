# Implementation Plan: Procurement & Supply Module (Phase 2)

## Goal
Implement the missing features from "Chapter 3: Procurement and Supply Chain" to align the AI-PMS with stakeholder requirements.

## 1. Data Schema Updates (Layer 0 & 1)
### Enums (`app/core/enums.py`)
- Add `IndentStatus`: `DRAFT`, `SUBMITTED`, `TECH_REVIEW`, `COMMERCIAL_REVIEW`, `APPROVED`, `PO_ISSUED`, `REJECTED`.
- Add `EquipmentStrategy`: `PURCHASED`, `LEASED`.
- Update `MaterialCategory` to include `EQUIPMENT`.

### Models (`app/models/procurement.py`)
- **Indent**: Material requisition header.
  - Fields: `indent_number`, `status`, `requested_by`, `need_date`, `project_id`, `boq_reference`, `remarks`.
- **IndentLineItem**: Items requested in an indent.
  - Fields: `indent_id`, `material_id`, `quantity`, `unit`, `estimated_cost`.
- **MaterialScheduleLink**: Bridges procurement and construction timelines.
  - Fields: `material_id`, `activity_id`, `po_id` (optional), `required_quantity`, `need_date`, `status_flag` (Late, On-Track).
- **Material Update**: Add `is_equipment` and `strategy` (Purchased/Leased).

## 2. Backend Implementation
### DTOs (`app/modules/procurement/dtos/`)
- Create `IndentCreate`, `IndentRead`, `MaterialScheduleLinkCreate`, etc.

### Services (`app/modules/procurement/services/`)
- `IndentService`: Handle the 5-step approval flow mentioned in Chapter 3.
- `ScheduleProcurementService`: Logic to sync `Activity.planned_start` with `PO.expected_delivery_date`.

### Routers (`app/modules/procurement/routers/`)
- Add endpoints for Indents and Schedule Links.

## 3. Frontend Implementation
### Views
- **Indents Dashboard**: Create and track material requisitions.
- **Schedule Linkage View**: Visualize the "Material Gap" (`PO.delivery > Activity.start`).
- **Vendor Portal Updates**: Support FAT results and delivery tracking.

## 4. Integration
- Link `Indent` to `PurchaseOrder` (Step 6 of process flow).
- Link `Activity` (Layer 1) to `MaterialScheduleLink`.
