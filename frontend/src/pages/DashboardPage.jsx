import { useState } from 'react'
import Navbar from '../components/Navbar'
import AnalyzeTab from '../components/AnalyzeTab'
import RegisterTab from '../components/RegisterTab'
import ListTab from '../components/ListTab'
import styles from './DashboardPage.module.css'

const PANELS = {
  'analyze':            AnalyzeTab,
  'register-container': RegisterTab,
  'list':               ListTab,
}

export default function DashboardPage() {
  const [activeTab, setActiveTab] = useState('analyze')
  const Panel = PANELS[activeTab]

  return (
    <div className={styles.layout}>
      <Navbar activeTab={activeTab} onTabChange={setActiveTab} />
      <main className={styles.main}>
        <Panel />
      </main>
    </div>
  )
}
