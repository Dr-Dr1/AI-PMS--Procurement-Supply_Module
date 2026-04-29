"""
Model Registry — all SQLAlchemy models imported here so Alembic can discover them.
"""

# Layer 0: Foundation
from app.models.layer0 import (
    Program, Corridor, Package, Contract, Organization, Role, Person,
)

# Layer 1: Operational Core
from app.models.layer1 import (
    Activity, Dependency, Baseline, ITP, RFI, DPR, DPREntry,
    ProgressMeasurement,
)

# Layer 4: Audit
from app.models.layer4 import AuditEvent

# Procurement & Supply Chain
from app.models.procurement import (
    Vendor, Material, PurchaseOrder, POLineItem,
    Delivery, DeliveryItem, FATTest, VendorScoreHistory,
)

# Legacy (will be removed after migration)
from app.models.models import ProcurementOrder
