import axios from 'axios'

export const api = axios.create({
  baseURL: `${import.meta.env.VITE_PROCUREMENT_API_URL}/api/v1`,
})

// Auto-attach X-User-ID from localStorage (set by PersonaSwitcher / UserContext).
api.interceptors.request.use((config) => {
  const personaId = localStorage.getItem('aipms.personaId')
  if (personaId) {
    config.headers = config.headers || {}
    if (!config.headers['X-User-ID']) {
      config.headers['X-User-ID'] = personaId
    }
  }
  return config
})

// ─── Schedule Read (dropdowns) ────────────────────────────────────────────────
export const getAllProjects = () => api.get('/projects')
export const getCorridorsByProject = (projId) => api.get('/corridors', { params: projId ? { proj_id: projId } : {} })
export const getPackagesByProject = () => api.get('/packages')
export const getActivitiesByPackage = (packageId) => api.get(`/activities/package/${packageId}`)

// ─── Purchase Orders ──────────────────────────────────────────────────────────
export const listPOs = (packageId, params = {}) =>
  api.get('/procurement/pos', { params: { package_id: packageId, ...params } })

export const createPO = (data) =>
  api.post('/procurement/pos', data)

export const getPO = (id) =>
  api.get(`/procurement/pos/${id}`)

export const updatePO = (id, data) =>
  api.patch(`/procurement/pos/${id}`, data)

export const deletePO = (id) =>
  api.delete(`/procurement/pos/${id}`)

export const issuePO = (id) =>
  api.post(`/procurement/pos/${id}/issue`)

export const acknowledgePO = (id) =>
  api.post(`/procurement/pos/${id}/acknowledge`)

export const dispatchPO = (id) =>
  api.post(`/procurement/pos/${id}/dispatch`)

export const closePO = (id) =>
  api.post(`/procurement/pos/${id}/close`)

// ─── PO Line Items ────────────────────────────────────────────────────────────
export const listPOLineItems = (poId) =>
  api.get(`/procurement/pos/${poId}/items`)

export const addPOLineItem = (poId, data) =>
  api.post(`/procurement/pos/${poId}/items`, data)

export const updatePOLineItem = (poId, itemId, data) =>
  api.patch(`/procurement/pos/${poId}/items/${itemId}`, data)

export const deletePOLineItem = (poId, itemId) =>
  api.delete(`/procurement/pos/${poId}/items/${itemId}`)

// ─── Goods Receipts (GRN) ─────────────────────────────────────────────────────
export const listGRNs = (packageId, params = {}) =>
  api.get('/procurement/grns', { params: { package_id: packageId, ...params } })

export const createGRN = (data) =>
  api.post('/procurement/grns', data)

export const getGRN = (id) =>
  api.get(`/procurement/grns/${id}`)

// ─── Material Links ────────────────────────────────────────────────────────────
export const listMaterialLinks = (packageId, params = {}) =>
  api.get('/procurement/material-links', { params: { package_id: packageId, ...params } })

export const createMaterialLink = (data) =>
  api.post('/procurement/material-links', data)

export const getMaterialLink = (id) =>
  api.get(`/procurement/material-links/${id}`)

export const updateMaterialLink = (id, data) =>
  api.patch(`/procurement/material-links/${id}`, data)

export const deleteMaterialLink = (id) =>
  api.delete(`/procurement/material-links/${id}`)

export const refreshLinkRisk = (id) =>
  api.post(`/procurement/material-links/${id}/refresh-risk`)

export const bulkRefreshRisk = (packageId) =>
  api.post('/procurement/material-links/bulk-refresh-risk', null, { params: { package_id: packageId } })

// ─── Dashboard ─────────────────────────────────────────────────────────────────
export const getProcurementDashboard = (packageId) =>
  api.get('/procurement/dashboard', { params: packageId ? { package_id: packageId } : {} })
