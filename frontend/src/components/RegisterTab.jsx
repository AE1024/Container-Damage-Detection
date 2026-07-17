import { useState } from 'react'
import { api } from '../api'
import { useToast } from '../App'
import styles from './RegisterTab.module.css'

const CONTAINER_TYPES = [
  'Kuru Yük', 'Soğutmalı', 'Açık Üst', 'Platform', 'Tank', 'Özel Amaçlı',
]

export default function RegisterTab() {
  const [msg,     setMsg]     = useState(null)
  const [loading, setLoading] = useState(false)
  const { showToast }         = useToast()

  async function handleSubmit(e) {
    e.preventDefault()
    setMsg(null)
    setLoading(true)
    const fd = new FormData(e.target)
    const body = {
      container_no:     fd.get('container_no').toUpperCase().replace(/\s/g, ''),
      container_type:   fd.get('container_type'),
      company_name:     fd.get('company_name').toUpperCase(),
      arrive_port:      fd.get('arrive_port'),
      destination_port: fd.get('destination_port'),
    }
    try {
      await api.registerContainer(body)
      setMsg({ type: 'success', text: `${body.container_no} başarıyla kayıt edildi.` })
      showToast('Konteyner kayıt edildi.', 'success')
      e.target.reset()
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
        <form onSubmit={handleSubmit} onReset={() => setMsg(null)}>
          <div className={styles.grid}>
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
                style={{ textTransform: 'uppercase' }}
              />
            </div>

            <div className="field">
              <label>Konteyner Tipi</label>
              <select name="container_type" required>
                <option value="">Seçiniz</option>
                {CONTAINER_TYPES.map(t => (
                  <option key={t} value={t}>{t}</option>
                ))}
              </select>
            </div>

            <div className="field">
              <label>Şirket Adı</label>
              <input
                name="company_name"
                type="text"
                placeholder="MAERSK LINE"
                required
                style={{ textTransform: 'uppercase' }}
              />
            </div>

            <div className="field">
              <label>Geliş Limanı</label>
              <input name="arrive_port" type="text" placeholder="İstanbul" required />
            </div>

            <div className="field">
              <label>Varış Limanı</label>
              <input name="destination_port" type="text" placeholder="Hamburg" required />
            </div>
          </div>

          {msg && (
            <div className={`form-alert ${msg.type}`} style={{ marginBottom: '20px' }}>
              {msg.text}
            </div>
          )}

          <div className={styles.actions}>
            <button type="submit" className="btn btn-primary" disabled={loading}>
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
            4 büyük harf + 7 rakam olmalıdır. Örnek: <code>MSCU1234567</code>, <code>MSKU9876543</code>
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
