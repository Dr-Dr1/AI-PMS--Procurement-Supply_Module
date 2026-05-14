import { useState, useEffect, useMemo } from 'react'
import { getAllProjects, getCorridorsByProject, getPackagesByProject } from '../apis/procurementApi'
import RoleProcurementDashboard from '../components/procurement/dashboard/RoleProcurementDashboard'
import POTab from '../components/procurement/POTab'
import GRNTab from '../components/procurement/GRNTab'
import MaterialLinksTab from '../components/procurement/MaterialLinksTab'
import PersonaSwitcher from '../components/identity/PersonaSwitcher'
import { useUser } from '../context/UserContext'
import styles from './procurement.module.css'

const TABS = [
  { id: 'dashboard',      label: 'Dashboard',      icon: '▦', anyOf: ['procurement.dashboard.exec','procurement.dashboard.logistics','procurement.dashboard.tender','procurement.dashboard.bim','procurement.dashboard.contract','procurement.dashboard.contractor','procurement.dashboard.pmc'] },
  { id: 'po',             label: 'PO Register',    icon: '≡', anyOf: ['procurement.po.view'] },
  { id: 'deliveries',     label: 'Deliveries',     icon: 'G',  anyOf: ['procurement.gr.view'] },
  { id: 'material-links', label: 'Material Links', icon: 'M',  anyOf: ['procurement.material_link.view'] },
]

function isAllowed(me, tab) {
  if (!me) return false
  if (me.is_superadmin) return true
  if (Array.isArray(me.features) && me.features.includes('*')) return true
  return tab.anyOf.some(f => me.features?.includes(f))
}

export default function Procurement() {
  const { me } = useUser()
  const visibleTabs = useMemo(() => TABS.filter(t => isAllowed(me, t)), [me])
  const [activeTab, setActiveTab] = useState('dashboard')

  useEffect(() => {
    if (!visibleTabs.length) return
    if (!visibleTabs.find(t => t.id === activeTab)) {
      setActiveTab(visibleTabs[0].id)
    }
  }, [visibleTabs, activeTab])
  const [projects, setProjects] = useState([])
  const [corridors, setCorridors] = useState([])
  const [allPackages, setAllPackages] = useState([])
  const [selectedProjectId, setSelectedProjectId] = useState(null)
  const [selectedCorridorId, setSelectedCorridorId] = useState(null)
  const [selectedPackageId, setSelectedPackageId] = useState(null)
  const [error, setError] = useState(null)

  useEffect(() => {
    getAllProjects()
      .then(({ data }) => {
        const list = data.data || []
        setProjects(list)
        if (list.length > 0) setSelectedProjectId(list[0].id)
      })
      .catch(() => setError('Failed to load projects'))
  }, [])

  useEffect(() => {
    if (!selectedProjectId) return
    const project = projects.find(p => p.id === selectedProjectId)
    if (!project) return
    setSelectedCorridorId(null)
    setSelectedPackageId(null)
    Promise.all([
      getCorridorsByProject(project.proj_id),
      getPackagesByProject(),
    ])
      .then(([cr, pr]) => {
        const cList = cr.data?.data || []
        const pList = pr.data?.data || []
        setCorridors(cList)
        setAllPackages(pList)
        if (cList.length > 0) setSelectedCorridorId(cList[0].id)
      })
      .catch(() => setError('Failed to load corridors/packages'))
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedProjectId, projects])

  const filteredPackages = selectedCorridorId
    ? allPackages.filter(p => p.corridor_id === selectedCorridorId)
    : allPackages

  useEffect(() => {
    if (filteredPackages.length > 0) {
      setSelectedPackageId(filteredPackages[0].id)
    } else {
      setSelectedPackageId(null)
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedCorridorId, allPackages.length])

  return (
    <div className={styles.shell}>
      <div className={styles.controlBar}>
        <span className={styles.barTitle}>Procurement</span>
        <span className={styles.barDivider} />

        <PersonaSwitcher />

        <nav className={styles.navTabs}>
          {visibleTabs.map(t => (
            <button
              key={t.id}
              className={activeTab === t.id ? styles.navActive : styles.navItem}
              onClick={() => setActiveTab(t.id)}
            >
              <span className={styles.navIcon}>{t.icon}</span>
              {t.label}
            </button>
          ))}
        </nav>

        <span className={styles.barSpacer} />

        <div className={styles.selectors}>
          <div className={styles.selectorGroup}>
            <span className={styles.selectorLabel}>Project</span>
            <select
              className={styles.sel}
              value={selectedProjectId ?? ''}
              onChange={e => setSelectedProjectId(e.target.value)}
            >
              {projects.map(p => (
                <option key={p.id} value={p.id}>
                  {p.proj_short_name || p.proj_name || p.id}
                </option>
              ))}
            </select>
          </div>
          {corridors.length > 0 && (
            <div className={styles.selectorGroup}>
              <span className={styles.selectorLabel}>Corridor</span>
              <select
                className={styles.sel}
                value={selectedCorridorId ?? ''}
                onChange={e => setSelectedCorridorId(e.target.value)}
              >
                {corridors.map(c => (
                  <option key={c.id} value={c.id}>{c.corridor_name}</option>
                ))}
              </select>
            </div>
          )}
          {filteredPackages.length > 0 && (
            <div className={styles.selectorGroup}>
              <span className={styles.selectorLabel}>Package</span>
              <select
                className={styles.sel}
                value={selectedPackageId ?? ''}
                onChange={e => setSelectedPackageId(e.target.value)}
              >
                {filteredPackages.map(p => (
                  <option key={p.id} value={p.id}>{p.package_name}</option>
                ))}
              </select>
            </div>
          )}
        </div>
      </div>

      <div className={styles.content}>
        <div className={styles.tabWrap}>
          {error && <p className={styles.error}>{error}</p>}
          {!selectedPackageId && <p className={styles.dim}>Select a package to view procurement data.</p>}
          {selectedPackageId && (
            <>
              {activeTab === 'dashboard'      && <RoleProcurementDashboard packageId={selectedPackageId} />}
              {activeTab === 'po'             && <POTab packageId={selectedPackageId} />}
              {activeTab === 'deliveries'     && <GRNTab packageId={selectedPackageId} />}
              {activeTab === 'material-links' && <MaterialLinksTab packageId={selectedPackageId} />}
            </>
          )}
        </div>
      </div>
    </div>
  )
}
