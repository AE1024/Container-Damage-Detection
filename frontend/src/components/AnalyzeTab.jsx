import { useState, useRef, useCallback, useEffect } from 'react'
import { api } from '../api'
import { useToast } from '../App'
import styles from './AnalyzeTab.module.css'

const MAX_FILES = 6
const ACCEPT    = ['image/jpeg', 'image/png', 'image/webp']

function makePreviewUrls(fileList) {
  return fileList.map(f => URL.createObjectURL(f))
}

export default function AnalyzeTab({ onSendToRegister }) {
  const [files,    setFiles]    = useState([])
  const [previews, setPreviews] = useState([])
  const [results,  setResults]  = useState(null)
  const [loading,  setLoading]  = useState(false)
  const [dragging, setDragging] = useState(false)

  const inputRef      = useRef(null)
  const { showToast } = useToast()

  // Eski object URL'lerini temizle (bellek sızıntısını önler)
  useEffect(() => {
    return () => { previews.forEach(url => URL.revokeObjectURL(url)) }
  }, [previews])

  const addFiles = useCallback((newFiles) => {
    const valid = Array.from(newFiles).filter(f => ACCEPT.includes(f.type))
    if (!valid.length) { showToast('Yalnızca JPG, PNG veya WebP dosyaları desteklenir.', 'error'); return }

    setFiles(prev => {
      const merged = [...prev, ...valid].slice(0, MAX_FILES)
      setPreviews(makePreviewUrls(merged))
      return merged
    })
    setResults(null)
  }, [showToast])

  const removeFile = (idx) => {
    setFiles(prev => {
      const next = prev.filter((_, i) => i !== idx)
      setPreviews(makePreviewUrls(next))
      return next
    })
  }

  const clearAll = () => { setFiles([]); setPreviews([]); setResults(null) }

  const onDrop = (e) => {
    e.preventDefault()
    setDragging(false)
    addFiles(e.dataTransfer.files)
  }

  async function handleAnalyze() {
    if (!files.length) return
    setLoading(true)
    setResults(null)
    try {
      const form = new FormData()
      files.forEach(f => form.append('files', f))
      const data = await api.analyze(form)
      setResults(data.results)
      showToast(`${data.count} görüntü analiz edildi.`, 'success')
    } catch (err) {
      showToast(err.message, 'error')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div>
      {/* Header */}
      <div className={styles.header}>
        <div>
          <h2 className={styles.title}>Hasar Analizi</h2>
          <p className={styles.sub}>Konteyner görüntülerini yükleyin, yapay zeka hasarı tespit etsin</p>
        </div>
        <span className="chip chip-sky">YZ Destekli</span>
      </div>

      {/* Upload Zone — hidden when results shown */}
      {!results && (
        <>
          <div
            className={`${styles.uploadZone} ${dragging ? styles.dragOver : ''}`}
            onDragOver={e => { e.preventDefault(); setDragging(true) }}
            onDragLeave={() => setDragging(false)}
            onDrop={onDrop}
            onClick={() => !files.length && inputRef.current?.click()}
          >
            <div className={styles.uploadIcon}>
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.5} width={28} height={28}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5m-13.5-9L12 3m0 0l4.5 4.5M12 3v13.5"/>
              </svg>
            </div>
            <p className={styles.uploadTitle}>Görüntü sürükleyin veya seçin</p>
            <p className={styles.uploadMeta}>JPG, PNG, WebP · En fazla {MAX_FILES} dosya</p>
            <button
              className="btn btn-primary"
              onClick={e => { e.stopPropagation(); inputRef.current?.click() }}
            >
              Dosya Seç
            </button>
            <input
              ref={inputRef}
              type="file"
              multiple
              accept=".jpg,.jpeg,.png,.webp"
              hidden
              onChange={e => addFiles(e.target.files)}
            />
          </div>

          {/* Preview */}
          {files.length > 0 && (
            <div className={styles.previewSection}>
              <div className={styles.sectionRow}>
                <h3 className={styles.sectionTitle}>Seçilen Görüntüler</h3>
                <div className={styles.sectionActions}>
                  <span className="chip chip-mist">{files.length} / {MAX_FILES}</span>
                  <button className="btn btn-ghost sm" onClick={clearAll}>Temizle</button>
                  {files.length < MAX_FILES && (
                    <button className="btn btn-ghost sm" onClick={() => inputRef.current?.click()}>+ Ekle</button>
                  )}
                </div>
              </div>

              <div className={styles.previewGrid}>
                {previews.map((url, i) => (
                  <div key={i} className={styles.previewItem}>
                    <img src={url} alt={files[i]?.name} />
                    <button className={styles.removeBtn} onClick={() => removeFile(i)}>✕</button>
                    <span className={styles.fileName}>{files[i]?.name}</span>
                  </div>
                ))}
              </div>

              <button
                className="btn btn-primary"
                onClick={handleAnalyze}
                disabled={loading}
              >
                {loading
                  ? <><span className="spinner" style={{borderTopColor:'#fff',borderColor:'rgba(255,255,255,.3)'}} />Analiz ediliyor...</>
                  : <><SearchIcon /> Analiz Başlat</>
                }
              </button>
            </div>
          )}
        </>
      )}

      {/* Results */}
      {results && (
        <div className={styles.resultsSection}>
          <div className={styles.sectionRow}>
            <h3 className={styles.sectionTitle}>Analiz Sonuçları</h3>
            <button className="btn btn-ghost sm" onClick={clearAll}>Yeni Analiz</button>
          </div>
          <div className={styles.resultsGrid}>
            {results.map((r, i) => (
              <ResultCard key={i} result={r} index={i} onSendToRegister={onSendToRegister} />
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

function ResultCard({ result, index, onSendToRegister }) {
  const { hasar_var, hasar, skor, tespit_sayisi, detections, annotated_img, container_no, company_name } = result

  return (
    <div className={styles.resultCard}>
      {/* Annotated image */}
      <div className={styles.resultImgWrap}>
        <img
          src={`data:image/png;base64,${annotated_img}`}
          alt={`Analiz ${index + 1}`}
        />
      </div>

      <div className={styles.resultBody}>
        <div className={styles.resultStatusRow}>
          <span className={`${styles.statusBadge} ${hasar_var ? styles.danger : styles.safe}`}>
            {hasar_var ? '⚠ Hasar Tespit Edildi' : '✓ Hasar Yok'}
          </span>
          <span style={{fontSize:'12px', color:'var(--c-ash)'}}>
            {tespit_sayisi} tespit
          </span>
        </div>

        {hasar_var && (
          <>
            <div className={styles.stats}>
              <div className={styles.stat}>
                <span className={styles.statLabel}>Hasar Türü</span>
                <span className={styles.statValue}>{hasar}</span>
              </div>
              <div className={styles.stat}>
                <span className={styles.statLabel}>Güven Skoru</span>
                <span className={styles.statValue}>{skor}</span>
              </div>
              <div className={styles.stat}>
                <span className={styles.statLabel}>Tespit Sayısı</span>
                <span className={styles.statValue}>{tespit_sayisi}</span>
              </div>
            </div>

            {detections.length > 0 && (
              <div className={styles.detectionList}>
                <p className={styles.detectionTitle}>Tespitler</p>
                {detections.map((d, i) => (
                  <div key={i} className={styles.detectionItem}>
                    <span className={styles.detectionClass}>{d.class}</span>
                    <span className={styles.detectionConf}>{Math.round(d.confidence * 100)}%</span>
                  </div>
                ))}
              </div>
            )}
          </>
        )}

        {/* Konteyner No / Şirket — her zaman gösterilir */}
        <div className={styles.containerInfoBox}>
          <div className={styles.containerInfoRow}>
            <span className={styles.containerInfoLabel}>Konteyner No</span>
            <span className={container_no ? styles.containerInfoValue : styles.containerInfoEmpty}>
              {container_no || '—'}
            </span>
          </div>
          <div className={styles.containerInfoRow}>
            <span className={styles.containerInfoLabel}>Şirket</span>
            <span className={company_name ? styles.containerInfoValue : styles.containerInfoEmpty}>
              {company_name || '—'}
            </span>
          </div>
          {container_no && (
            <button
              className={styles.sendToRegisterBtn}
              onClick={() => onSendToRegister?.(container_no, company_name)}
            >
              <RegisterIcon /> Konteyner Kayıt'a Gönder
            </button>
          )}
        </div>
      </div>
    </div>
  )
}

function RegisterIcon() {
  return (
    <svg viewBox="0 0 20 20" fill="currentColor" width={13} height={13}>
      <path d="M10.293 3.293a1 1 0 011.414 0l6 6a1 1 0 010 1.414l-6 6a1 1 0 01-1.414-1.414L14.586 11H3a1 1 0 110-2h11.586l-4.293-4.293a1 1 0 010-1.414z"/>
    </svg>
  )
}

function SearchIcon() {
  return (
    <svg viewBox="0 0 20 20" fill="currentColor" width={15} height={15}>
      <path fillRule="evenodd" d="M8 4a4 4 0 100 8 4 4 0 000-8zM2 8a6 6 0 1110.89 3.476l4.817 4.817a1 1 0 01-1.414 1.414l-4.816-4.816A6 6 0 012 8z" clipRule="evenodd"/>
    </svg>
  )
}
