import { useState, useEffect, useCallback, Fragment } from 'react'
import {
  listPOs, createPO, updatePO, deletePO,
  issuePO, acknowledgePO, dispatchPO, closePO,
  listPOLineItems, addPOLineItem, updatePOLineItem, deletePOLineItem,
} from '../../apis/procurementApi'
import ProcurementModal from './ProcurementModal'
import ProcurementBadge from './ProcurementBadge'
import styles from './POTab.module.css'

const BLANK_PO = { po_number: '', vendor_name: '', description: '', total_amount: 0, currency: 'INR', committed_delivery_date: '' }
const BLANK_ITEM = { item_code: '', description: '', unit: '', quantity: '', unit_rate: '' }
const STATUSES = ['', 'DRAFT', 'ISSUED', 'ACKNOWLEDGED', 'DISPATCHED', 'CLOSED']

export default function POTab({ packageId }) {
  const [pos, setPOs] = useState([])
  const [statusFilter, setStatusFilter] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const [showForm, setShowForm] = useState(false)
  const [editPO, setEditPO] = useState(null)
  const [form, setForm] = useState(BLANK_PO)

  const [expandedId, setExpandedId] = useState(null)
  const [lineItems, setLineItems] = useState({})
  const [showItemForm, setShowItemForm] = useState(null)
  const [itemForm, setItemForm] = useState(BLANK_ITEM)
  const [editItem, setEditItem] = useState(null)

  const load = useCallback(() => {
    setLoading(true)
    const params = statusFilter ? { status: statusFilter } : {}
    listPOs(packageId, params)
      .then(r => { setPOs(Array.isArray(r.data) ? r.data : []); setError(null) })
      .catch(e => setError(e.response?.data?.detail || 'Load failed'))
      .finally(() => setLoading(false))
  }, [packageId, statusFilter])

  useEffect(() => { load() }, [load])

  const loadItems = async (poId) => {
    const r = await listPOLineItems(poId)
    setLineItems(prev => ({ ...prev, [poId]: Array.isArray(r.data) ? r.data : [] }))
  }

  const toggleExpand = async (poId) => {
    if (expandedId === poId) { setExpandedId(null); return }
    setExpandedId(poId)
    await loadItems(poId)
  }

  const openCreate = () => { setForm(BLANK_PO); setEditPO(null); setShowForm(true) }
  const openEdit = (po) => {
    setForm({
      po_number: po.po_number, vendor_name: po.vendor_name, description: po.description || '',
      total_amount: po.total_amount, currency: po.currency,
      committed_delivery_date: po.committed_delivery_date || '',
    })
    setEditPO(po)
    setShowForm(true)
  }

  const handleSave = async () => {
    if (!form.po_number || !form.vendor_name) { setError('PO Number and Vendor Name are required'); return }
    try {
      const payload = { ...form, package_id: packageId, total_amount: parseFloat(form.total_amount) || 0 }
      if (!payload.committed_delivery_date) delete payload.committed_delivery_date
      if (editPO) await updatePO(editPO.id, payload)
      else await createPO(payload)
      setShowForm(false); setError(null); load()
    } catch (e) {
      setError(e.response?.data?.detail || 'Save failed')
    }
  }

  const handleDelete = async (po) => {
    if (!confirm(`Delete PO ${po.po_number}?`)) return
    try { await deletePO(po.id); load() } catch (e) { setError(e.response?.data?.detail || 'Delete failed') }
  }

  const handleTransition = async (po, action) => {
    try {
      const fn = { issue: issuePO, acknowledge: acknowledgePO, dispatch: dispatchPO, close: closePO }[action]
      await fn(po.id); load()
    } catch (e) { setError(e.response?.data?.detail || `${action} failed`) }
  }

  const openAddItem = (poId) => { setShowItemForm(poId); setItemForm(BLANK_ITEM); setEditItem(null) }
  const openEditItem = (poId, item) => {
    setShowItemForm(poId)
    setItemForm({ item_code: item.item_code, description: item.description, unit: item.unit, quantity: item.quantity, unit_rate: item.unit_rate })
    setEditItem(item)
  }

  const handleSaveItem = async (poId) => {
    if (!itemForm.item_code || !itemForm.description || !itemForm.unit) { setError('Item code, description and unit are required'); return }
    const payload = { ...itemForm, quantity: parseFloat(itemForm.quantity) || 0, unit_rate: parseFloat(itemForm.unit_rate) || 0 }
    try {
      if (editItem) await updatePOLineItem(poId, editItem.id, payload)
      else await addPOLineItem(poId, payload)
      setShowItemForm(null); setEditItem(null); await loadItems(poId); load()
    } catch (e) { setError(e.response?.data?.detail || 'Save failed') }
  }

  const handleDeleteItem = async (poId, item) => {
    if (!confirm(`Delete item "${item.item_code}"?`)) return
    try { await deletePOLineItem(poId, item.id); await loadItems(poId); load() } catch (e) { setError(e.response?.data?.detail || 'Delete failed') }
  }

  const today = new Date().toISOString().slice(0, 10)
  const overdue = pos.filter(p => p.is_overdue).length
  const issued = pos.filter(p => p.status === 'ISSUED').length
  const dispatched = pos.filter(p => p.status === 'DISPATCHED').length

  return (
    <div>
      {/* Toolbar */}
      <div className={styles.toolbar}>
        <span className={styles.toolbarTitle}>PO Register <span className={styles.count}>{pos.length}</span></span>
        <select className={styles.filterSel} value={statusFilter} onChange={e => setStatusFilter(e.target.value)}>
          {STATUSES.map(s => <option key={s} value={s}>{s || 'All Statuses'}</option>)}
        </select>
        <button className={styles.addBtn} onClick={openCreate}>+ New PO</button>
      </div>

      {/* Stats bar */}
      <div className={styles.statsBar}>
        <div className={`${styles.stat} ${styles.statBlue}`}><div className={styles.statVal}>{pos.length}</div><div className={styles.statLabel}>Total</div></div>
        <div className={styles.stat}><div className={styles.statVal}>{issued}</div><div className={styles.statLabel}>Issued</div></div>
        <div className={`${styles.stat} ${styles.statAmber}`}><div className={styles.statVal}>{dispatched}</div><div className={styles.statLabel}>Dispatched</div></div>
        <div className={`${styles.stat} ${overdue > 0 ? styles.statRed : ''}`}><div className={styles.statVal}>{overdue}</div><div className={styles.statLabel}>Overdue</div></div>
      </div>

      {error && <p className={styles.error}>{error}</p>}

      {/* Create/Edit Modal */}
      {showForm && (
        <ProcurementModal
          title={editPO ? 'Edit Purchase Order' : 'New Purchase Order'}
          sub={editPO?.po_number}
          icon="📦"
          onClose={() => setShowForm(false)}
          footer={
            <>
              <button className={styles.cancelBtn} onClick={() => setShowForm(false)}>Cancel</button>
              <button className={styles.submitBtn} onClick={handleSave}>{editPO ? 'Update' : 'Create'}</button>
            </>
          }
        >
          <div className={styles.formGrid}>
            <div className={styles.fieldGroup}>
              <label className={styles.label}>PO Number *</label>
              <input className={styles.input} value={form.po_number} onChange={e => setForm(f => ({ ...f, po_number: e.target.value }))} placeholder="PO-2025-001" />
            </div>
            <div className={styles.fieldGroup}>
              <label className={styles.label}>Vendor Name *</label>
              <input className={styles.input} value={form.vendor_name} onChange={e => setForm(f => ({ ...f, vendor_name: e.target.value }))} placeholder="Vendor name" />
            </div>
            <div className={styles.fieldGroup}>
              <label className={styles.label}>Total Amount</label>
              <input className={styles.input} type="number" value={form.total_amount} onChange={e => setForm(f => ({ ...f, total_amount: e.target.value }))} />
            </div>
            <div className={styles.fieldGroup}>
              <label className={styles.label}>Currency</label>
              <input className={styles.input} value={form.currency} onChange={e => setForm(f => ({ ...f, currency: e.target.value }))} />
            </div>
            <div className={styles.fieldGroup}>
              <label className={styles.label}>Committed Delivery Date</label>
              <input className={styles.input} type="date" value={form.committed_delivery_date} onChange={e => setForm(f => ({ ...f, committed_delivery_date: e.target.value }))} />
            </div>
            <div className={`${styles.fieldGroup} ${styles.colSpan2}`}>
              <label className={styles.label}>Description</label>
              <textarea className={styles.textarea} value={form.description} onChange={e => setForm(f => ({ ...f, description: e.target.value }))} rows={2} />
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
                <th></th>
                <th>PO Number</th>
                <th>Vendor</th>
                <th>Description</th>
                <th>Amount</th>
                <th>Status</th>
                <th>Delivery Date</th>
                <th>Overdue</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {pos.length === 0 && (
                <tr><td colSpan={9} className={styles.empty}>No purchase orders found.</td></tr>
              )}
              {pos.map(po => (
                <Fragment key={po.id}>
                  <tr className={po.is_overdue ? styles.rowOverdue : ''}>
                    <td>
                      <button className={styles.expandBtn} onClick={() => toggleExpand(po.id)}>
                        {expandedId === po.id ? '▲' : '▶'}
                      </button>
                    </td>
                    <td className={styles.monoCell}>{po.po_number}</td>
                    <td>{po.vendor_name}</td>
                    <td className={styles.descCell}>{po.description || '—'}</td>
                    <td className={styles.amtCell}>{po.currency} {Number(po.total_amount).toLocaleString()}</td>
                    <td><ProcurementBadge status={po.status} type="po" /></td>
                    <td>{po.committed_delivery_date || '—'}</td>
                    <td>{po.is_overdue ? <ProcurementBadge status="OVERDUE" type="ml" /> : <span className={styles.onTrack}>—</span>}</td>
                    <td>
                      <div className={styles.actions}>
                        <button className={styles.actionBtn} onClick={() => openEdit(po)}>Edit</button>
                        {po.status === 'DRAFT' && <button className={styles.actionBtn} onClick={() => handleTransition(po, 'issue')}>Issue</button>}
                        {(po.status === 'DRAFT' || po.status === 'ISSUED') && <button className={styles.actionBtn} onClick={() => handleTransition(po, 'acknowledge')}>Acknowledge</button>}
                        {po.status === 'ACKNOWLEDGED' && <button className={styles.actionBtn} onClick={() => handleTransition(po, 'dispatch')}>Dispatch</button>}
                        {po.status !== 'CLOSED' && <button className={styles.actionBtnSec} onClick={() => handleTransition(po, 'close')}>Close</button>}
                        <button className={styles.dangerBtn} onClick={() => handleDelete(po)}>Del</button>
                      </div>
                    </td>
                  </tr>

                  {/* Expanded line items panel */}
                  {expandedId === po.id && (
                    <tr>
                      <td colSpan={9} className={styles.expandPanel}>
                        <div className={styles.expandHeader}>
                          <span>Line Items — {po.po_number}</span>
                          <button className={styles.addBtn} onClick={() => openAddItem(po.id)}>+ Add Item</button>
                        </div>

                        {/* Add/Edit item form */}
                        {showItemForm === po.id && (
                          <div className={styles.itemFormWrap}>
                            <div className={styles.formGrid3}>
                              <div className={styles.fieldGroup}>
                                <label className={styles.label}>Item Code *</label>
                                <input className={styles.input} value={itemForm.item_code} onChange={e => setItemForm(f => ({ ...f, item_code: e.target.value }))} />
                              </div>
                              <div className={`${styles.fieldGroup} ${styles.colSpan2}`}>
                                <label className={styles.label}>Description *</label>
                                <input className={styles.input} value={itemForm.description} onChange={e => setItemForm(f => ({ ...f, description: e.target.value }))} />
                              </div>
                              <div className={styles.fieldGroup}>
                                <label className={styles.label}>Unit *</label>
                                <input className={styles.input} value={itemForm.unit} onChange={e => setItemForm(f => ({ ...f, unit: e.target.value }))} placeholder="MT, m³, nos…" />
                              </div>
                              <div className={styles.fieldGroup}>
                                <label className={styles.label}>Quantity</label>
                                <input className={styles.input} type="number" value={itemForm.quantity} onChange={e => setItemForm(f => ({ ...f, quantity: e.target.value }))} />
                              </div>
                              <div className={styles.fieldGroup}>
                                <label className={styles.label}>Unit Rate</label>
                                <input className={styles.input} type="number" value={itemForm.unit_rate} onChange={e => setItemForm(f => ({ ...f, unit_rate: e.target.value }))} />
                              </div>
                            </div>
                            <div className={styles.itemFormActions}>
                              <button className={styles.cancelBtn} onClick={() => { setShowItemForm(null); setEditItem(null) }}>Cancel</button>
                              <button className={styles.submitBtn} onClick={() => handleSaveItem(po.id)}>{editItem ? 'Update' : 'Add'}</button>
                            </div>
                          </div>
                        )}

                        {/* Sub table */}
                        <table className={styles.subTable}>
                          <thead>
                            <tr>
                              <th>Item Code</th>
                              <th>Description</th>
                              <th>Unit</th>
                              <th>Qty</th>
                              <th>Unit Rate</th>
                              <th>Amount</th>
                              <th>Actions</th>
                            </tr>
                          </thead>
                          <tbody>
                            {(lineItems[po.id] || []).length === 0 && (
                              <tr><td colSpan={7} className={styles.empty}>No line items yet.</td></tr>
                            )}
                            {(lineItems[po.id] || []).map(item => (
                              <tr key={item.id}>
                                <td className={styles.monoCell}>{item.item_code}</td>
                                <td>{item.description}</td>
                                <td>{item.unit}</td>
                                <td>{Number(item.quantity).toLocaleString()}</td>
                                <td>{Number(item.unit_rate).toLocaleString()}</td>
                                <td className={styles.amtCell}>{Number(item.amount).toLocaleString()}</td>
                                <td>
                                  <div className={styles.actions}>
                                    <button className={styles.actionBtn} onClick={() => openEditItem(po.id, item)}>Edit</button>
                                    <button className={styles.dangerBtn} onClick={() => handleDeleteItem(po.id, item)}>Del</button>
                                  </div>
                                </td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </td>
                    </tr>
                  )}
                </Fragment>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
