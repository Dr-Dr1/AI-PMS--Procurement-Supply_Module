from uuid import UUID
from typing import Optional
from datetime import date, datetime

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models_v2.procurement import ProcurementPO, ProcurementGRN, ProcurementMaterialLink
from app.core.enums import POStatus, MaterialLinkStatus


class DashboardRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_kpis(self, package_id: Optional[UUID]) -> dict:
        today = date.today()
        now = datetime.utcnow()

        # PO stats
        po_q = select(ProcurementPO)
        if package_id:
            po_q = po_q.where(ProcurementPO.package_id == package_id)
        pos = list((await self.db.execute(po_q)).scalars().all())

        total_pos = len(pos)
        pos_by_status = {s.value: 0 for s in POStatus}
        overdue = 0
        for po in pos:
            pos_by_status[po.status] = pos_by_status.get(po.status, 0) + 1
            if (
                po.committed_delivery_date
                and po.committed_delivery_date < today
                and po.status != POStatus.CLOSED
            ):
                overdue += 1

        # GRN stats
        grn_q = select(ProcurementGRN)
        if package_id:
            grn_q = grn_q.where(ProcurementGRN.package_id == package_id)
        grns = list((await self.db.execute(grn_q)).scalars().all())

        total_grns = len(grns)
        grns_this_month = sum(
            1 for g in grns
            if g.received_date
            and g.received_date.month == today.month
            and g.received_date.year == today.year
        )

        # Material link stats
        ml_q = select(ProcurementMaterialLink)
        if package_id:
            ml_q = ml_q.where(ProcurementMaterialLink.package_id == package_id)
        links = list((await self.db.execute(ml_q)).scalars().all())

        total_links = len(links)
        at_risk = sum(1 for l in links if l.status in (MaterialLinkStatus.AT_RISK, MaterialLinkStatus.OVERDUE))
        cp_delayed = sum(1 for l in links if l.is_critical_path and l.status == MaterialLinkStatus.OVERDUE)

        # Delivery compliance: GRNs received on or before ordered delivery vs total closed POs
        closed_pos = [p for p in pos if p.status == POStatus.CLOSED]
        if closed_pos:
            on_time = sum(
                1 for p in closed_pos
                if not p.is_overdue
            )
            compliance = on_time / len(closed_pos)
        else:
            compliance = 1.0

        return {
            "total_pos": total_pos,
            "pos_by_status": pos_by_status,
            "overdue_deliveries": overdue,
            "at_risk_materials": at_risk,
            "cp_materials_delayed": cp_delayed,
            "delivery_compliance_rate": round(compliance, 4),
            "total_grns": total_grns,
            "grns_this_month": grns_this_month,
            "total_material_links": total_links,
        }
