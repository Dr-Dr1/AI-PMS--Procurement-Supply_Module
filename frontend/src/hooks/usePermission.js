import { useUser } from '../context/UserContext'

export function useCanAccess(feature) {
  const { me } = useUser()
  if (!me) return false
  if (me.is_superadmin) return true
  if (Array.isArray(me.features) && me.features.includes('*')) return true
  return Array.isArray(me.features) && me.features.includes(feature)
}

export function useHasAnyFeature(features = []) {
  const { me } = useUser()
  if (!me) return false
  if (me.is_superadmin) return true
  if (Array.isArray(me.features) && me.features.includes('*')) return true
  return features.some(f => Array.isArray(me.features) && me.features.includes(f))
}

export function Gate({ feature, anyOf, children, fallback = null }) {
  const single = useCanAccess(feature || '__never__')
  const any = useHasAnyFeature(anyOf || [])
  const allowed = feature ? single : any
  return allowed ? children : fallback
}
