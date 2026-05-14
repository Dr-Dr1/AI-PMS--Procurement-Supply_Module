import { createContext, useContext, useEffect, useState, useCallback } from 'react'
import { getMe, listPersonas } from '../apis/identityApi'

const UserContext = createContext({
  me: null,
  personas: [],
  loading: false,
  error: null,
  setPersonId: () => {},
  clearPerson: () => {},
})

const STORAGE_KEY = 'aipms.personaId'

export function UserProvider({ children }) {
  const [personId, setPersonIdState] = useState(
    () => localStorage.getItem(STORAGE_KEY) || null,
  )
  const [me, setMe] = useState(null)
  const [personas, setPersonas] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  // Load personas list once
  useEffect(() => {
    listPersonas()
      .then(({ data }) => setPersonas(data || []))
      .catch(err => setError(err.message || 'Failed to load personas'))
  }, [])

  // Load /me whenever personId changes
  useEffect(() => {
    if (!personId) {
      setMe(null)
      return
    }
    setLoading(true)
    getMe()
      .then(({ data }) => {
        setMe(data)
        setError(null)
      })
      .catch(err => {
        setMe(null)
        setError(err.response?.data?.detail || err.message || 'Failed to load user')
      })
      .finally(() => setLoading(false))
  }, [personId])

  const setPersonId = useCallback((id) => {
    if (id) {
      localStorage.setItem(STORAGE_KEY, id)
    } else {
      localStorage.removeItem(STORAGE_KEY)
    }
    setPersonIdState(id)
  }, [])

  const clearPerson = useCallback(() => setPersonId(null), [setPersonId])

  return (
    <UserContext.Provider value={{ me, personas, loading, error, setPersonId, clearPerson }}>
      {children}
    </UserContext.Provider>
  )
}

export function useUser() {
  return useContext(UserContext)
}
