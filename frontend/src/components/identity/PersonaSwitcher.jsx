import { useMemo } from 'react'
import { useUser } from '../../context/UserContext'
import styles from './PersonaSwitcher.module.css'

const ORG_ORDER = ['OWNER', 'CONTRACTOR', 'PMC', 'CLIENT', 'SUBCONTRACTOR', 'VENDOR', 'OEM', 'REGULATORY', 'TPI']

export default function PersonaSwitcher() {
  const { me, personas, setPersonId } = useUser()

  const grouped = useMemo(() => {
    const buckets = {}
    for (const p of personas) {
      const key = p.role_code === 'SUPERADMIN' ? 'SUPERADMIN' : p.org_type
      if (!buckets[key]) buckets[key] = []
      buckets[key].push(p)
    }
    const ordered = []
    if (buckets['SUPERADMIN']) ordered.push(['SUPERADMIN', buckets['SUPERADMIN']])
    for (const ot of ORG_ORDER) {
      if (buckets[ot]) ordered.push([ot, buckets[ot]])
    }
    return ordered
  }, [personas])

  const currentId = me?.person_id || ''

  return (
    <div className={styles.wrap}>
      <span className={styles.label}>Logged in as</span>
      <select
        className={styles.select}
        value={currentId}
        onChange={(e) => setPersonId(e.target.value)}
      >
        {!currentId && <option value="">— Select persona —</option>}
        {grouped.map(([group, items]) => (
          <optgroup key={group} label={group}>
            {items.map(p => (
              <option key={p.person_id} value={p.person_id}>
                {p.name} · {p.role_name} ({p.rbac_tier})
              </option>
            ))}
          </optgroup>
        ))}
      </select>
      {me && (
        <span className={styles.chip}>
          {me.is_superadmin && <span className={styles.superBadge}>SUPER</span>}
          <span className={styles.tierBadge}>{me.rbac_tier}</span>
          <span className={styles.orgBadge}>{me.org_type}</span>
        </span>
      )}
    </div>
  )
}
