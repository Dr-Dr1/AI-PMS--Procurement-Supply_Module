import styles from './ProcurementModal.module.css'

export default function ProcurementModal({ title, sub, icon, onClose, children, footer, width = 640 }) {
  return (
    <div className={styles.overlay} onClick={e => e.target === e.currentTarget && onClose()}>
      <div className={styles.modal} style={{ width }}>
        <div className={styles.header}>
          <div className={styles.headerLeft}>
            <span className={styles.headerIcon}>{icon}</span>
            <div>
              <div className={styles.headerTitle}>{title}</div>
              {sub && <div className={styles.headerSub}>{sub}</div>}
            </div>
          </div>
          <button className={styles.closeBtn} onClick={onClose}>&#x2715; Close</button>
        </div>
        <div className={styles.body}>{children}</div>
        {footer && <div className={styles.footer}>{footer}</div>}
      </div>
    </div>
  )
}
