"""Role-aware Procurement dashboard. 7 builders (logistics = own view)."""
from typing import Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.enums import POStatus, MaterialLinkStatus
from app.modules.identity_module.role_permissions import ROLE_DASHBOARD_VIEW
from ..repositories.repository import DashboardRepository
from ..dtos.role_response_dtos import RoleDashboardDTO, DashboardBlock, DashboardMetric


class RoleDashboardService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = DashboardRepository(db)

    async def get_my_dashboard(
        self, package_id: Optional[UUID], role_code: str, person_id: UUID,
    ) -> RoleDashboardDTO:
        view = ROLE_DASHBOARD_VIEW.get(role_code, "exec")
        builder = {
            "exec":       self._exec_blocks,
            "logistics":  self._logistics_blocks,
            "tender":     self._tender_blocks,
            "bim":        self._bim_blocks,
            "contract":   self._contract_blocks,
            "contractor": self._contractor_blocks,
            "pmc":        self._pmc_blocks,
        }.get(view, self._exec_blocks)
        blocks = await builder(package_id)
        return RoleDashboardDTO(
            view=view, role_code=role_code, package_id=package_id, blocks=blocks,
        )

    async def _exec_blocks(self, package_id: Optional[UUID]) -> list[DashboardBlock]:
        k = await self.repo.get_kpis(package_id)
        return [
            DashboardBlock(key="health", title="Procurement Health", drill_to="po", metrics=[
                DashboardMetric(label="Total POs", value=k["total_pos"]),
                DashboardMetric(label="Overdue deliveries", value=k["overdue_deliveries"],
                                intent=_intent(k["overdue_deliveries"], 0, 3, higher_is_better=False)),
                DashboardMetric(label="Delivery compliance",
                                value=f"{k['delivery_compliance_rate']*100:.1f}%",
                                intent=_intent(k["delivery_compliance_rate"], 0.9, 0.7, higher_is_better=True)),
                DashboardMetric(label="GRNs this month", value=k["grns_this_month"], intent="good"),
            ]),
            DashboardBlock(key="risk", title="Materials at Risk", drill_to="material_link", metrics=[
                DashboardMetric(label="Materials at risk", value=k["at_risk_materials"],
                                intent=_intent(k["at_risk_materials"], 0, 3, higher_is_better=False)),
                DashboardMetric(label="Critical-path delays", value=k["cp_materials_delayed"],
                                intent=_intent(k["cp_materials_delayed"], 0, 1, higher_is_better=False)),
            ]),
        ]

    async def _logistics_blocks(self, package_id: Optional[UUID]) -> list[DashboardBlock]:
        k = await self.repo.get_kpis(package_id)
        ps = k["pos_by_status"]
        return [
            DashboardBlock(key="open_pos", title="Open POs", drill_to="po", metrics=[
                DashboardMetric(label=status, value=cnt)
                for status, cnt in ps.items() if cnt > 0
            ] or [DashboardMetric(label="No POs yet", value=0)]),
            DashboardBlock(key="incoming", title="Incoming Goods", drill_to="grn", metrics=[
                DashboardMetric(label="GRNs total", value=k["total_grns"]),
                DashboardMetric(label="GRNs this month", value=k["grns_this_month"], intent="good"),
                DashboardMetric(label="Overdue deliveries", value=k["overdue_deliveries"],
                                intent=_intent(k["overdue_deliveries"], 0, 5, higher_is_better=False)),
            ]),
            DashboardBlock(key="stores", title="Stores & Inventory", drill_to="material_link", metrics=[
                DashboardMetric(label="Total material links", value=k["total_material_links"]),
                DashboardMetric(label="At risk / overdue", value=k["at_risk_materials"],
                                intent="warn" if k["at_risk_materials"] else "good"),
                DashboardMetric(label="On critical path & delayed", value=k["cp_materials_delayed"],
                                intent=_intent(k["cp_materials_delayed"], 0, 1, higher_is_better=False)),
            ]),
        ]

    async def _tender_blocks(self, package_id: Optional[UUID]) -> list[DashboardBlock]:
        k = await self.repo.get_kpis(package_id)
        ps = k["pos_by_status"]
        return [
            DashboardBlock(key="pipeline", title="Order Pipeline", drill_to="po", metrics=[
                DashboardMetric(label="Total POs", value=k["total_pos"]),
                DashboardMetric(label="Open / Draft",
                                value=ps.get("DRAFT", 0) + ps.get("PENDING_APPROVAL", 0)),
                DashboardMetric(label="Closed", value=ps.get("CLOSED", 0), intent="good"),
            ]),
            DashboardBlock(key="vendors", title="Vendor Performance", drill_to="po", metrics=[
                DashboardMetric(label="Delivery compliance",
                                value=f"{k['delivery_compliance_rate']*100:.1f}%",
                                intent=_intent(k["delivery_compliance_rate"], 0.9, 0.7, higher_is_better=True)),
                DashboardMetric(label="Overdue deliveries", value=k["overdue_deliveries"]),
            ]),
        ]

    async def _bim_blocks(self, package_id: Optional[UUID]) -> list[DashboardBlock]:
        k = await self.repo.get_kpis(package_id)
        return [
            DashboardBlock(key="specs", title="Material Specs", drill_to="material_link", metrics=[
                DashboardMetric(label="Linked materials", value=k["total_material_links"]),
                DashboardMetric(label="At risk", value=k["at_risk_materials"],
                                intent="warn" if k["at_risk_materials"] else "good"),
            ]),
            DashboardBlock(key="po_overview", title="PO Volume", drill_to="po", metrics=[
                DashboardMetric(label="Total POs", value=k["total_pos"]),
                DashboardMetric(label="GRNs this month", value=k["grns_this_month"]),
            ]),
        ]

    async def _contract_blocks(self, package_id: Optional[UUID]) -> list[DashboardBlock]:
        k = await self.repo.get_kpis(package_id)
        ps = k["pos_by_status"]
        return [
            DashboardBlock(key="contracts", title="Vendor Contracts", drill_to="po", metrics=[
                DashboardMetric(label="Total POs", value=k["total_pos"]),
                DashboardMetric(label="Pending approval", value=ps.get("PENDING_APPROVAL", 0),
                                intent="warn" if ps.get("PENDING_APPROVAL", 0) else "good"),
                DashboardMetric(label="Closed", value=ps.get("CLOSED", 0)),
            ]),
            DashboardBlock(key="penalty", title="Penalty / LD Risk", drill_to="po", metrics=[
                DashboardMetric(label="Overdue deliveries", value=k["overdue_deliveries"],
                                intent=_intent(k["overdue_deliveries"], 0, 3, higher_is_better=False)),
                DashboardMetric(label="Critical-path delays", value=k["cp_materials_delayed"]),
            ]),
        ]

    async def _contractor_blocks(self, package_id: Optional[UUID]) -> list[DashboardBlock]:
        k = await self.repo.get_kpis(package_id)
        return [
            DashboardBlock(key="my_grns", title="Goods Receipts", drill_to="grn", metrics=[
                DashboardMetric(label="GRNs raised this month", value=k["grns_this_month"]),
                DashboardMetric(label="Total GRNs", value=k["total_grns"]),
            ]),
            DashboardBlock(key="pending", title="Pending Receipts", drill_to="po", metrics=[
                DashboardMetric(label="Overdue deliveries", value=k["overdue_deliveries"],
                                intent="warn" if k["overdue_deliveries"] else "good"),
                DashboardMetric(label="Materials at risk", value=k["at_risk_materials"]),
            ]),
        ]

    async def _pmc_blocks(self, package_id: Optional[UUID]) -> list[DashboardBlock]:
        k = await self.repo.get_kpis(package_id)
        return [
            DashboardBlock(key="inspection", title="Awaiting Inspection", drill_to="grn", metrics=[
                DashboardMetric(label="GRNs this month", value=k["grns_this_month"]),
                DashboardMetric(label="Material links at risk", value=k["at_risk_materials"],
                                intent="warn" if k["at_risk_materials"] else "good"),
            ]),
            DashboardBlock(key="quality_holds", title="Quality on Materials", drill_to="material_link",
                           metrics=[
                DashboardMetric(label="Critical-path delays", value=k["cp_materials_delayed"],
                                intent=_intent(k["cp_materials_delayed"], 0, 1, higher_is_better=False)),
            ]),
        ]


def _intent(value, good_threshold, warn_threshold, *, higher_is_better: bool) -> str:
    if higher_is_better:
        if value >= good_threshold:
            return "good"
        if value >= warn_threshold:
            return "warn"
        return "bad"
    if value <= good_threshold:
        return "good"
    if value <= warn_threshold:
        return "warn"
    return "bad"
