import { useState } from 'react'
import Navbar from '../components/Navbar'
import AnalyzeTab from '../components/AnalyzeTab'
import RegisterTab from '../components/RegisterTab'
import ListTab from '../components/ListTab'
import styles from './DashboardPage.module.css'

const TABS = ['analyze', 'register-container', 'list']
const PANELS = {
  'analyze':            AnalyzeTab,
  'register-container': RegisterTab,
  'list':               ListTab,
}

export default function DashboardPage() {
  const [activeTab,          setActiveTab]          = useState('analyze')
  const [prefillContainerNo, setPrefillContainerNo] = useState('')
  const [prefillCompanyName, setPrefillCompanyName] = useState('')
  const [prefillIsDamaged,   setPrefillIsDamaged]   = useState(null)
  const [prefillKey,         setPrefillKey]         = useState(0)

  function handleSendToRegister(containerNo, companyName, isDamaged) {
    setPrefillContainerNo(containerNo || '')
    setPrefillCompanyName(companyName || '')
    setPrefillIsDamaged(isDamaged ?? null)
    setPrefillKey(k => k + 1)
    setActiveTab('register-container')
  }

  return (
    <div className={styles.layout}>
      <Navbar activeTab={activeTab} onTabChange={setActiveTab} />
      <main className={styles.main}>
        {TABS.map(tab => {
          const Panel = PANELS[tab]
          const extraProps = tab === 'analyze'
            ? { onSendToRegister: handleSendToRegister }
            : tab === 'register-container'
            ? { prefillContainerNo, prefillCompanyName, prefillIsDamaged, prefillKey, onPrefillUsed: () => { setPrefillContainerNo(''); setPrefillCompanyName(''); setPrefillIsDamaged(null) } }
            : {}
          return (
            <div key={tab} style={{ display: activeTab === tab ? 'block' : 'none' }}>
              <Panel isActive={activeTab === tab} {...extraProps} />
            </div>
          )
        })}
      </main>
    </div>
  )
}
