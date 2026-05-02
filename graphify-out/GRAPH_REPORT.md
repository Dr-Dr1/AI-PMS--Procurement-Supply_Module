# Graph Report - .  (2026-05-02)

## Corpus Check
- Corpus is ~17,553 words - fits in a single context window. You may not need a graph.

## Summary
- 387 nodes · 1823 edges · 17 communities detected
- Extraction: 26% EXTRACTED · 74% INFERRED · 0% AMBIGUOUS · INFERRED: 1342 edges (avg confidence: 0.52)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- [[_COMMUNITY_Deliveries|Deliveries]]
- [[_COMMUNITY_Deliveries|Deliveries]]
- [[_COMMUNITY_Deliveries|Deliveries]]
- [[_COMMUNITY_Community 3|Community 3]]
- [[_COMMUNITY_Community 4|Community 4]]
- [[_COMMUNITY_Community 5|Community 5]]
- [[_COMMUNITY_Vendor Management|Vendor Management]]
- [[_COMMUNITY_Database Migrations|Database Migrations]]
- [[_COMMUNITY_Vendor Management|Vendor Management]]
- [[_COMMUNITY_Community 9|Community 9]]
- [[_COMMUNITY_Community 10|Community 10]]
- [[_COMMUNITY_Community 11|Community 11]]
- [[_COMMUNITY_Community 12|Community 12]]
- [[_COMMUNITY_Community 13|Community 13]]
- [[_COMMUNITY_Community 14|Community 14]]
- [[_COMMUNITY_Community 30|Community 30]]
- [[_COMMUNITY_Community 31|Community 31]]

## God Nodes (most connected - your core abstractions)
1. `PurchaseOrderService` - 55 edges
2. `DeliveryService` - 53 edges
3. `FATTestService` - 53 edges
4. `VendorService` - 51 edges
5. `MaterialService` - 51 edges
6. `IndentService` - 51 edges
7. `MaterialScheduleLinkService` - 48 edges
8. `VendorScoreService` - 47 edges
9. `ProcurementService` - 47 edges
10. `DashboardService` - 45 edges

## Surprising Connections (you probably didn't know these)
- `get_dashboard()` --calls--> `DashboardService`  [INFERRED]
  app/modules/procurement/routers/router.py → app/modules/procurement/services/service.py
- `create_vendor()` --calls--> `VendorService`  [INFERRED]
  app/modules/procurement/routers/router.py → app/modules/procurement/services/service.py
- `list_vendors()` --calls--> `VendorService`  [INFERRED]
  app/modules/procurement/routers/router.py → app/modules/procurement/services/service.py
- `get_vendor()` --calls--> `VendorService`  [INFERRED]
  app/modules/procurement/routers/router.py → app/modules/procurement/services/service.py
- `update_vendor()` --calls--> `VendorService`  [INFERRED]
  app/modules/procurement/routers/router.py → app/modules/procurement/services/service.py

## Hyperedges (group relationships)
- **Procurement Lifecycle** — phase2_indents, api_documentation_pos, api_documentation_deliveries, api_documentation_fat [INFERRED 0.85]

## Communities

### Community 0 - "Deliveries"
Cohesion: 0.14
Nodes (53): BaseModel, DeliveryCreate, DeliveryItemCreate, DeliveryItemResponse, DeliveryResponse, DeliveryUpdate, FATTestCreate, FATTestResponse (+45 more)

### Community 1 - "Deliveries"
Cohesion: 0.14
Nodes (50): Base, ApprovalStatus, CurrencyCode, DeliveryStatus, EquipmentStrategy, FATStatus, IndentStatus, MaterialCategory (+42 more)

### Community 2 - "Deliveries"
Cohesion: 0.06
Nodes (4): DeliveryRepository, FATTestRepository, MaterialRepository, PurchaseOrderRepository

### Community 3 - "Community 3"
Cohesion: 0.28
Nodes (38): ActivityStatus, ActivityType, AuditAction, BaselineStatus, DependencyType, DPRStatus, InitiatorRole, ITPStatus (+30 more)

### Community 4 - "Community 4"
Cohesion: 0.06
Nodes (35): add_vendor_score(), convert_indent_to_po(), create_delivery(), create_fat_test(), create_indent(), create_material(), create_order(), create_purchase_order() (+27 more)

### Community 5 - "Community 5"
Cohesion: 0.39
Nodes (23): AIAccessLevel, ContractStandard, EOTMethodology, OrgType, Per expert AS06: FIDIC covers all contract types., 6-tier RBAC per Method Statement Section 14.1, RBACTier, SubsystemCategory (+15 more)

### Community 6 - "Vendor Management"
Cohesion: 0.22
Nodes (1): ApiService

