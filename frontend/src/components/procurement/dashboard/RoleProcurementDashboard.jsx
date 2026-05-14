import { useUser } from '../../../context/UserContext'
import ExecDashboard from './dashboards/ExecDashboard'
import LogisticsDashboard from './dashboards/LogisticsDashboard'
import TenderDashboard from './dashboards/TenderDashboard'
import BimDashboard from './dashboards/BimDashboard'
import ContractDashboard from './dashboards/ContractDashboard'
import ContractorDashboard from './dashboards/ContractorDashboard'
import PmcDashboard from './dashboards/PmcDashboard'


const VIEW_COMPONENTS = {
  exec:       ExecDashboard,
  logistics:  LogisticsDashboard,
  tender:     TenderDashboard,
  bim:        BimDashboard,
  contract:   ContractDashboard,
  contractor: ContractorDashboard,
  pmc:        PmcDashboard,
}

export default function RoleProcurementDashboard({ packageId }) {
  const { me } = useUser()
  if (!me) {
    return <p style={{ padding: 20, color: '#6b7280' }}>Select a persona to view your dashboard.</p>
  }
  const Component = VIEW_COMPONENTS[me.dashboard_view] || ExecDashboard
  return <Component packageId={packageId} />
}
