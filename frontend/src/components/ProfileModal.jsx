import { useState, useEffect, useRef } from 'react'
import { api } from '../api'
import { useAuth, useToast } from '../App'
import styles from './ProfileModal.module.css'

export default function ProfileModal({ onClose }) {
  const { user, setUser } = useAuth()
  const { showToast }     = useToast()

  const [profileLoading, setProfileLoading] = useState(false)
  const [passLoading,    setPassLoading]    = useState(false)

  const modalRef = useRef(null)

  useEffect(() => {
    function onKey(e) { if (e.key === 'Escape') onClose() }
    document.addEventListener('keydown', onKey)
    return () => document.removeEventListener('keydown', onKey)
  }, [onClose])

  function handleOverlayClick(e) {
    if (modalRef.current && !modalRef.current.contains(e.target)) onClose()
  }

  async function handleProfile(e) {
    e.preventDefault()
    const fd = new FormData(e.target)
    const body = {}
    const fn = fd.get('first_name').trim()
    const ln = fd.get('last_name').trim()
    const co = fd.get('company').trim()
    if (fn) body.first_name = fn
    if (ln) body.last_name  = ln
    if (co) body.company    = co

    if (!Object.keys(body).length) {
      showToast('En az bir alan doldurun.', 'error')
      return
    }

    setProfileLoading(true)
    try {
      await api.updateProfile(body)
      const newFirstName = body.first_name ?? user.full_name.split(' ')[0].toLowerCase()
      const newLastName  = body.last_name  ?? user.full_name.split(' ')[1]?.toLowerCase() ?? ''
      const newFullName  = `${cap(newFirstName)} ${cap(newLastName)}`.trim()
      const newCompany   = body.company ?? user.company

      const updated = { ...user, full_name: newFullName, company: newCompany }
      localStorage.setItem('cg_user', JSON.stringify(updated))
      setUser(updated)
      showToast('Profil güncellendi.', 'success')
      e.target.reset()
    } catch (err) {
      showToast(err.message, 'error')
    } finally {
      setProfileLoading(false)
    }
  }

  async function handlePassword(e) {
    e.preventDefault()
    const fd  = new FormData(e.target)
    const pwd = fd.get('password').trim()

    if (pwd.length < 6) {
      showToast('Şifre en az 6 karakter olmalıdır.', 'error')
      return
    }

    setPassLoading(true)
    try {
      await api.updateProfile({ password: pwd })
      showToast('Şifre güncellendi.', 'success')
      e.target.reset()
    } catch (err) {
      showToast(err.message, 'error')
    } finally {
      setPassLoading(false)
    }
  }

  const initials = user?.full_name
    ? user.full_name.split(' ').map(w => w[0]).join('').toUpperCase().slice(0, 2)
    : '?'

  return (
    <div className={styles.overlay} onMouseDown={handleOverlayClick}>
      <div className={styles.modal} ref={modalRef}>

        {/* Header */}
        <div className={styles.header}>
          <div className={styles.avatarLg}>{initials}</div>
          <div>
            <p className={styles.name}>{user?.full_name}</p>
            {user?.username && (
              <p className={styles.username}>@{user.username}</p>
            )}
            <p className={styles.meta}>{user?.company} · {user?.role}</p>
          </div>
          <button className={styles.closeBtn} onClick={onClose} aria-label="Kapat">
            <svg viewBox="0 0 20 20" fill="currentColor" width={16} height={16}>
              <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd"/>
            </svg>
          </button>
        </div>

        <div className={styles.divider} />

        {/* Profile section */}
        <section className={styles.section}>
          <p className={styles.sectionTitle}>Profil Bilgileri</p>
          <form onSubmit={handleProfile}>
            <div className={styles.row}>
              <div className="field">
                <label>Ad</label>
                <input name="first_name" type="text" placeholder={cap(user?.full_name?.split(' ')[0] ?? '')} />
              </div>
              <div className="field">
                <label>Soyad</label>
                <input name="last_name" type="text" placeholder={cap(user?.full_name?.split(' ')[1] ?? '')} />
              </div>
            </div>
            <div className="field" style={{ marginBottom: 16 }}>
              <label>Şirket</label>
              <input name="company" type="text" placeholder={user?.company ?? ''} />
            </div>
            <button className="btn btn-primary sm" type="submit" disabled={profileLoading}>
              {profileLoading
                ? <><span className="spinner" style={{ borderTopColor: '#fff', borderColor: 'rgba(255,255,255,.3)' }} />Kaydediliyor...</>
                : 'Güncelle'}
            </button>
          </form>
        </section>

        <div className={styles.divider} />

        {/* Password section */}
        <section className={styles.section}>
          <p className={styles.sectionTitle}>Şifre Değiştir</p>
          <form onSubmit={handlePassword}>
            <div className="field" style={{ marginBottom: 16 }}>
              <label>Yeni Şifre</label>
              <input name="password" type="password" placeholder="En az 6 karakter" required minLength={6} />
            </div>
            <button className="btn btn-primary sm" type="submit" disabled={passLoading}>
              {passLoading
                ? <><span className="spinner" style={{ borderTopColor: '#fff', borderColor: 'rgba(255,255,255,.3)' }} />Değiştiriliyor...</>
                : 'Şifreyi Değiştir'}
            </button>
          </form>
        </section>

      </div>
    </div>
  )
}

function cap(str = '') {
  return str.charAt(0).toUpperCase() + str.slice(1).toLowerCase()
}
