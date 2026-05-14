import { UserProvider } from './context/UserContext'
import Procurement from './pages/procurement'
import './index.css'

export default function App() {
  return (
    <UserProvider>
      <Procurement />
    </UserProvider>
  )
}