### Community 7 - "Database Migrations"
Cohesion: 0.22
Nodes (5): lifespan(), init_db(), Run alembic migrations (sync operation), Initialize database with migrations on startup (runs in thread), run_migrations()

### Community 8 - "Vendor Management"
Cohesion: 0.29
Nodes (7): Deliveries API, FAT Tests API, Material Catalogue API, Purchase Orders API, Vendor Management API, Indents (Material Requisition), Material Schedule Link

### Community 9 - "Community 9"
Cohesion: 0.7
Nodes (1): _validate_transition()

### Community 10 - "Community 10"
Cohesion: 0.5
Nodes (1): add procurement models

### Community 11 - "Community 11"
Cohesion: 0.5
Nodes (1): create procurement table  Revision ID: 8442c332232d Revises: Create Date: 2026-0

### Community 12 - "Community 12"
Cohesion: 0.5
Nodes (1): add new module tables

### Community 13 - "Community 13"
Cohesion: 0.5
Nodes (1): add procurement models

### Community 14 - "Community 14"
Cohesion: 0.67
Nodes (2): get_sync_url(), Convert async database URL to sync for migrations

### Community 30 - "Community 30"
Cohesion: 1.0
Nodes (1): Procurement Module

### Community 31 - "Community 31"
Cohesion: 1.0
Nodes (1): Phase 2 Implementation Plan

## Knowledge Gaps
- **29 isolated node(s):** `Convert async database URL to sync for migrations`, `add procurement models`, `create procurement table  Revision ID: 8442c332232d Revises: Create Date: 2026-0`, `add new module tables`, `add procurement models` (+24 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **Thin community `Vendor Management`** (17 nodes): `api.js`, `ApiService`, `.convertIndentToPO()`, `.createIndent()`, `.createMaterial()`, `.createPurchaseOrder()`, `.createScheduleLink()`, `.createVendor()`, `.getDashboardSummary()`, `.getDeliveries()`, `.getFATTests()`, `.getIndents()`, `.getMaterials()`, `.getPurchaseOrders()`, `.getScheduleLinks()`, `.getVendors()`, `.request()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 9`** (5 nodes): `.update_status()`, `.update_status()`, `.update_status()`, `.update_status()`, `_validate_transition()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 10`** (4 nodes): `a2c2a0febb4e_add_procurement_models.py`, `downgrade()`, `add procurement models`, `upgrade()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 11`** (4 nodes): `8442c332232d_create_procurement_table.py`, `downgrade()`, `create procurement table  Revision ID: 8442c332232d Revises: Create Date: 2026-0`, `upgrade()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 12`** (4 nodes): `afa3fc3d28c5_add_new_module_tables.py`, `downgrade()`, `add new module tables`, `upgrade()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 13`** (4 nodes): `fc0a8671c15e_add_procurement_models.py`, `downgrade()`, `add procurement models`, `upgrade()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 14`** (3 nodes): `get_sync_url()`, `env.py`, `Convert async database URL to sync for migrations`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 30`** (1 nodes): `Procurement Module`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 31`** (1 nodes): `Phase 2 Implementation Plan`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `PurchaseOrderService` connect `Deliveries` to `Deliveries`, `Deliveries`, `Community 4`, `Community 9`?**
  _High betweenness centrality (0.055) - this node is a cross-community bridge._
- **Why does `DeliveryService` connect `Deliveries` to `Community 9`, `Deliveries`, `Community 4`, `Deliveries`?**
  _High betweenness centrality (0.050) - this node is a cross-community bridge._
- **Why does `FATTestService` connect `Deliveries` to `Community 9`, `Deliveries`, `Community 4`, `Deliveries`?**
  _High betweenness centrality (0.049) - this node is a cross-community bridge._
- **Are the 47 inferred relationships involving `PurchaseOrderService` (e.g. with `Procurement API Router — All endpoints for the Procurement & Supply Chain module` and `VendorRepository`) actually correct?**
  _`PurchaseOrderService` has 47 INFERRED edges - model-reasoned connections that need verification._
- **Are the 46 inferred relationships involving `DeliveryService` (e.g. with `Procurement API Router — All endpoints for the Procurement & Supply Chain module` and `VendorRepository`) actually correct?**
  _`DeliveryService` has 46 INFERRED edges - model-reasoned connections that need verification._
- **Are the 46 inferred relationships involving `FATTestService` (e.g. with `Procurement API Router — All endpoints for the Procurement & Supply Chain module` and `VendorRepository`) actually correct?**
  _`FATTestService` has 46 INFERRED edges - model-reasoned connections that need verification._
- **Are the 45 inferred relationships involving `VendorService` (e.g. with `Procurement API Router — All endpoints for the Procurement & Supply Chain module` and `VendorRepository`) actually correct?**
  _`VendorService` has 45 INFERRED edges - model-reasoned connections that need verification._