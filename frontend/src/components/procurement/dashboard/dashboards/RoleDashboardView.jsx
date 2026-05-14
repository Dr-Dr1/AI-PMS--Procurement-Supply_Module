import { useEffect, useState } from 'react'
import { getMyDashboard } from '../../../../apis/identityApi'
import { useUser } from '../../../../context/UserContext'
import DashboardBlock from './DashboardBlock'
import styles from './role-dashboard.module.css'

export default function RoleDashboardView({ packageId, title, subtitle }) {
  const { me } = useUser()
  const [payload, setPayload] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  useEffect(() => {
    if (!me) return
    setLoading(true)
    setError(null)
    getMyDashboard(packageId)
      .then((res) => setPayload(res.data))
      .catch(err => setError(err.response?.data?.detail || err.message || 'Failed to load'))
      .finally(() => setLoading(false))
  }, [packageId, me?.person_id])

  if (loading) return <p className={styles.dim}>Loading dashboard…</p>
  if (error) return <p className={styles.error}>{error}</p>
  if (!payload || !payload.blocks?.length) {
    return <p className={styles.dim}>No data for this view yet.</p>
  }

  return (
    <div className={styles.wrap}>
      <header className={styles.header}>
        <h3 className={styles.title}>{title}</h3>
        <span className={styles.subtitle}>
          {subtitle || `${me?.role_name} · view: ${payload.view}`}
        </span>
      </header>
      <div className={styles.blockGrid}>
        {payload.blocks.map(b => <DashboardBlock key={b.key} block={b} />)}
      </div>
    </div>
  )
}
