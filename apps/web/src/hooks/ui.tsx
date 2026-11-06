import { createContext, useCallback, useContext, useState, ReactNode } from 'react'

export interface Toast { id: number; msg: string; kind: 'ok' | 'err' | 'info' }
const ToastCtx = createContext<{ toasts: Toast[]; push: (msg: string, kind?: Toast['kind']) => void }>(
  { toasts: [], push: () => {} },
)

export function ToastProvider({ children }: { children: ReactNode }) {
  const [toasts, setToasts] = useState<Toast[]>([])
  const push = useCallback((msg: string, kind: Toast['kind'] = 'info') => {
    const id = Date.now() + Math.random()
    setToasts((t) => [...t, { id, msg, kind }])
    setTimeout(() => setToasts((t) => t.filter((x) => x.id !== id)), 4500)
  }, [])
  return (
    <ToastCtx.Provider value={{ toasts, push }}>
      {children}
      <div className="sb-toast-root" aria-live="polite" aria-atomic="true">
        {toasts.map((t) => (
          <div key={t.id} className={`sb-toast ${t.kind === 'err' ? 'sb-toast-err' : t.kind === 'ok' ? 'sb-toast-ok' : ''}`}>
            {t.msg}
          </div>
        ))}
      </div>
    </ToastCtx.Provider>
  )
}
export const useToast = () => useContext(ToastCtx)

export function useAsync<T>(fn: () => Promise<T>, deps: unknown[] = []) {
  const [data, setData] = useState<T | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [reloadKey, setReloadKey] = useState(0)
  const reload = useCallback(() => setReloadKey((k) => k + 1), [])
  // eslint-disable-next-line react-hooks/exhaustive-deps
  return { data, loading, error, reload, setData, setError, setLoading, reloadKey, deps }
}

export function highlight(text: string, query: string) {
  if (!query.trim()) return text
  const terms = query.trim().split(/\s+/).filter(Boolean).map((t) => t.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'))
  try {
    const re = new RegExp(`(${terms.join('|')})`, 'gi')
    const parts = text.split(re)
    return parts.map((p, i) => (re.test(p) ? <mark key={i} className="sb-highlight">{p}</mark> : p))
  } catch { return text }
}

export function errMsg(e: unknown): string {
  return e instanceof Error ? e.message : String(e)
}
