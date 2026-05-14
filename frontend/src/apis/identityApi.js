import { api } from './procurementApi'

export const listPersonas = () => api.get('/identity/personas')
export const getMe = () => api.get('/identity/me')
export const listRoles = () => api.get('/identity/roles')
export const getMyDashboard = (packageId) =>
  api.get('/procurement/dashboard/me', { params: packageId ? { package_id: packageId } : {} })
