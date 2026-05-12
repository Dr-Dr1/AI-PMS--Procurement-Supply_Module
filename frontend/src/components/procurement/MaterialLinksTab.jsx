import { useState, useEffect, useCallback } from 'react'
import { listMaterialLinks, createMaterialLink, updateMaterialLink, deleteMaterialLink, refreshLinkRisk, bulkRefreshRisk, listPOs, getActivitiesByPackage } from '../../apis/procurementApi'
import ProcurementModal from './ProcurementModal'
import ProcurementBadge from './ProcurementBadge'
import styles from './MaterialLinksTab.module.css'

const BLANK_LINK = {
  material_name: '', activity_id: '', po_id: '',
  is_critical_path: false, planned_delivery_date: '', actual_delivery_date: '',
}

const RISK_LEVELS = ['', 'LOW', 'MEDIUM', 'HIGH']

export default function MaterialLinksTab({ packageId }) {
  const [links, setLinks] = useState([])
  const [pos, setPOs] = useState([])
  const [activities, setActivities] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [riskFilter, setRiskFilter] = useState('')
  const [cpOnly, setCpOnly] = useState(false)
  const [showForm, setShowForm] = useState(false)
  const [editLink, setEditLink] = useState(null)
  const [form, setForm] = useState(BLANK_LINK)
  const [refreshing, setRefreshing] = useState(null)
  const [bulkRefreshing, setBulkRefreshing] = useState(false)

  const load = useCallback(() => {
    setLoading(true)
    const params = {}
    if (riskFilter) params.risk_level = riskFilter
    if (cpOnly) params.on_critical_path = true
    listMaterialLinks(packageId, params)
      .then(r => { setLinks(Array.isArray(r.data) ? r.data : []); setError(null) })
      .catch(e => setError(e.response?.data?.detail || 'Load failed'))
      .finally(() => setLoading(false))
  }, [packageId, riskFilter, cpOnly])

  useEffect(() => { load() }, [load])

  useEffect(() => {
    listPOs(packageId).then(r => setPOs(Array.isArray(r.data) ? r.data : [])).catch(() => {})
    getActivitiesByPackage(packageId)
      .then(r => setActivities(Array.isArray(r.data?.data) ? r.data.data : []))
      .catch(() => {})
  }, [packageId])

  const openCreate = () => { setForm(BLANK_LINK); setEditLink(null); setShowForm(true) }
  const openEdit = (link) => {
    setForm({
      material_name: link.material_name,
      activity_id: link.activity_id || '',
      po_id: link.po_id || '',
      is_critical_path: link.is_critical_path,
      planned_delivery_date: link.planned_delivery_date || '',
      actual_delivery_date: link.actual_delivery_date || '',
    })
    setEditLink(link)
    setShowForm(true)
  }

  const handleSave = async () => {
    if (!form.material_name) { setError('Material Name is required'); return }
    try {
      const payload = { ...form, package_id: packageId }
      if (!payload.activity_id) delete payload.activity_id
      if (!payload.po_id) delete payload.po_id
      if (!payload.planned_delivery_date) delete payload.planned_delivery_date
      if (!payload.actual_delivery_date) delete payload.actual_delivery_date
      if (editLink) await updateMaterialLink(editLink.id, payload)
      else await createMaterialLink(payload)
      setShowForm(false); setError(null); load()
    } catch (e) {
      setError(e.response?.data?.detail || 'Save failed')
    }
  }

  const handleDelete = async (link) => {
    if (!confirm(`Delete material link "${link.material_name}"?`)) return
    try { await deleteMaterialLink(link.id); load() } catch (e) { setError(e.response?.data?.detail || 'Delete failed') }
  }

  const handleRefresh = async (link) => {
    setRefreshing(link.id)
    try { await refreshLinkRisk(link.id); load() } catch (e) { setError(e.response?.data?.detail || 'Refresh failed') }
    finally { setRefreshing(null) }
  }

  const handleBulkRefresh = async () => {
    setBulkRefreshing(true)
    try { await bulkRefreshRisk(packageId); load() } catch (e) { setError(e.response?.data?.detail || 'Bulk refresh failed') }
    finally { setBulkRefreshing(false) }
  }

  const total = links.length
  const atRisk = links.filter(l => l.status === 'AT_RISK').length
  const overdue = links.filter(l => l.status === 'OVERDUE').length
  const cpCount = links.filter(l => l.is_critical_path).length

  return (
    <div>
      {/* Toolbar */}
      <div className={styles.toolbar}>
        <span className={styles.toolbarTitle}>Material Links <span className={styles.count}>{links.length}</span></span>
        <select className={styles.filterSel} value={riskFilter} onChange={e => setRiskFilter(e.target.value)}>
          {RISK_LEVELS.map(r => <option key={r} value={r}>{r || 'All Risk Levels'}</option>)}
        </select>
        <label className={styles.cpToggle}>
          <input type="checkbox" checked={cpOnly} onChange={e => setCpOnly(e.target.checked)} />
          Critical Path Only
        </label>
        <button className={styles.refreshBtn} onClick={handleBulkRefresh} disabled={bulkRefreshing}>
          {bulkRefreshing ? 'Refreshing…' : '⟳ Refresh All Risk'}
        </button>
        <button className={styles.addBtn} onClick={openCreate}>+ New Link</button>
      </div>

      {/* Stats bar */}
      <div className={styles.statsBar}>
        <div className={`${styles.stat} ${styles.statBlue}`}><div className={styles.statVal}>{total}</div><div className={styles.statLabel}>Total</div></div>
        <div className={`${styles.stat} ${styles.statAmber}`}><div className={styles.statVal}>{atRisk}</div><div className={styles.statLabel}>At Risk</div></div>
        <div className={`${styles.stat} ${overdue > 0 ? styles.statRed : ''}`}><div className={styles.statVal}>{overdue}</div><div className={styles.statLabel}>Overdue</div></div>
        <div className={styles.stat}><div className={styles.statVal}>{cpCount}</div><div className={styles.statLabel}>Critical Path</div></div>
      </div>

      {error && <p className={styles.error}>{error}</p>}

      {/* Create/Edit Modal */}
      {showForm && (
        <ProcurementModal
          title={editLink ? 'Edit Material Link' : 'New Material Link'}
          sub={editLink?.material_name}
          icon="🔗"
          onClose={() => setShowForm(false)}
          width={640}
          footer={
            <>
              <button className={styles.cancelBtn} onClick={() => setShowForm(false)}>Cancel</button>
              <button className={styles.submitBtn} onClick={handleSave}>{editLink ? 'Update' : 'Create'}</button>
            </>
          }
        >
          <div className={styles.formGrid}>
            <div className={`${styles.fieldGroup} ${styles.colSpan2}`}>
              <label className={styles.label}>Material Name *</label>
              <input className={styles.input} value={form.material_name} onChange={e => setForm(f => ({ ...f, material_name: e.target.value }))} placeholder="e.g. Steel Reinforcement Bars" />
            </div>
            <div className={styles.fieldGroup}>
              <label className={styles.label}>Activity</label>
              <select className={styles.input} value={form.activity_id} onChange={e => setForm(f => ({ ...f, activity_id: e.target.value }))}>
                <option value="">— no activity —</option>
                {activities.map(a => (
                  <option key={a.id} value={a.p6_activity_id}>
                    {a.p6_activity_id} — {a.activity_name}
                  </option>
                ))}
              </select>
            </div>
            <div className={styles.fieldGroup}>
              <label className={styles.label}>Purchase Order</label>
              <select className={styles.input} value={form.po_id} onChange={e => setForm(f => ({ ...f, po_id: e.target.value }))}>
                <option value="">— no PO linked —</option>
                {pos.map(p => <option key={p.id} value={p.id}>{p.po_number} — {p.vendor_name}</option>)}
              </select>
            </div>
            <div className={styles.fieldGroup}>
              <label className={styles.label}>Planned Delivery Date</label>
              <input className={styles.input} type="date" value={form.planned_delivery_date} onChange={e => setForm(f => ({ ...f, planned_delivery_date: e.target.value }))} />
            </div>
            <div className={styles.fieldGroup}>
              <label className={styles.label}>Actual Delivery Date</label>
              <input className={styles.input} type="date" value={form.actual_delivery_date} onChange={e => setForm(f => ({ ...f, actual_delivery_date: e.target.value }))} />
            </div>
            <div className={`${styles.fieldGroup} ${styles.colSpan2}`}>
              <label className={styles.cpLabel}>
                <input type="checkbox" checked={form.is_critical_path} onChange={e => setForm(f => ({ ...f, is_critical_path: e.target.checked }))} />
                Critical Path Material
              </label>
            </div>
          </div>
        </ProcurementModal>
      )}

      {/* Table */}
      {loading ? <p className={styles.dim}>Loading…</p> : (
        <div className={styles.tableWrap}>
          <table className={styles.table}>
            <thead>
              <tr>
                <th>Material Name</th>
                <th>Activity ID</th>
                <th>PO Number</th>
                <th>Planned Date</th>
                <th>Actual Date</th>
                <th>Risk Score</th>
                <th>Risk Level</th>
                <th>Status</th>
                <th>CP</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {links.length === 0 && (
                <tr><td colSpan={10} className={styles.empty}>No material links found.</td></tr>
              )}
              {links.map(link => {
                const po = pos.find(p => p.id === link.po_id)
                return (
                  <tr key={link.id} className={link.status === 'OVERDUE' ? styles.rowOverdue : link.status === 'AT_RISK' ? styles.rowAtRisk : ''}>
                    <td className={styles.materialCell}>{link.material_name}</td>
                    <td className={styles.monoCell}>{link.activity_id || '—'}</td>
                    <td className={styles.monoCell}>{po?.po_number || (link.po_id ? link.po_id.slice(0, 8) + '…' : '—')}</td>
                    <td>{link.planned_delivery_date || '—'}</td>
                    <td>{link.actual_delivery_date || '—'}</td>
                    <td><span className={styles.scoreCell} data-level={link.risk_level}>{link.risk_score}</span></td>
                    <td><ProcurementBadge status={link.risk_level} type="risk" /></td>
                    <td><ProcurementBadge status={link.status} type="ml" /></td>
                    <td>{link.is_critical_path ? <span className={styles.cpBadge}>CP</span> : <span className={styles.noCp}>—</span>}</td>
                    <td>
                      <div className={styles.actions}>
                        <button className={styles.actionBtn} onClick={() => openEdit(link)}>Edit</button>
                        <button className={styles.actionBtn} onClick={() => handleRefresh(link)} disabled={refreshing === link.id}>
                          {refreshing === link.id ? '…' : '⟳'}
                        </button>
                        <button className={styles.dangerBtn} onClick={() => handleDelete(link)}>Del</button>
                      </div>
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
