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
  const [prefillKey,         setPrefillKey]         = useState(0)

  function handleSendToRegister(containerNo, companyName) {
    setPrefillContainerNo(containerNo || '')
    setPrefillCompanyName(companyName || '')
    setPrefillKey(k => k + 1)   // her tıklamada artar → RegisterTab her zaman sıfırlanır
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
            ? { prefillContainerNo, prefillCompanyName, prefillKey, onPrefillUsed: () => { setPrefillContainerNo(''); setPrefillCompanyName('') } }
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
