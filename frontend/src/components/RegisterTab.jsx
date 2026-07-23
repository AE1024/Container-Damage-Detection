import { useState, useEffect, useRef } from 'react'
import { api } from '../api'
import { useToast } from '../App'
import styles from './RegisterTab.module.css'

const CONTAINER_TYPES = [
  'Kuru Yük', 'Soğutmalı', 'Açık Üst', 'Platform', 'Tank', 'Özel Amaçlı',
]

const COREX_PORTS = [
  'Gebze Terminali',
  'Körfez Terminali',
  'Ankara Terminali',
  'Marsaxlokk Terminali',
  'Takoradi Terminali',
  'Taranto Terminali',
  'Oslo Terminali',
  'Gävle Terminali',
  'Stockholm Nord Terminali',
  'Acajutla Terminali',
  'La Unión Terminali',
  'Paita Terminali',
  'Puerto Bolívar Terminali',
  'Puerto Quetzal Terminali',
  'Liscont Terminali',
  'Figueira Da Foz Terminali',
  'Sotagus Terminali',
  'Leixões Terminali',
  'Aveiro Terminali',
  'Setúbal Terminali',
  'Tersado Terminali',
  'Huelva Terminali',
  'Ferrol Terminali',
  'Elvas Terminali',
]

function getBicCompany(bicMap, containerNo) {
  if (!bicMap || !containerNo || containerNo.length < 4) return null
  const code = containerNo.slice(0, 4).toUpperCase()
  return bicMap[code] || null
}


