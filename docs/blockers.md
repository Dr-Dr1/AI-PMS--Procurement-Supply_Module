# Project Blockers & Stakeholder Clarifications (v1)

This document tracks items that require stakeholder input or technical decisions before we can proceed with the next phase of implementation.

## 🛑 Technical Blockers

### 1. Offline Capability Requirement
*   **Context**: Site engineers work in tunnels, deep shafts, and station basements where cellular connectivity is non-existent.
*   **Blocker**: If "Live Sync" is the only mode, RFI/DPR capture will fail in 40% of the construction area.
*   **Question**: Is an **Offline-First / Sync-Later** architecture required for the mobile app?

### 2. P6 (Primavera) Integration
*   **Context**: The domain guide mentions XER formats and S-Curve comparisons.
*   **Blocker**: Manual entry of thousands of activities is error-prone.
*   **Question**: Do we need a parser for `.xer` or `.xml` files to ingest the master schedule, or will data be pulled from an existing API?

---

## ❓ Stakeholder Clarifications Needed

### 3. Design Weightage Granularity
*   **Context**: The guide allocates 15-18% weightage to Design.
*   - **Question**: How should this percentage be distributed across the design stages?
    *   Example: Conceptual (2%), Preliminary (3%), Detailed (5%), GFC Approval (8%)?
    *   Does this weightage vary between **Civil** and **Systems (E&M)** packages?

### 4. RA Bill (Payment) Workflow
*   **Context**: The guide mentions RA Bills follow RFI verification.
*   **Question**: Is there a formal **Joint Measurement Record (JMR)** or **Measurement Book (MB)** process that must sit between RFI approval and RA Bill generation, or does the system auto-calculate value directly from RFIs?

### 5. Permit to Work (PTW) Authority
*   **Context**: High-risk activities require fresh PTWs daily.
*   **Question**: In the DMRC/Contractor hierarchy, who has the final "Approving" authority to close a PTW and allow work to start? (Safety Officer, Resident Engineer, or Site In-Charge?)

### 6. Subsystem Definitions
*   **Context**: 11+ engineering disciplines work in the same space.
*   **Question**: Please provide the full list of `SubsystemType` enums required (e.g., Civil, S&T, Traction, TVS, E&M, AFC, PSD, etc.) to ensure the routing logic for RFIs is correct.

### 7. Legacy Data Migration
*   **Context**: Most Phase IV packages are already in progress.
*   **Question**: Do we need to migrate existing POs, Vendor scores, and Drawings from Excel/Legacy systems, or will this system only track "Day 1" data after launch?
