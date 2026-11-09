// Generated from OpenAPI 2026-11-08; regenerate with scripts/generate_types.sh

/** Auth user (from users table; web-safe fields). */
export interface User {
  id: string
  email: string
  full_name?: string | null
  created_at?: string
}

export interface TokenResponse {
  access_token: string
  token_type: string
}

/** Source (SourceOut in openapi.json). */
export interface Source {
  id: string
  kind: string
  title: string | null
  url?: string | null
  content_hash: string
  chunks?: number
  deduplicated?: boolean
  meta?: Record<string, unknown> | null
  created_at?: string
}

/** Document chunk row. */
export interface Document {
  id: string
  user_id?: string
  source_id?: string | null
  chunk_index: number
  text: string
  meta?: Record<string, unknown>
  created_at?: string
}

export interface SearchResult {
  document_id: string
  source_id: string | null
  chunk_index: number
  text: string
  citation: Citation
}

export interface Citation {
  document_id: string
  source_id?: string | null
  chunk_index?: number
  snippet?: string
  meta?: Record<string, unknown>
}

export interface SearchResponse {
  query: string
  count: number
  results: SearchResult[]
  citations: Citation[]
}

export interface ResearchStep {
  agent?: string
  name?: string
  role?: string
  status?: string
  output?: string
  [k: string]: unknown
}

export interface ResearchResponse {
  session_id?: string
  query: string
  steps: ResearchStep[]
  findings: { text: string; document_id?: string; chunk_index?: number }[]
  contradictions?: unknown[]
  gaps?: unknown[]
  citations?: Citation[]
  project_id?: string | null
  human_approval?: boolean | string | null
  next_actions?: string[]
  [k: string]: unknown
}

/** Project (projects table + tasks). */
export interface Project {
  id: string
  title: string
  description?: string
  status?: string
  tasks?: Task[]
  created_at?: string
  [k: string]: unknown
}

export interface Task {
  id?: string
  project_id?: string
  title: string
  body?: string
  status?: string
  assignee?: string | null
  created_at?: string
  [k: string]: unknown
}

export interface Integration {
  name: string
  status?: string
  requires_oauth?: boolean
  [k: string]: unknown
}

export interface AgentInfo {
  name: string
  role?: string
  permissions?: string[] | string
  [k: string]: unknown
}
