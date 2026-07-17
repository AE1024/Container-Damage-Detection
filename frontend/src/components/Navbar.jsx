import { useAuth, useToast } from '../App'
import { api } from '../api'
import styles from './Navbar.module.css'

const TABS = [
  { key: 'analyze',            label: 'Hasar Analizi',      Icon: IconAnalyze },
  { key: 'register-container', label: 'Konteyner Kayıt',    Icon: IconPlus },
  { key: 'list',               label: 'Konteyner Listesi',  Icon: IconList },
]

export default function Navbar({ activeTab, onTabChange }) {
  const { user, logout } = useAuth()
  const { showToast }    = useToast()

  async function handleLogout() {
    try { await api.logout() } catch { /* token expired is fine */ }
    logout()
    showToast('Oturum sonlandırıldı.', 'info')
  }

  const initials = user?.full_name
    ? user.full_name.split(' ').map(w => w[0]).join('').toUpperCase().slice(0, 2)
    : '?'

  return (
    <nav className={styles.nav}>
      {/* Brand */}
      <div className={styles.brand}>
        <div className={styles.brandIcon}>
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} width={16} height={16}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M20 7H4a2 2 0 00-2 2v10a2 2 0 002 2h16a2 2 0 002-2V9a2 2 0 00-2-2z"/>
            <path strokeLinecap="round" strokeLinejoin="round" d="M16 21V5a2 2 0 00-2-2h-4a2 2 0 00-2 2v16"/>
          </svg>
        </div>
        <span className={styles.brandName}>ContainerGuard</span>
      </div>

      {/* Tabs */}
      <div className={styles.pills}>
        {TABS.map(({ key, label, Icon }) => (
          <button
            key={key}
            className={`${styles.tab} ${activeTab === key ? styles.active : ''}`}
            onClick={() => onTabChange(key)}
          >
            <Icon />
            <span>{label}</span>
          </button>
        ))}
      </div>

      {/* User */}
      <div className={styles.user}>
        <div className={styles.avatar}>{initials}</div>
        <div className={styles.userInfo}>
          <span className={styles.userName}>{user?.full_name}</span>
          <span className={styles.userCompany}>{user?.company}</span>
        </div>
        <span className={`chip ${styles.roleBadge} ${user?.role === 'admin' ? 'chip-lavender' : 'chip-mist'}`}>
          {user?.role}
        </span>
        <button className="btn btn-ghost sm" onClick={handleLogout}>Çıkış</button>
      </div>
    </nav>
  )
}

function IconAnalyze() {
  return (
    <svg viewBox="0 0 20 20" fill="currentColor" width={14} height={14}>
      <path fillRule="evenodd" d="M4 3a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V5a2 2 0 00-2-2H4zm12 12H4l4-8 3 6 2-4 3 6z" clipRule="evenodd"/>
    </svg>
  )
}
function IconPlus() {
  return (
    <svg viewBox="0 0 20 20" fill="currentColor" width={14} height={14}>
      <path fillRule="evenodd" d="M10 3a1 1 0 011 1v5h5a1 1 0 110 2h-5v5a1 1 0 11-2 0v-5H4a1 1 0 110-2h5V4a1 1 0 011-1z" clipRule="evenodd"/>
    </svg>
  )
}
function IconList() {
  return (
    <svg viewBox="0 0 20 20" fill="currentColor" width={14} height={14}>
      <path fillRule="evenodd" d="M3 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1z" clipRule="evenodd"/>
    </svg>
  )
}
