"""create procurement module tables

Revision ID: 002_procurement_module
Revises: afa3fc3d28c5
Create Date: 2026-05-12

"""
revision = '002_procurement_module'
down_revision = 'afa3fc3d28c5'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.execute("DROP TABLE IF EXISTS procurement_orders CASCADE")

    # Drop any stale enum types from partial previous runs, then recreate cleanly
    op.execute("DROP TYPE IF EXISTS po_status_enum CASCADE")
    op.execute("DROP TYPE IF EXISTS grn_status_enum CASCADE")
    op.execute("DROP TYPE IF EXISTS risk_level_enum CASCADE")
    op.execute("DROP TYPE IF EXISTS material_link_status_enum CASCADE")

    op.execute("CREATE TYPE po_status_enum AS ENUM ('DRAFT','ISSUED','ACKNOWLEDGED','DISPATCHED','CLOSED')")
    op.execute("CREATE TYPE grn_status_enum AS ENUM ('PENDING','ACCEPTED','PARTIALLY_ACCEPTED','REJECTED')")
    op.execute("CREATE TYPE risk_level_enum AS ENUM ('LOW','MEDIUM','HIGH')")
    op.execute("CREATE TYPE material_link_status_enum AS ENUM ('ON_TRACK','AT_RISK','OVERDUE')")

    op.execute("""
        CREATE TABLE IF NOT EXISTS procurement_pos (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            package_id UUID NOT NULL,
            po_number VARCHAR(100) NOT NULL UNIQUE,
            vendor_name VARCHAR(300) NOT NULL,
            description TEXT,
            total_amount NUMERIC(15,2) NOT NULL DEFAULT 0,
            currency VARCHAR(10) NOT NULL DEFAULT 'INR',
            status po_status_enum NOT NULL DEFAULT 'DRAFT',
            committed_delivery_date DATE,
            is_overdue BOOLEAN NOT NULL DEFAULT false,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
        )
    """)
    op.execute("CREATE INDEX IF NOT EXISTS ix_procurement_pos_package_id ON procurement_pos (package_id)")

    op.execute("""
        CREATE TABLE IF NOT EXISTS procurement_po_line_items (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            po_id UUID NOT NULL REFERENCES procurement_pos(id) ON DELETE CASCADE,
            item_code VARCHAR(100) NOT NULL,
            description TEXT NOT NULL,
            unit VARCHAR(50) NOT NULL,
            quantity NUMERIC(14,4) NOT NULL,
            unit_rate NUMERIC(14,4) NOT NULL,
            amount NUMERIC(15,2) NOT NULL DEFAULT 0,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now()
        )
    """)
    op.execute("CREATE INDEX IF NOT EXISTS ix_procurement_po_line_items_po_id ON procurement_po_line_items (po_id)")

    op.execute("""
        CREATE TABLE IF NOT EXISTS procurement_grns (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            po_id UUID NOT NULL REFERENCES procurement_pos(id),
            package_id UUID NOT NULL,
            grn_number VARCHAR(100) NOT NULL UNIQUE,
            received_date DATE NOT NULL,
            received_qty NUMERIC(14,4) NOT NULL,
            ordered_qty NUMERIC(14,4),
            unit VARCHAR(50) NOT NULL,
            status grn_status_enum NOT NULL DEFAULT 'ACCEPTED',
            test_certificate_ref VARCHAR(200),
            inspector VARCHAR(200),
            remarks TEXT,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now()
        )
    """)
    op.execute("CREATE INDEX IF NOT EXISTS ix_procurement_grns_package_id ON procurement_grns (package_id)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_procurement_grns_po_id ON procurement_grns (po_id)")

    op.execute("""
        CREATE TABLE IF NOT EXISTS procurement_material_links (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            package_id UUID NOT NULL,
            material_name VARCHAR(300) NOT NULL,
            activity_id VARCHAR(200),
            po_id UUID REFERENCES procurement_pos(id),
            is_critical_path BOOLEAN NOT NULL DEFAULT false,
            risk_score INTEGER NOT NULL DEFAULT 0,
            risk_level risk_level_enum NOT NULL DEFAULT 'LOW',
            status material_link_status_enum NOT NULL DEFAULT 'ON_TRACK',
            planned_delivery_date DATE,
            actual_delivery_date DATE,
            last_risk_refresh TIMESTAMPTZ,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
        )
    """)
    op.execute("CREATE INDEX IF NOT EXISTS ix_procurement_material_links_package_id ON procurement_material_links (package_id)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_procurement_material_links_po_id ON procurement_material_links (po_id)")


def downgrade():
    op.execute("DROP TABLE IF EXISTS procurement_material_links")
    op.execute("DROP TABLE IF EXISTS procurement_grns")
    op.execute("DROP TABLE IF EXISTS procurement_po_line_items")
    op.execute("DROP TABLE IF EXISTS procurement_pos")
    op.execute("DROP TYPE IF EXISTS po_status_enum")
    op.execute("DROP TYPE IF EXISTS grn_status_enum")
    op.execute("DROP TYPE IF EXISTS risk_level_enum")
    op.execute("DROP TYPE IF EXISTS material_link_status_enum")
