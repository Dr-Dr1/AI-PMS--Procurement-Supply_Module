import { useState, useEffect, useCallback } from 'react'
import { listGRNs, createGRN, listPOs } from '../../apis/procurementApi'
import ProcurementModal from './ProcurementModal'
import ProcurementBadge from './ProcurementBadge'
import styles from './GRNTab.module.css'

const BLANK_GRN = {
  po_id: '', grn_number: '', received_date: '', received_qty: '', ordered_qty: '',
  unit: '', status: 'ACCEPTED', test_certificate_ref: '', inspector: '', remarks: '',
}

const GRN_STATUSES = ['PENDING', 'ACCEPTED', 'PARTIALLY_ACCEPTED', 'REJECTED']

export default function GRNTab({ packageId }) {
  const [grns, setGRNs] = useState([])
  const [pos, setPOs] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [poFilter, setPoFilter] = useState('')
  const [dateFrom, setDateFrom] = useState('')
  const [dateTo, setDateTo] = useState('')
  const [showForm, setShowForm] = useState(false)
  const [form, setForm] = useState(BLANK_GRN)

  const load = useCallback(() => {
    setLoading(true)
    const params = {}
    if (poFilter) params.po_id = poFilter
    if (dateFrom) params.date_from = dateFrom
    if (dateTo) params.date_to = dateTo
    listGRNs(packageId, params)
      .then(r => { setGRNs(Array.isArray(r.data) ? r.data : []); setError(null) })
      .catch(e => setError(e.response?.data?.detail || 'Load failed'))
      .finally(() => setLoading(false))
  }, [packageId, poFilter, dateFrom, dateTo])

  useEffect(() => { load() }, [load])

  useEffect(() => {
    listPOs(packageId).then(r => setPOs(Array.isArray(r.data) ? r.data : [])).catch(() => {})
  }, [packageId])

  const handleSave = async () => {
    if (!form.po_id || !form.grn_number || !form.received_date || !form.unit) {
      setError('PO, GRN Number, Received Date and Unit are required'); return
    }
    try {
      const payload = {
        ...form,
        package_id: packageId,
        received_qty: parseFloat(form.received_qty) || 0,
        ordered_qty: form.ordered_qty ? parseFloat(form.ordered_qty) : null,
      }
      if (!payload.ordered_qty) delete payload.ordered_qty
      if (!payload.test_certificate_ref) delete payload.test_certificate_ref
      if (!payload.inspector) delete payload.inspector
      if (!payload.remarks) delete payload.remarks
      await createGRN(payload)
      setShowForm(false); setError(null); load()
    } catch (e) {
      setError(e.response?.data?.detail || 'Save failed')
    }
  }

  const today = new Date()
  const thisMonth = grns.filter(g => {
    if (!g.received_date) return false
    const d = new Date(g.received_date)
    return d.getMonth() === today.getMonth() && d.getFullYear() === today.getFullYear()
  }).length
  const withCert = grns.filter(g => g.test_certificate_ref).length
  const uniquePOs = new Set(grns.map(g => g.po_id).filter(Boolean)).size

  return (
    <div>
      {/* Toolbar */}
      <div className={styles.toolbar}>
        <span className={styles.toolbarTitle}>Deliveries <span className={styles.count}>{grns.length}</span></span>
        <select className={styles.filterSel} value={poFilter} onChange={e => setPoFilter(e.target.value)}>
          <option value="">All POs</option>
          {pos.map(p => <option key={p.id} value={p.id}>{p.po_number}</option>)}
        </select>
        <input type="date" className={styles.dateInput} value={dateFrom} onChange={e => setDateFrom(e.target.value)} title="Date from" />
        <input type="date" className={styles.dateInput} value={dateTo} onChange={e => setDateTo(e.target.value)} title="Date to" />
        <button className={styles.addBtn} onClick={() => { setForm(BLANK_GRN); setShowForm(true) }}>+ New GRN</button>
      </div>

      {/* Stats bar */}
      <div className={styles.statsBar}>
        <div className={`${styles.stat} ${styles.statBlue}`}><div className={styles.statVal}>{grns.length}</div><div className={styles.statLabel}>Total GRNs</div></div>
        <div className={`${styles.stat} ${styles.statAmber}`}><div className={styles.statVal}>{thisMonth}</div><div className={styles.statLabel}>This Month</div></div>
        <div className={`${styles.stat} ${styles.statGreen}`}><div className={styles.statVal}>{withCert}</div><div className={styles.statLabel}>With Test Cert</div></div>
        <div className={styles.stat}><div className={styles.statVal}>{uniquePOs}</div><div className={styles.statLabel}>Unique POs</div></div>
      </div>

      {error && <p className={styles.error}>{error}</p>}

      {/* Create Modal */}
      {showForm && (
        <ProcurementModal
          title="New Goods Receipt Note"
          icon="🚛"
          onClose={() => setShowForm(false)}
          width={680}
          footer={
            <>
              <button className={styles.cancelBtn} onClick={() => setShowForm(false)}>Cancel</button>
              <button className={styles.submitBtn} onClick={handleSave}>Create GRN</button>
            </>
          }
        >
          <div className={styles.formGrid}>
            <div className={styles.fieldGroup}>
              <label className={styles.label}>Purchase Order *</label>
              <select className={styles.input} value={form.po_id} onChange={e => setForm(f => ({ ...f, po_id: e.target.value }))}>
                <option value="">— select PO —</option>
                {pos.map(p => <option key={p.id} value={p.id}>{p.po_number} — {p.vendor_name}</option>)}
              </select>
            </div>
            <div className={styles.fieldGroup}>
              <label className={styles.label}>GRN Number *</label>
              <input className={styles.input} value={form.grn_number} onChange={e => setForm(f => ({ ...f, grn_number: e.target.value }))} placeholder="GRN-2025-001" />
            </div>
            <div className={styles.fieldGroup}>
              <label className={styles.label}>Received Date *</label>
              <input className={styles.input} type="date" value={form.received_date} onChange={e => setForm(f => ({ ...f, received_date: e.target.value }))} />
            </div>
            <div className={styles.fieldGroup}>
              <label className={styles.label}>Status</label>
              <select className={styles.input} value={form.status} onChange={e => setForm(f => ({ ...f, status: e.target.value }))}>
                {GRN_STATUSES.map(s => <option key={s} value={s}>{s.replace(/_/g, ' ')}</option>)}
              </select>
            </div>
            <div className={styles.fieldGroup}>
              <label className={styles.label}>Received Qty</label>
              <input className={styles.input} type="number" value={form.received_qty} onChange={e => setForm(f => ({ ...f, received_qty: e.target.value }))} />
            </div>
            <div className={styles.fieldGroup}>
              <label className={styles.label}>Ordered Qty</label>
              <input className={styles.input} type="number" value={form.ordered_qty} onChange={e => setForm(f => ({ ...f, ordered_qty: e.target.value }))} />
            </div>
            <div className={styles.fieldGroup}>
              <label className={styles.label}>Unit *</label>
              <input className={styles.input} value={form.unit} onChange={e => setForm(f => ({ ...f, unit: e.target.value }))} placeholder="MT, m³, nos…" />
            </div>
            <div className={styles.fieldGroup}>
              <label className={styles.label}>Inspector</label>
              <input className={styles.input} value={form.inspector} onChange={e => setForm(f => ({ ...f, inspector: e.target.value }))} />
            </div>
            <div className={`${styles.fieldGroup} ${styles.colSpan2}`}>
              <label className={styles.label}>Test Certificate Ref</label>
              <input className={styles.input} value={form.test_certificate_ref} onChange={e => setForm(f => ({ ...f, test_certificate_ref: e.target.value }))} placeholder="TC-2025-123" />
            </div>
            <div className={`${styles.fieldGroup} ${styles.colSpan2}`}>
              <label className={styles.label}>Remarks</label>
              <textarea className={styles.textarea} value={form.remarks} onChange={e => setForm(f => ({ ...f, remarks: e.target.value }))} rows={2} />
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
                <th>GRN Number</th>
                <th>PO Number</th>
                <th>Received Date</th>
                <th>Received Qty</th>
                <th>Unit</th>
                <th>Status</th>
                <th>Test Cert</th>
                <th>Inspector</th>
                <th>Remarks</th>
              </tr>
            </thead>
            <tbody>
              {grns.length === 0 && (
                <tr><td colSpan={9} className={styles.empty}>No goods receipts found.</td></tr>
              )}
              {grns.map(grn => {
                const po = pos.find(p => p.id === grn.po_id)
                return (
                  <tr key={grn.id}>
                    <td className={styles.monoCell}>{grn.grn_number}</td>
                    <td className={styles.monoCell}>{po?.po_number || grn.po_id?.slice(0, 8) + '…'}</td>
                    <td>{grn.received_date}</td>
                    <td>{Number(grn.received_qty).toLocaleString()}</td>
                    <td>{grn.unit}</td>
                    <td><ProcurementBadge status={grn.status} type="grn" /></td>
                    <td className={grn.test_certificate_ref ? styles.certCell : styles.noCert}>
                      {grn.test_certificate_ref || '—'}
                    </td>
                    <td>{grn.inspector || '—'}</td>
                    <td className={styles.remarksCell}>{grn.remarks || '—'}</td>
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
