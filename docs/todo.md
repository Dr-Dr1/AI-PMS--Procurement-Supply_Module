# Domain Gap Analysis & Implementation Roadmap (v2)

Based on the **Metro Rail Construction Domain Guide (v2)**, here is the gap analysis between the current AI-PMS codebase and the physical reality of metro construction.

## 🔴 Critical Gaps (Missing Entities/Workflows)

### 1. Design & Engineering Lifecycle
*   **Gap**: No models for `Drawing`, `Transmittal`, or `ReviewCycle`.
*   **Domain Fact**: Design represents 15-18% of project weightage and is a primary blocker for construction.
*   **Required Update**: 
    - Create `Drawing` model with revision tracking.
    - Implement `Transmittal` and `DesignReview` workflow (Approved, Revise & Resubmit, GFC).
    - Add `weightage` field to `Activity` to support the 15-18% design progress rule.

### 2. Regulatory Permits & Safety (PTW)
*   **Gap**: No tracking for Regulatory Permits (Environmental, Traffic, Utility) or Permits to Work (PTW).
*   **Domain Fact**: High-risk activities (hot work, height, confined space) require daily PTWs. Regulatory delays are a top project risk.
*   **Required Update**:
    - Create `Permit` model for statutory clearances (MoEFCC, Tree cutting, Traffic).
    - Create `PermitToWork` (PTW) system for site operations (Hot work, Height, etc.).
    - Link PTWs to `DPR` for safety compliance reporting.

### 3. Quality Management (NCRs)
*   **Gap**: `NCR` (Non-Conformance Report) model is missing.
*   **Domain Fact**: NCRs must track both **Product** (defects) and **Process** (compliance) violations.
*   **Required Update**:
    - Create `NCR` model with `ncr_type` (Product vs Process).
    - Implement compliance tracking (Closure rate, Aging, Repeat rate).

### 4. Advanced Progress Reporting
*   **Gap**: Missing high-level aggregation for Weekly (WPR) and Monthly (MPR) reports.
*   **Domain Fact**: MPRs are the basis for executive dashboards and financial RA Bills.
*   **Required Update**:
    - Create `WeeklyProgressReport` and `MonthlyProgressReport` aggregations.
    - Implement S-Curve calculation logic (Planned vs Actual cumulative).

---

## 🟡 Partial Gaps (Enhancements Needed)

### 5. Procurement & Supply Chain
*   **Status**: `Indent`, `PurchaseOrder`, `Delivery`, and `FATTest` exist.
*   **Gap**: `Indent` approval flow is simplified; `EquipmentStrategy` (Purchased vs Leased) needs UI exposure.
*   **Required Update**:
    - Expand `Indent` logic to follow the 5-step commercial/technical approval flow.
    - Enhance `Material` model to better track "Leased" equipment overheads.

### 6. Organizational Hierarchy
*   **Status**: `Person` and `Organization` exist.
*   **Gap**: Role-based access doesn't yet mirror the DMRC (MD -> CPM) vs Contractor (PM -> SE) tree.
*   **Required Update**:
    - Implement specific `Role` mapping per the Chapter 2A Organizational Tree.

---

## ✅ Current Matches (Well-Implemented)
*   **RFI System**: Correctly identifies RFI closure as the primary verified progress signal.
*   **DPR System**: Correctly captures daily site data (manpower, equipment, weather) as supporting evidence.
*   **MaterialScheduleLink**: Successfully bridges the construction schedule with the procurement timeline.

---

## 📅 Immediate Next Steps
1.  **Phase 2.1**: Implement Design & Drawing models (High Weightage).
2.  **Phase 2.2**: Implement NCR and PTW systems (Safety & Compliance).
3.  **Phase 2.3**: Aggregate DPR data into Weekly/Monthly Reporting dashboards.
