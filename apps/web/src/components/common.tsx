import { ReactNode, useEffect, useRef } from 'react'
import { Link } from 'react-router-dom'
import { useApp } from '../store/theme'

// ---------- Layout ----------
const NAV = [
  { to: '/', label: 'Dashboard', icon: '⌂' },
  { to: '/library', label: 'Library', icon: '📚' },
  { to: '/search', label: 'Search', icon: '🔍' },
  { to: '/research', label: 'Research', icon: '🧪' },
  { to: '/agents', label: 'Agents', icon: '🤖' },
  { to: '/projects', label: 'Projects', icon: '📋' },
  { to: '/integrations', label: 'Integrations', icon: '🔌' },
  { to: '/graph', label: 'Graph', icon: '🕸' },
  { to: '/memory', label: 'Memory', icon: '🧠' },
  { to: '/activity', label: 'Activity', icon: '📈' },
  { to: '/settings', label: 'Settings', icon: '⚙' },
]

export function Layout({ children }: { children: ReactNode }) {
  const { theme, setTheme, logout } = useApp()
  return (
    <div className="sb-layout">
      <a className="sb-skip" href="#sb-main">Skip to main content</a>
      <aside className="sb-sidebar" aria-label="Primary">
        <div className="sb-brand">🧠 SecondBrain</div>
        <nav className="sb-nav" aria-label="Main navigation">
          {NAV.map((n) => (
            <NavLink key={n.to} to={n.to} label={n.label} icon={n.icon} />
          ))}
        </nav>
      </aside>
      <div className="sb-main">
        <header className="sb-topbar">
          <strong>SecondBrain</strong>
          <span className="sb-badge">API: /api</span>
          <span className="sb-topbar-spacer" />
          <button
            className="sb-btn sb-btn-ghost"
            aria-label={`Switch to ${theme === 'dark' ? 'light' : 'dark'} theme`}
            onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
          >
            {theme === 'dark' ? '☀ Light' : '🌙 Dark'}
          </button>
          <button className="sb-btn" aria-label="Log out" onClick={logout}>Logout</button>
        </header>
        <main id="sb-main" className="sb-content" tabIndex={-1}>{children}</main>
      </div>
    </div>
  )
}

function NavLink({ to, label, icon }: { to: string; label: string; icon: string }) {
  const { } = useApp()
  const isActive = to === '/' ? window.location.pathname === '/' : window.location.pathname.startsWith(to)
  return (
    <Link to={to} aria-current={isActive ? 'page' : undefined} className={isActive ? 'active' : ''} onClick={() => {}}>
      <span aria-hidden>{icon}</span> {label}
    </Link>
  )
}

// ---------- Primitives ----------
export function PageHeader({ title, sub, action }: { title: string; sub?: string; action?: ReactNode }) {
  return (
    <div className="sb-pageheader">
      <div><h1>{title}</h1>{sub ? <p>{sub}</p> : null}</div>
      {action}
    </div>
  )
}
export function StatCard({ label, value }: { label: string; value: ReactNode }) {
  return <div className="sb-card"><div className="sb-stat-label">{label}</div><div className="sb-stat-value">{value}</div></div>
}
export function Badge({ children, tone }: { children: ReactNode; tone?: 'ok' | 'warn' | 'danger' }) {
  const cls = tone === 'ok' ? 'sb-badge-ok' : tone === 'warn' ? 'sb-badge-warn' : tone === 'danger' ? 'sb-badge-danger' : ''
  return <span className={`sb-badge ${cls}`}>{children}</span>
}
export function EmptyState({ title, hint }: { title: string; hint?: string }) {
  return (
    <div className="sb-card sb-empty" role="status">
      <p style={{ fontSize: 17, fontWeight: 700, color: 'var(--text)' }}>{title}</p>
      {hint ? <p className="sb-small">{hint}</p> : null}
    </div>
  )
}
export function ErrorState({ message, onRetry }: { message: string; onRetry?: () => void }) {
  return (
    <div className="sb-error" role="alert">
      <p style={{ fontWeight: 700 }}>Something went wrong</p>
      <p className="sb-small">{message}</p>
      {onRetry ? <button className="sb-btn" onClick={onRetry}>↻ Retry</button> : null}
    </div>
  )
}
export function LoadingSkeleton({ label = 'Loading…' }: { label?: string }) {
  return <div className="sb-skeleton" role="status" aria-label={label}>{label}</div>
}

export function Modal({ title, onClose, children }: { title: string; onClose: () => void; children: ReactNode }) {
  const ref = useRef<HTMLDivElement>(null)
  useEffect(() => {
    ref.current?.focus()
    const h = (e: KeyboardEvent) => { if (e.key === 'Escape') onClose() }
    window.addEventListener('keydown', h)
    return () => window.removeEventListener('keydown', h)
  }, [onClose])
  return (
    <div className="sb-modal-backdrop" onClick={onClose}>
      <div className="sb-modal" role="dialog" aria-modal="true" aria-label={title} ref={ref} tabIndex={-1} onClick={(e) => e.stopPropagation()}>
        <div className="sb-row" style={{ justifyContent: 'space-between' }}>
          <h2>{title}</h2>
          <button className="sb-btn sb-btn-ghost" aria-label="Close dialog" onClick={onClose}>✕</button>
        </div>
        {children}
      </div>
    </div>
  )
}
export function ConfirmDialog({ title, body, onConfirm, onCancel }: { title: string; body: string; onConfirm: () => void; onCancel: () => void }) {
  return (
    <Modal title={title} onClose={onCancel}>
      <p>{body}</p>
      <div className="sb-row" style={{ marginTop: 18 }}>
        <button className="sb-btn sb-btn-danger" onClick={onConfirm}>Confirm</button>
        <button className="sb-btn" onClick={onCancel}>Cancel</button>
      </div>
    </Modal>
  )
}
export function NotAvailableYet({ what }: { what: string }) {
  return (
    <div className="sb-card">
      <p><Badge tone="warn">API not yet available</Badge></p>
      <p className="sb-muted">The <strong>{what}</strong> endpoint is not available on the backend yet. This page will light up automatically once it ships — nothing here is faked.</p>
    </div>
  )
}
