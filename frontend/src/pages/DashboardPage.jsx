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
  const [activeTab, setActiveTab] = useState('analyze')

  return (
    <div className={styles.layout}>
      <Navbar activeTab={activeTab} onTabChange={setActiveTab} />
      <main className={styles.main}>
        {TABS.map(tab => {
          const Panel = PANELS[tab]
          return (
            <div key={tab} style={{ display: activeTab === tab ? 'block' : 'none' }}>
              <Panel />
            </div>
          )
        })}
      </main>
    </div>
  )
}
