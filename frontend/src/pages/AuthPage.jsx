import { useState } from 'react'
import { useAuth, useToast } from '../App'
import { api } from '../api'
import styles from './AuthPage.module.css'

export default function AuthPage() {
  const [activeTab,      setActiveTab]      = useState('login')
  const [loginErr,       setLoginErr]       = useState('')
  const [regErr,         setRegErr]         = useState('')
  const [regOk,          setRegOk]          = useState('')
  const [loading,        setLoading]        = useState(false)
  const [showLoginPwd,   setShowLoginPwd]   = useState(false)
  const [showRegPwd,     setShowRegPwd]     = useState(false)

  const [username,       setUsername]       = useState('')
  const [usernameStatus, setUsernameStatus] = useState('idle') // idle | checking | available | taken | invalid

  const { login }     = useAuth()
  const { showToast } = useToast()

  async function handleUsernameBlur() {
    if (!username) { setUsernameStatus('idle'); return }
    if (username.length < 3 || !/^[a-z0-9_]+$/.test(username)) {
      setUsernameStatus('invalid')
      return
    }
    setUsernameStatus('checking')
    try {
      const res = await api.checkUsername(username)
      setUsernameStatus(res.available ? 'available' : 'taken')
    } catch {
      setUsernameStatus('idle')
    }
  }

  function resetTabs() {
    setLoginErr(''); setRegErr(''); setRegOk('')
    setUsername(''); setUsernameStatus('idle')
  }

  async function handleLogin(e) {
    e.preventDefault()
    setLoginErr('')
    setLoading(true)
    const fd = new FormData(e.target)
    try {
      const data = await api.login({
        username:   fd.get('username').trim(),
        first_name: fd.get('first_name').trim(),
        last_name:  fd.get('last_name').trim(),
        password:   fd.get('password'),
      })
      login(data.access_token, {
        full_name: data.full_name,
        role: data.role,
        company: data.company,
        username: data.username,
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
    if (usernameStatus === 'taken') {
      setRegErr('Bu kullanıcı adı zaten alınmış.')
      return
    }
    if (usernameStatus !== 'available') {
      setRegErr('Lütfen geçerli ve müsait bir kullanıcı adı girin.')
      return
    }
    setLoading(true)
    const fd = new FormData(e.target)
    try {
      const data = await api.register({
        first_name: fd.get('first_name').trim(),
        last_name:  fd.get('last_name').trim(),
        username:   username.trim().toLowerCase(),
        company:    fd.get('company').trim(),
        password:   fd.get('password'),
      })
      login(data.access_token, {
        full_name: data.full_name,
        role:      data.role,
        company:   data.company,
        username:  data.username,
      })
      showToast(`Hoş geldiniz, ${data.full_name}! Hesabınız oluşturuldu.`, 'success')
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
            onClick={() => { setActiveTab('login'); resetTabs() }}
          >
            Giriş Yap
          </button>
          <button
            className={`${styles.tab} ${activeTab === 'register' ? styles.active : ''}`}
            onClick={() => { setActiveTab('register'); resetTabs() }}
          >
            Kayıt Ol
          </button>
        </div>

        {/* Login Form */}
        {activeTab === 'login' && (
          <form className={styles.form} onSubmit={handleLogin}>
            <div className="field-row">
              <div className="field">
                <label>Ad <span className="hint">opsiyonel</span></label>
                <input name="first_name" type="text" placeholder="Adınız" />
              </div>
              <div className="field">
                <label>Soyad <span className="hint">opsiyonel</span></label>
                <input name="last_name" type="text" placeholder="Soyadınız" />
              </div>
            </div>
            <div className="field">
              <label>Kullanıcı Adı</label>
              <input name="username" type="text" placeholder="kullanici_adi" required autoComplete="username" />
            </div>
            <div className="field">
              <label>Şifre</label>
              <div className={styles.pwdWrap}>
                <input name="password" type={showLoginPwd ? 'text' : 'password'} placeholder="••••••" required />
                <button type="button" className={styles.pwdToggle} onClick={() => setShowLoginPwd(v => !v)}>
                  {showLoginPwd ? <EyeOffIcon /> : <EyeIcon />}
                </button>
              </div>
            </div>
            {loginErr && <div className="form-alert error">{loginErr}</div>}
            <button type="submit" className="btn btn-primary full" disabled={loading}>
              {loading
                ? <><span className="spinner" style={{borderTopColor:'#fff',borderColor:'rgba(255,255,255,.3)'}} /> Giriş yapılıyor...</>
                : 'Giriş Yap'}
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

            {/* Username field with live check */}
            <div className="field">
              <label>
                Kullanıcı Adı
                <span className="hint">Benzersiz, harf/rakam/_</span>
              </label>
              <div className={styles.usernameWrap}>
                <input
                  name="username"
                  type="text"
                  placeholder="kullanici_adi"
                  required
                  autoComplete="off"
                  value={username}
                  onChange={e => { setUsername(e.target.value.toLowerCase().replace(/[^a-z0-9_]/g, '')); setUsernameStatus('idle') }}
                  onBlur={handleUsernameBlur}
                  className={
                    usernameStatus === 'available' ? styles.inputValid :
                    usernameStatus === 'taken' || usernameStatus === 'invalid' ? styles.inputError : ''
                  }
                />
                <span className={styles.usernameIcon}>
                  {usernameStatus === 'checking' && (
                    <span className="spinner" style={{width:16,height:16,borderTopColor:'#2563eb',borderColor:'rgba(37,99,235,.2)'}} />
                  )}
                  {usernameStatus === 'available' && <CheckIcon />}
                  {usernameStatus === 'taken'     && <XIcon color="#ff3e00" />}
                  {usernameStatus === 'invalid'   && <XIcon color="#ff3e00" />}
                </span>
              </div>
              {usernameStatus === 'taken'   && <span className={styles.usernameMsg + ' ' + styles.usernameMsgError}>Bu kullanıcı adı zaten alınmış.</span>}
              {usernameStatus === 'invalid' && <span className={styles.usernameMsg + ' ' + styles.usernameMsgError}>En az 3 karakter; harf, rakam ve _ kullanın.</span>}
              {usernameStatus === 'available' && <span className={styles.usernameMsg + ' ' + styles.usernameMsgOk}>Kullanıcı adı müsait!</span>}
            </div>

            <div className="field">
              <label>Şirket</label>
              <input name="company" type="text" placeholder="Şirket adı" required />
            </div>
            <div className="field">
              <label>Şifre <span className="hint">En az 6 karakter</span></label>
              <div className={styles.pwdWrap}>
                <input name="password" type={showRegPwd ? 'text' : 'password'} placeholder="••••••" minLength={6} required />
                <button type="button" className={styles.pwdToggle} onClick={() => setShowRegPwd(v => !v)}>
                  {showRegPwd ? <EyeOffIcon /> : <EyeIcon />}
                </button>
              </div>
            </div>
            {regErr && <div className="form-alert error">{regErr}</div>}
            {regOk  && <div className="form-alert success">{regOk}</div>}
            <button type="submit" className="btn btn-primary full" disabled={loading || usernameStatus === 'checking' || usernameStatus === 'taken' || usernameStatus === 'invalid'}>
              {loading
                ? <><span className="spinner" style={{borderTopColor:'#fff',borderColor:'rgba(255,255,255,.3)'}} /> Kayıt yapılıyor...</>
                : 'Kayıt Ol'}
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

function CheckIcon() {
  return (
    <svg viewBox="0 0 20 20" fill="none" width={18} height={18}>
      <circle cx="10" cy="10" r="9" fill="#22c55e" />
      <path d="M6 10l3 3 5-5" stroke="#fff" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  )
}

function XIcon({ color }) {
  return (
    <svg viewBox="0 0 20 20" fill="none" width={18} height={18}>
      <circle cx="10" cy="10" r="9" fill={color} />
      <path d="M7 7l6 6M13 7l-6 6" stroke="#fff" strokeWidth={2} strokeLinecap="round" />
    </svg>
  )
}

function EyeIcon() {
  return (
    <svg viewBox="0 0 20 20" fill="none" stroke="currentColor" strokeWidth={1.6} width={18} height={18}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M1 10s3.5-6 9-6 9 6 9 6-3.5 6-9 6-9-6-9-6z"/>
      <circle cx="10" cy="10" r="2.5" strokeLinecap="round"/>
    </svg>
  )
}

function EyeOffIcon() {
  return (
    <svg viewBox="0 0 20 20" fill="none" stroke="currentColor" strokeWidth={1.6} width={18} height={18}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M3 3l14 14M8.5 8.6A2.5 2.5 0 0011.4 11.5M6.2 6.3C3.9 7.6 2 10 2 10s3 5 8 5c1.5 0 2.8-.4 4-.9M10 5c4.4.3 7 5 7 5a13.5 13.5 0 01-2 2.5"/>
    </svg>
  )
}
