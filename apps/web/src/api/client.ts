// Typed API client — all calls go through /api (Vite proxy in dev).
// Canonical shared contracts (SB-ARCH-004) live in packages/shared/types.ts.
import type {
  User, Source, Document, SearchResult, ResearchStep,
  SearchResponse, ResearchResponse, Project, Task, Integration, AgentInfo, TokenResponse,
} from '../../../../packages/shared/types'

export type {
  User, Source, Document, SearchResult, ResearchStep,
  SearchResponse, ResearchResponse, Project, Task, Integration, AgentInfo, TokenResponse,
}

export class ApiError extends Error {
  status: number
  body: string
  constructor(message: string, status: number, body = '') {
    super(message)
    this.name = 'ApiError'
    this.status = status
    this.body = body
  }
}

export const TOKEN_KEY = 'sb_token'

export function getToken(): string | null {
  try { return localStorage.getItem(TOKEN_KEY) } catch { return null }
}
export function setToken(t: string | null) {
  try {
    if (t) localStorage.setItem(TOKEN_KEY, t)
    else localStorage.removeItem(TOKEN_KEY)
  } catch { /* ignore */ }
}

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  const headers: Record<string, string> = { ...(init.headers as Record<string, string>) }
  const token = getToken()
  if (token) headers.Authorization = `Bearer ${token}`
  let res: Response
  try {
    res = await fetch(path, { ...init, headers })
  } catch (e) {
    throw new ApiError(`Network error reaching ${path}: ${e instanceof Error ? e.message : 'unknown'}`, 0)
  }
  const text = await res.text()
  let data: unknown = null
  try { data = text ? JSON.parse(text) : null } catch { data = text }
  if (!res.ok) {
    const msg = (data as any)?.detail ?? (data as any)?.message ?? text ?? res.statusText
    throw new ApiError(typeof msg === 'string' && msg ? msg : `${res.status} ${res.statusText}`, res.status, text)
  }
  return data as T
}

const json = (body: unknown): RequestInit => ({
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(body),
})

// ---------- Types ----------
// Canonical shapes (TokenResponse, SearchResponse, ResearchResponse, Project,
// Task, Integration, AgentInfo, Source, Document, SearchResult) are re-exported
// from packages/shared/types.ts above (SB-ARCH-004). Web-only shapes follow.
export interface SourceSummary { id: string; kind: string; title: string; url?: string | null; content_hash?: string; chunks?: number; deduplicated?: boolean }
export interface SourceDetail extends SourceSummary {
  meta?: Record<string, unknown> | null
  chunks_detail?: Chunk[]
  chunks_list?: Chunk[]
}
export interface Chunk { id: string; chunk_index: number; text: string }
export interface DashboardData { [k: string]: unknown; metrics?: Record<string, number>; sources?: unknown[]; projects?: unknown[]; recent_activity?: unknown[]; activity?: unknown[]; memories?: unknown[]; entities?: unknown[] }
export interface MemoryItem { id: string; text?: string; content?: string; key?: string; [k: string]: unknown }
export interface GraphData { entities?: unknown[]; relationships?: unknown[]; nodes?: unknown[]; edges?: unknown[]; [k: string]: unknown }
export interface AuditEvent { id?: string; timestamp?: string; created_at?: string; action?: string; actor?: string; detail?: string; [k: string]: unknown }

// ---------- Auth ----------
export const apiAuth = {
  register: (email: string, password: string, full_name: string) =>
    request<TokenResponse>('/api/auth/register', json({ email, password, full_name })),
  login: (email: string, password: string) =>
    request<TokenResponse>('/api/auth/login', json({ email, password })),
}

// ---------- Sources ----------
export interface CreateSourcePayload { kind: string; title?: string; url?: string; content?: string; meta?: Record<string, unknown> }
export const apiSources = {
  create: (p: CreateSourcePayload) => request<SourceSummary>('/api/sources', json(p)),
  list: () => request<SourceSummary[]>('/api/sources'),
  get: (id: string) => request<any>(`/api/sources/${encodeURIComponent(id)}`),
  upload: (files: File[]) => {
    const fd = new FormData()
    files.forEach(f => fd.append('files', f))
    return request<{ uploaded: number; results: unknown[] }>('/api/sources/upload', { method: 'POST', body: fd })
  },
}

// ---------- Search ----------
export const apiSearch = {
  search: (q: string, kind = '', limit = 20) => {
    const params = new URLSearchParams({ q, limit: String(limit) })
    if (kind) params.set('kind', kind)
    return request<SearchResponse>(`/api/search?${params}`)
  },
}

// ---------- Research ----------
export const apiResearch = {
  run: (query: string, limit = 10) => request<ResearchResponse>('/api/research', json({ query, limit })),
}

// ---------- Agents ----------
export const apiAgents = {
  list: () => request<{ agents: AgentInfo[]; count: number }>('/api/agents'),
  run: (agent: string, query: string) => request<any>('/api/agents/run', json({ agent, query })),
}

// ---------- Projects ----------
export const apiProjects = {
  create: (title: string, description = '', status = 'active') =>
    request<Project>('/api/projects', json({ title, description, status })),
  list: () => request<Project[]>('/api/projects'),
  get: (id: string) => request<Project>(`/api/projects/${encodeURIComponent(id)}`),
  addTask: (id: string, t: { title: string; body?: string; status?: string; assignee?: string }) =>
    request<Task>(`/api/projects/${encodeURIComponent(id)}/tasks`, json(t)),
  issueDraft: (id: string) => request<any>(`/api/projects/${encodeURIComponent(id)}/issue-draft`, json({})),
}

// ---------- Integrations ----------
export const apiIntegrations = {
  list: () => request<{ integrations: Integration[]; contract?: unknown; count: number }>('/api/integrations'),
}

// ---------- Optional / degrading endpoints ----------
export const apiOptional = {
  dashboard: () => request<DashboardData>('/api/dashboard'),
  memoryList: () => request<any>('/api/memory'),
  memoryCreate: (body: Record<string, unknown>) => request<any>('/api/memory', json(body)),
  memoryUpdate: (id: string, body: Record<string, unknown>) =>
    request<any>(`/api/memory/${encodeURIComponent(id)}`, { method: 'PATCH', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) }),
  memoryDelete: (id: string) => request<any>(`/api/memory/${encodeURIComponent(id)}`, { method: 'DELETE' }),
  graph: () => request<GraphData>('/api/graph'),
  graphAddEntity: (body: Record<string, unknown>) => request<any>('/api/graph/entities', json(body)),
  graphAddRelationship: (body: Record<string, unknown>) => request<any>('/api/graph/relationships', json(body)),
  audit: (page = 1, limit = 20) =>
    request<any>(`/api/audit?limit=${limit}&offset=${(page - 1) * limit}`),
}
