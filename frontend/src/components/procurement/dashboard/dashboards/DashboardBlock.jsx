import styles from './role-dashboard.module.css'

const INTENT_COLORS = {
  good: '#059669',
  warn: '#d97706',
  bad:  '#dc2626',
  neutral: '#1f2937',
}

export default function DashboardBlock({ block }) {
  return (
    <div className={styles.block}>
      <div className={styles.blockHeader}>
        <h4 className={styles.blockTitle}>{block.title}</h4>
        {block.drill_to && (
          <span className={styles.blockHint}>drill: {block.drill_to}</span>
        )}
      </div>
      <div className={styles.metricGrid}>
        {block.metrics.map((m, i) => (
          <div key={i} className={styles.metric}>
            <div
              className={styles.metricValue}
              style={{ color: INTENT_COLORS[m.intent] || INTENT_COLORS.neutral }}
            >
              {m.value ?? '—'}
            </div>
            <div className={styles.metricLabel}>{m.label}</div>
            {m.hint && <div className={styles.metricHint}>{m.hint}</div>}
          </div>
        ))}
      </div>
    </div>
  )
}