export default function RegisterTab({ prefillContainerNo = '', prefillCompanyName = '', prefillKey = 0, onPrefillUsed }) {
  const [msg,         setMsg]         = useState(null)
  const [loading,     setLoading]     = useState(false)
  const [containerNo, setContainerNo] = useState(prefillContainerNo)
  const [companyName, setCompanyName] = useState(prefillCompanyName)
  const [bicMap,      setBicMap]      = useState({})
  const { showToast }                 = useToast()

  const [arrivePort, setArrivePort] = useState('')
  const [destPort,   setDestPort]   = useState('')
  const portSame = arrivePort && destPort && arrivePort === destPort

  // BIC tablosunu backend'den tek seferlik yükle
  const bicFetched = useRef(false)
  useEffect(() => {
    if (bicFetched.current) return
    bicFetched.current = true
    api.getBicMap().then(setBicMap).catch(() => {})
  }, [])

  const bicCompany = getBicCompany(bicMap, containerNo)
  const bicLocked  = !!bicCompany

  // BIC kodu tanındığında şirket adını otomatik doldur
  useEffect(() => {
    if (bicCompany) setCompanyName(bicCompany)
    else if (containerNo.length < 4) setCompanyName('')
  }, [bicCompany])

  useEffect(() => {
    if (prefillKey === 0) return
    setContainerNo(prefillContainerNo)
    setCompanyName(prefillCompanyName)
  }, [prefillKey])

  const isAutofilled = !!(prefillContainerNo || prefillCompanyName)

  async function handleSubmit(e) {
    e.preventDefault()
    setMsg(null)
    setLoading(true)
    const fd = new FormData(e.target)
    const body = {
      container_no:     (fd.get('container_no') || '').toUpperCase().replace(/\s/g, ''),
      container_type:   fd.get('container_type'),
      company_name:     (fd.get('company_name') || '').toLocaleUpperCase('en-US'),
      arrive_port:      fd.get('arrive_port'),
      destination_port: fd.get('destination_port'),
    }
    try {
      await api.registerContainer(body)
      setMsg({ type: 'success', text: `${body.container_no} başarıyla kayıt edildi.` })
      showToast('Konteyner kayıt edildi.', 'success')
      e.target.reset()
      setContainerNo('')
      setCompanyName('')
      onPrefillUsed?.()
    } catch (err) {
      setMsg({ type: 'error', text: err.message })
    } finally {
      setLoading(false)
    }
  }

  return (
    <div>
      <div className={styles.header}>
        <div>
          <h2 className={styles.title}>Konteyner Kayıt</h2>
          <p className={styles.sub}>Yeni konteyner bilgilerini sisteme ekleyin</p>
        </div>
      </div>

      <div className={styles.card}>
        <form onSubmit={handleSubmit} onReset={() => { setMsg(null); setContainerNo(''); setCompanyName(''); setArrivePort(''); setDestPort('') }}>
          {isAutofilled && (
            <div className={styles.autofillBanner}>
              <span>⚡ Hasar analizinden otomatik dolduruldu — geri kalan alanları tamamlayın.</span>
            </div>
          )}

          <div className={styles.grid}>
            {/* Konteyner No */}
            <div className="field">
              <label>
                Konteyner No
                <span className="hint">4 harf + 7 rakam</span>
              </label>
              <input
                name="container_no"
                type="text"
                placeholder="MSCU1234567"
                maxLength={11}
                required
                value={containerNo}
                onChange={e => {
                  const raw = e.target.value.toUpperCase().replace(/\s/g, '')
                  // İlk 4: sadece harf, sonraki 7: sadece rakam
                  const letters = raw.slice(0, 4).replace(/[^A-Z]/g, '')
                  const digits  = raw.slice(4).replace(/[^0-9]/g, '').slice(0, 7)
                  setContainerNo(letters + digits)
                }}
                style={{
                  textTransform: 'uppercase',
                  fontFamily: 'monospace',
                  borderColor: prefillContainerNo ? 'var(--c-lavender)' : undefined,
                  boxShadow: prefillContainerNo ? '0 0 0 2px rgba(99,102,241,.15)' : undefined,
                }}
              />
              {bicCompany && (
                <span className={styles.bicHint}>
                  <BicIcon /> BIC tanındı — şirket otomatik dolduruldu.
                </span>
              )}
            </div>

            {/* Konteyner Tipi */}
            <div className="field">
              <label>Konteyner Tipi</label>
              <select name="container_type" required>
                <option value="">Seçiniz</option>
                {CONTAINER_TYPES.map(t => (
                  <option key={t} value={t}>{t}</option>
                ))}
              </select>
            </div>

            {/* Şirket Adı */}
            <div className="field">
              <label>
                Şirket Adı
                {bicLocked && <span className="hint">BIC'ten otomatik</span>}
              </label>
              <input
                name="company_name"
                type="text"
                placeholder="MAERSK LINE"
                required
                value={companyName}
                onChange={e => { if (!bicLocked) setCompanyName(e.target.value.toUpperCase()) }}
                readOnly={bicLocked}
                style={{
                  background: bicLocked ? '#f0f4ff' : undefined,
                  color: bicLocked ? 'var(--c-lavender)' : undefined,
                  cursor: bicLocked ? 'not-allowed' : undefined,
                  borderColor: bicLocked ? 'var(--c-lavender)' : prefillCompanyName ? 'var(--c-lavender)' : undefined,
                  boxShadow: bicLocked ? '0 0 0 2px rgba(37,99,235,.12)' : prefillCompanyName ? '0 0 0 2px rgba(99,102,241,.15)' : undefined,
                }}
              />
              {!bicLocked && !bicCompany && containerNo.length >= 4 && (
                <span className={styles.bicWarn}>BIC kodu tanınmıyor — şirket adını manuel girin.</span>
              )}
            </div>

            {/* Geliş Limanı — CoreX dropdown */}
            <div className="field">
              <label>Geliş Limanı</label>
              <select name="arrive_port" required value={arrivePort} onChange={e => setArrivePort(e.target.value)}
                style={{ borderColor: portSame ? '#ff3e00' : undefined, boxShadow: portSame ? '0 0 0 3px rgba(255,62,0,.12)' : undefined }}>
                <option value="">Seçiniz</option>
                {COREX_PORTS.map(p => (
                  <option key={p} value={p}>{p}</option>
                ))}
              </select>
            </div>

            {/* Varış Limanı — CoreX dropdown */}
            <div className="field">
              <label>Varış Limanı</label>
              <select name="destination_port" required value={destPort} onChange={e => setDestPort(e.target.value)}
                style={{ borderColor: portSame ? '#ff3e00' : undefined, boxShadow: portSame ? '0 0 0 3px rgba(255,62,0,.12)' : undefined }}>
                <option value="">Seçiniz</option>
                {COREX_PORTS.map(p => (
                  <option key={p} value={p}>{p}</option>
                ))}
              </select>
              {portSame && <span className={styles.bicWarn}>⚠ Geliş ve varış limanı aynı olamaz.</span>}
            </div>
          </div>

          {msg && (
            <div className={`form-alert ${msg.type}`} style={{ marginBottom: '20px' }}>
              {msg.text}
            </div>
          )}

          <div className={styles.actions}>
            <button type="submit" className="btn btn-primary" disabled={loading || !!portSame}>
              {loading
                ? <><span className="spinner" style={{borderTopColor:'#fff',borderColor:'rgba(255,255,255,.3)'}} />Kaydediliyor...</>
                : <><PlusIcon />Konteyner Kaydet</>
              }
            </button>
            <button type="reset" className="btn btn-ghost">Formu Temizle</button>
          </div>
        </form>
      </div>

      {/* Info box */}
      <div className={styles.infoBox}>
        <div className={styles.infoIcon}>
          <svg viewBox="0 0 20 20" fill="currentColor" width={16} height={16}>
            <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd"/>
          </svg>
        </div>
        <div>
          <p className={styles.infoTitle}>Konteyner Numarası Formatı</p>
          <p className={styles.infoText}>
            4 büyük harf (BIC kodu) + 7 rakam olmalıdır. Örnek: <code>MSCU1234567</code>, <code>MSKU9876543</code>
          </p>
        </div>
      </div>
    </div>
  )
}

function PlusIcon() {
  return (
    <svg viewBox="0 0 20 20" fill="currentColor" width={15} height={15}>
      <path fillRule="evenodd" d="M10 3a1 1 0 011 1v5h5a1 1 0 110 2h-5v5a1 1 0 11-2 0v-5H4a1 1 0 110-2h5V4a1 1 0 011-1z" clipRule="evenodd"/>
    </svg>
  )
}

function BicIcon() {
  return (
    <svg viewBox="0 0 16 16" fill="currentColor" width={12} height={12} style={{flexShrink:0}}>
      <path fillRule="evenodd" d="M8 1a7 7 0 100 14A7 7 0 008 1zm.75 4.25a.75.75 0 00-1.5 0v3.5a.75.75 0 001.5 0v-3.5zm0 5.5a.75.75 0 00-1.5 0v.5a.75.75 0 001.5 0v-.5z" clipRule="evenodd"/>
    </svg>
  )
}
