import styles from './ProcurementBadge.module.css'

const PO_COLORS = {
  DRAFT: '#6b7280',
  ISSUED: '#2563eb',
  ACKNOWLEDGED: '#7c3aed',
  DISPATCHED: '#d97706',
  CLOSED: '#10b981',
}

const GRN_COLORS = {
  PENDING: '#6b7280',
  ACCEPTED: '#059669',
  PARTIALLY_ACCEPTED: '#d97706',
  REJECTED: '#dc2626',
}

const RISK_COLORS = {
  LOW: '#059669',
  MEDIUM: '#d97706',
  HIGH: '#dc2626',
}

const ML_STATUS_COLORS = {
  ON_TRACK: '#059669',
  AT_RISK: '#d97706',
  OVERDUE: '#dc2626',
}

const MAP = { po: PO_COLORS, grn: GRN_COLORS, risk: RISK_COLORS, ml: ML_STATUS_COLORS }

export default function ProcurementBadge({ status, type = 'po' }) {
  if (!status) return null
  const color = (MAP[type] || {})[status] || '#6b7280'
  return (
    <span className={styles.badge} style={{ background: color + '20', color }}>
      {status.replace(/_/g, ' ')}
    </span>
  )
}
