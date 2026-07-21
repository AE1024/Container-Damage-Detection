import { useState, useEffect } from 'react'
import { api } from '../api'
import { useAuth, useToast } from '../App'
import styles from './ListTab.module.css'

const CONTAINER_TYPES = ['Kuru Yük', 'Soğutmalı', 'Açık Üst', 'Platform', 'Tank', 'Özel Amaçlı']

export default function ListTab({ isActive }) {
  const [containers,     setContainers]     = useState([])
  const [total,          setTotal]          = useState(0)
  const [loading,        setLoading]        = useState(false)
  const [dateFrom,       setDateFrom]       = useState('')
  const [dateTo,         setDateTo]         = useState('')
  const [limit,          setLimit]          = useState('10')
  const [containerNo,    setContainerNo]    = useState('')
  const [containerType,  setContainerType]  = useState('')
  const [companyName,    setCompanyName]    = useState('')

  const { user }      = useAuth()
  const { showToast } = useToast()

  function buildParams() {
    return {
      date_from:      dateFrom      || undefined,
      date_to:        dateTo        || undefined,
      limit,
      container_no:   containerNo   || undefined,
      container_type: containerType || undefined,
      company_name:   companyName   || undefined,
    }
  }

  async function fetchList(params) {
    setLoading(true)
    try {
      const data = await api.listContainers(params)
      setContainers(data.containers)
      setTotal(data.total)
    } catch (err) {
      showToast(err.message, 'error')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { if (isActive) fetchList({ limit }) }, [isActive])

  function handleFilter(e) {
    e.preventDefault()
    fetchList(buildParams())
  }

  function handleClear() {
    setDateFrom('')
    setDateTo('')
    setContainerNo('')
    setContainerType('')
    setCompanyName('')
    fetchList({ limit })
  }

  async function handleDelete(containerNo) {
    if (!window.confirm(`"${containerNo}" numaralı konteyneri silmek istediğinizden emin misiniz?`)) return
    try {
      await api.deleteContainer(containerNo)
      showToast(`${containerNo} silindi.`, 'success')
      setContainers(prev => prev.filter(c => c.container_no !== containerNo))
      setTotal(t => t - 1)
    } catch (err) {
      showToast(err.message, 'error')
    }
  }

  const hasActiveFilters = dateFrom || dateTo || containerNo || containerType || companyName

  return (
    <div>
      {/* Header */}
      <div className={styles.header}>
        <div>
          <h2 className={styles.title}>Konteyner Listesi</h2>
          <p className={styles.sub}>Kayıtlı konteynerleri görüntüleyin ve yönetin</p>
        </div>
        <button
          className="btn btn-ghost sm"
          onClick={() => fetchList(buildParams())}
        >
          <RefreshIcon /> Yenile
        </button>
      </div>

      {/* Filters */}
      <form className={styles.filtersCard} onSubmit={handleFilter}>
        <div className={styles.filtersRow}>
          <div className="field">
            <label>Konteyner No</label>
            <input
              type="text"
              placeholder="MSCU1234567"
              value={containerNo}
              onChange={e => setContainerNo(e.target.value.toUpperCase())}
              style={{ textTransform: 'uppercase', fontFamily: 'monospace' }}
            />
          </div>
          <div className="field">
            <label>Yük Tipi</label>
            <select value={containerType} onChange={e => setContainerType(e.target.value)}>
              <option value="">Tümü</option>
              {CONTAINER_TYPES.map(t => <option key={t} value={t}>{t}</option>)}
            </select>
          </div>
          <div className="field">
            <label>Şirket</label>
            <input
              type="text"
              placeholder="Şirket adı..."
              value={companyName}
              onChange={e => setCompanyName(e.target.value)}
            />
          </div>
        </div>
        <div className={styles.filtersRow} style={{ marginTop: 12 }}>
          <div className="field">
            <label>Başlangıç Tarihi</label>
            <input type="date" value={dateFrom} onChange={e => setDateFrom(e.target.value)} />
          </div>
          <div className="field">
            <label>Bitiş Tarihi</label>
            <input type="date" value={dateTo} onChange={e => setDateTo(e.target.value)} />
          </div>
          <div className="field">
            <label>Limit</label>
            <select value={limit} onChange={e => setLimit(e.target.value)}>
              <option value="10">10 kayıt</option>
              <option value="25">25 kayıt</option>
              <option value="50">50 kayıt</option>
              <option value="100">100 kayıt</option>
            </select>
          </div>
          <button type="submit" className="btn btn-primary sm" style={{ alignSelf: 'flex-end' }}>
            Filtrele
          </button>
          {hasActiveFilters && (
            <button
              type="button"
              className="btn btn-ghost sm"
              style={{ alignSelf: 'flex-end' }}
              onClick={handleClear}
            >
              Temizle
            </button>
          )}
        </div>
      </form>

      {/* Table */}
      <div className={styles.tableCard}>
        {loading && (
          <div className={styles.stateRow}>
            <span className="spinner" />
            <span>Yükleniyor...</span>
          </div>
        )}

        {!loading && containers.length === 0 && (
          <div className={styles.emptyState}>
            <svg viewBox="0 0 48 48" fill="none" stroke="currentColor" strokeWidth={1.5} width={48} height={48}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M40 14H8a4 4 0 00-4 4v20a4 4 0 004 4h32a4 4 0 004-4V18a4 4 0 00-4-4z"/>
              <path strokeLinecap="round" strokeLinejoin="round" d="M32 42V10a4 4 0 00-4-4H20a4 4 0 00-4 4v32"/>
            </svg>
            <p>Kayıtlı konteyner bulunamadı.</p>
          </div>
        )}

        {!loading && containers.length > 0 && (
          <>
            <div className={styles.tableScroll}>
              <table className={styles.table}>
                <thead>
                  <tr>
                    <th>Konteyner No</th>
                    <th>Tip</th>
                    <th>Şirket</th>
                    <th>Geliş Limanı</th>
                    <th>Varış Limanı</th>
                    <th>Kaydeden</th>
                    <th>Tarih</th>
                    <th></th>
                  </tr>
                </thead>
                <tbody>
                  {containers.map(c => (
                    <tr key={c.container_no}>
                      <td className={styles.containerNo}>{c.container_no}</td>
                      <td><span className={styles.typeBadge}>{c.container_type}</span></td>
                      <td>{c.company_name}</td>
                      <td>{c.arrive_port}</td>
                      <td>{c.destination_port}</td>
                      <td className={styles.registeredBy}>{c.registered_by}</td>
                      <td className={styles.date}>{c.created_at}</td>
                      <td>
                        <button
                          className="btn btn-danger-sm"
                          onClick={() => handleDelete(c.container_no)}
                        >
                          <TrashIcon /> Sil
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <div className={styles.tableFooter}>
              {total} kayıt
              {user?.role === 'admin' && <span className={styles.adminNote}> · Tüm kullanıcılar</span>}
            </div>
          </>
        )}
      </div>
    </div>
  )
}

function RefreshIcon() {
  return (
    <svg viewBox="0 0 20 20" fill="currentColor" width={13} height={13}>
      <path fillRule="evenodd" d="M4 2a1 1 0 011 1v2.101a7.002 7.002 0 0111.601 2.566 1 1 0 11-1.885.666A5.002 5.002 0 005.999 7H9a1 1 0 010 2H4a1 1 0 01-1-1V3a1 1 0 011-1zm.008 9.057a1 1 0 011.276.61A5.002 5.002 0 0014.001 13H11a1 1 0 110-2h5a1 1 0 011 1v5a1 1 0 11-2 0v-2.101a7.002 7.002 0 01-11.601-2.566 1 1 0 01.61-1.276z" clipRule="evenodd"/>
    </svg>
  )
}

function TrashIcon() {
  return (
    <svg viewBox="0 0 20 20" fill="currentColor" width={12} height={12}>
      <path fillRule="evenodd" d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v6a1 1 0 102 0V8a1 1 0 00-1-1z" clipRule="evenodd"/>
    </svg>
  )
}
