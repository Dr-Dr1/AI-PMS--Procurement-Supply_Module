import { useState, useEffect } from 'react'
import { getProcurementDashboard } from '../../apis/procurementApi'
import styles from './ProcurementDashboard.module.css'

const PO_STATUS_COLORS = {
  DRAFT: '#6b7280',
  ISSUED: '#2563eb',
  ACKNOWLEDGED: '#7c3aed',
  DISPATCHED: '#d97706',
  CLOSED: '#10b981',
}

function KpiCard({ label, value, sub, color }) {
  return (
    <div className={styles.kpiCard}>
      <div className={styles.kpiValue} style={{ color: color || '#1e3a8a' }}>{value ?? '—'}</div>
      <div className={styles.kpiLabel}>{label}</div>
      {sub && <div className={styles.kpiSub}>{sub}</div>}
    </div>
  )
}

function StatusBar({ byStatus }) {
  if (!byStatus) return null
  const entries = Object.entries(byStatus).filter(([, v]) => v > 0)
  if (entries.length === 0) return null
  return (
    <div className={styles.statusBarWrap}>
      {entries.map(([status, count]) => (
        <div key={status} className={styles.statusBarItem}>
          <span className={styles.statusDot} style={{ background: PO_STATUS_COLORS[status] || '#6b7280' }} />
          <span className={styles.statusName}>{status.replace(/_/g, ' ')}</span>
          <span className={styles.statusCount}>{count}</span>
        </div>
      ))}
    </div>
  )
}

export default function ProcurementDashboard({ packageId }) {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  useEffect(() => {
    if (!packageId) return
    setLoading(true)
    setError(null)
    getProcurementDashboard(packageId)
      .then(res => setData(res.data))
      .catch(() => setError('Failed to load dashboard'))
      .finally(() => setLoading(false))
  }, [packageId])

  if (loading) return <p className={styles.dim}>Loading dashboard…</p>
  if (error) return <p className={styles.error}>{error}</p>
  if (!data) return <p className={styles.dim}>No data yet.</p>

  const compliancePct = data.delivery_compliance_rate != null
    ? `${(data.delivery_compliance_rate * 100).toFixed(1)}%`
    : '—'

  return (
    <div>
      <div className={styles.kpiGrid}>
        <KpiCard label="Total POs" value={data.total_pos} color="#1d4ed8" />
        <KpiCard label="Overdue Deliveries" value={data.overdue_deliveries} color={data.overdue_deliveries > 0 ? '#dc2626' : '#059669'} />
        <KpiCard label="At-Risk Materials" value={data.at_risk_materials} color={data.at_risk_materials > 0 ? '#d97706' : '#059669'} />
        <KpiCard label="CP Materials Delayed" value={data.cp_materials_delayed} color={data.cp_materials_delayed > 0 ? '#dc2626' : '#059669'} />
        <KpiCard label="Delivery Compliance" value={compliancePct} color="#059669" />
        <KpiCard label="Total GRNs" value={data.total_grns} />
        <KpiCard label="GRNs This Month" value={data.grns_this_month} color="#0891b2" />
        <KpiCard label="Material Links" value={data.total_material_links} color="#7c3aed" />
      </div>

      {data.pos_by_status && (
        <div className={styles.section}>
          <div className={styles.sectionTitle}>PO Status Breakdown</div>
          <div className={styles.chartWrap}>
            <StatusBar byStatus={data.pos_by_status} />
          </div>
        </div>
      )}
    </div>
  )
}
