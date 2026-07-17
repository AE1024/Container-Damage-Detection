export default function Toast({ message, type = 'info' }) {
  const icons = {
    success: '✓',
    error:   '✕',
    info:    'ℹ',
  }
  return (
    <div className={`toast ${type}`}>
      <span>{icons[type]}</span>
      <span>{message}</span>
    </div>
  )
}
