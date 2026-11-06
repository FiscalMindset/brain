import { createContext, useContext, useEffect, useState, ReactNode } from 'react'
import { setToken } from '../api/client'

type Theme = 'dark' | 'light'
const Ctx = createContext<{ theme: Theme; setTheme: (t: Theme) => void; authed: boolean; logout: () => void; markAuthed: () => void }>(
  { theme: 'dark', setTheme: () => {}, authed: false, logout: () => {}, markAuthed: () => {} },
)

export function ThemeProvider({ children }: { children: ReactNode }) {
  const [theme, setThemeState] = useState<Theme>(() => {
    try {
      const t = localStorage.getItem('sb_theme')
      return t === 'light' || t === 'dark' ? t : 'dark'
    } catch { return 'dark' }
  })
  const [authed, setAuthed] = useState<boolean>(() => { try { return !!localStorage.getItem('sb_token') } catch { return false } })

  const setTheme = (t: Theme) => {
    setThemeState(t)
    document.documentElement.setAttribute('data-theme', t)
    try { localStorage.setItem('sb_theme', t) } catch {}
  }
  useEffect(() => { document.documentElement.setAttribute('data-theme', theme) }, []) // eslint-disable-line
  const logout = () => { setToken(null); setAuthed(false); window.location.href = '/login' }
  const markAuthed = () => setAuthed(true)

  return <Ctx.Provider value={{ theme, setTheme, authed, logout, markAuthed }}>{children}</Ctx.Provider>
}

export const useApp = () => useContext(Ctx)
