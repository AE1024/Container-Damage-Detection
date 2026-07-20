import { useState } from 'react'
import { useAuth, useToast } from '../App'
import { api } from '../api'
import styles from './AuthPage.module.css'

export default function AuthPage() {
  const [activeTab, setActiveTab] = useState('login')
  const [loginErr,  setLoginErr]  = useState('')
  const [regErr,    setRegErr]    = useState('')
  const [regOk,     setRegOk]     = useState('')
  const [loading,   setLoading]   = useState(false)

  const { login }     = useAuth()
  const { showToast } = useToast()

  async function handleLogin(e) {
    e.preventDefault()
    setLoginErr('')
    setLoading(true)
    const fd = new FormData(e.target)
    try {
      const data = await api.login({
        first_name: fd.get('first_name').trim(),
        last_name:  fd.get('last_name').trim(),
        password: fd.get('password'),
      })
      login(data.access_token, {
        full_name: data.full_name,
        role: data.role,
        company: data.company,
      })
      showToast(`Hoş geldiniz, ${data.full_name}!`, 'success')
    } catch (err) {
      setLoginErr(err.message)
    } finally {
      setLoading(false)
    }
  }

  async function handleRegister(e) {
    e.preventDefault()
    setRegErr('')
    setRegOk('')
    setLoading(true)
    const fd = new FormData(e.target)
    try {
      const data = await api.register({
        first_name: fd.get('first_name').trim(),
        last_name:  fd.get('last_name').trim(),
        company:  fd.get('company').trim(),
        password: fd.get('password'),
      })
      setRegOk(data.message || 'Kayıt başarılı! Giriş yapabilirsiniz.')
      e.target.reset()
    } catch (err) {
      setRegErr(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className={styles.wrapper}>
      <div className={styles.card}>
        {/* Brand */}
        <div className={styles.brand}>
          <div className={styles.brandIcon}>
            <ContainerIcon />
          </div>
          <h1 className={styles.brandName}>ContainerGuard</h1>
          <p className={styles.brandSub}>Port Konteyner Takip Sistemi</p>
        </div>

        {/* Tabs */}
        <div className={styles.tabs}>
          <button
            className={`${styles.tab} ${activeTab === 'login' ? styles.active : ''}`}
            onClick={() => { setActiveTab('login'); setLoginErr(''); setRegErr(''); setRegOk(''); }}
          >
            Giriş Yap
          </button>
          <button
            className={`${styles.tab} ${activeTab === 'register' ? styles.active : ''}`}
            onClick={() => { setActiveTab('register'); setLoginErr(''); setRegErr(''); setRegOk(''); }}
          >
            Kayıt Ol
          </button>
        </div>

        {/* Login Form */}
        {activeTab === 'login' && (
          <form className={styles.form} onSubmit={handleLogin}>
            <div className="field-row">
              <div className="field">
                <label>Ad</label>
                <input name="first_name" type="text" placeholder="Adınız" required />
              </div>
              <div className="field">
                <label>Soyad</label>
                <input name="last_name" type="text" placeholder="Soyadınız" required />
              </div>
            </div>
            <div className="field">
              <label>Şifre</label>
              <input name="password" type="password" placeholder="••••••" required />
            </div>
            {loginErr && <div className="form-alert error">{loginErr}</div>}
            <button type="submit" className="btn btn-primary full" disabled={loading}>
              {loading ? <><span className="spinner" style={{borderTopColor:'#fff',borderColor:'rgba(255,255,255,.3)'}} /> Giriş yapılıyor...</> : 'Giriş Yap'}
            </button>
          </form>
        )}

        {/* Register Form */}
        {activeTab === 'register' && (
          <form className={styles.form} onSubmit={handleRegister}>
            <div className="field-row">
              <div className="field">
                <label>Ad</label>
                <input name="first_name" type="text" placeholder="Adınız" required />
              </div>
              <div className="field">
                <label>Soyad</label>
                <input name="last_name" type="text" placeholder="Soyadınız" required />
              </div>
            </div>
            <div className="field">
              <label>Şirket</label>
              <input name="company" type="text" placeholder="Şirket adı" required />
            </div>
            <div className="field">
              <label>Şifre <span className="hint">En az 6 karakter</span></label>
              <input name="password" type="password" placeholder="••••••" minLength={6} required />
            </div>
            {regErr && <div className="form-alert error">{regErr}</div>}
            {regOk  && <div className="form-alert success">{regOk}</div>}
            <button type="submit" className="btn btn-primary full" disabled={loading}>
              {loading ? <><span className="spinner" style={{borderTopColor:'#fff',borderColor:'rgba(255,255,255,.3)'}} /> Kayıt yapılıyor...</> : 'Kayıt Ol'}
            </button>
          </form>
        )}
      </div>
    </div>
  )
}

function ContainerIcon() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} width={28} height={28}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M20 7H4a2 2 0 00-2 2v10a2 2 0 002 2h16a2 2 0 002-2V9a2 2 0 00-2-2z"/>
      <path strokeLinecap="round" strokeLinejoin="round" d="M16 21V5a2 2 0 00-2-2h-4a2 2 0 00-2 2v16"/>
    </svg>
  )
}
