import React, { useCallback, useEffect, useState } from 'react'
import { BrowserRouter, Routes, Route, Navigate, useNavigate, useParams, Link } from 'react-router-dom'
import { ThemeProvider, useApp } from './store/theme'
import { ToastProvider, useToast, highlight, errMsg } from './hooks/ui'
import { Layout, PageHeader, StatCard, Badge, EmptyState, ErrorState, LoadingSkeleton, ConfirmDialog, Modal } from './components/common'
import { ApiError, apiAuth, apiSources, apiSearch, apiResearch, apiAgents, apiProjects, apiIntegrations, apiOptional, setToken } from './api/client'

// ---------- small helpers ----------
function useFetch<T>(fn: () => Promise<T>, deps: unknown[] = []) {
  const [data, setData] = useState<T | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const load = useCallback(async () => {
    setLoading(true); setError(null)
    try { setData(await fn()) } catch (e) { setError(errMsg(e)) } finally { setLoading(false) }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, deps)
  useEffect(() => { load() }, [load])
  return { data, loading, error, reload: load }
}
const s = (v: unknown) => (v == null ? '—' : String(v))

function RequireAuth({ children }: { children: React.ReactNode }) {
  const { authed } = useApp()
  if (!authed) return <Navigate to="/login" replace />
  return <Layout>{children}</Layout>
}

// ---------- Login ----------
function LoginPage() {
  const nav = useNavigate(); const toast = useToast(); const { markAuthed } = useApp()
  const [mode, setMode] = useState<'login' | 'register'>('login')
  const [email, setEmail] = useState(''); const [password, setPassword] = useState(''); const [fullName, setFullName] = useState('')
  const [busy, setBusy] = useState(false); const [error, setError] = useState<string | null>(null)
  const submit = async (e: React.FormEvent) => {
    e.preventDefault(); setBusy(true); setError(null)
    try {
      const r = mode === 'login' ? await apiAuth.login(email, password) : await apiAuth.register(email, password, fullName)
      setToken(r.access_token); markAuthed(); toast.push('Signed in', 'ok'); nav('/')
    } catch (err) { setError(errMsg(err)) } finally { setBusy(false) }
  }
  return (
    <div className="sb-auth">
      <div className="sb-card">
        <h1 style={{ marginTop: 0 }}>🧠 SecondBrain</h1>
        <p className="sb-muted">Personal research & knowledge workspace. Sign in to continue.</p>
        {error ? <ErrorState message={error} /> : null}
        <form onSubmit={submit}>
          <label className="sb-label" htmlFor="email">Email</label>
          <input id="email" className="sb-input" type="email" required value={email} onChange={e => setEmail(e.target.value)} autoComplete="email" />
          {mode === 'register' ? (<>
            <label className="sb-label" htmlFor="fullName">Full name</label>
            <input id="fullName" className="sb-input" value={fullName} onChange={e => setFullName(e.target.value)} autoComplete="name" />
          </>) : null}
          <label className="sb-label" htmlFor="password">Password</label>
          <input id="password" className="sb-input" type="password" required minLength={8} value={password} onChange={e => setPassword(e.target.value)} autoComplete="current-password" />
          <button className="sb-btn sb-btn-primary" style={{ width: '100%', marginTop: 18, justifyContent: 'center' }} disabled={busy}>{busy ? 'Please wait…' : mode === 'login' ? 'Sign in' : 'Create account'}</button>
        </form>
        <p className="sb-small" style={{ marginTop: 14 }}>
          {mode === 'login' ? <>No account? <button className="sb-btn sb-btn-ghost" onClick={() => setMode('register')}>Register</button></>
            : <>Have an account? <button className="sb-btn sb-btn-ghost" onClick={() => setMode('login')}>Sign in</button></>}
        </p>
      </div>
    </div>
  )
}

// ---------- Dashboard ----------
function DashboardPage() {
  const { data, loading, error, reload } = useFetch(() => apiOptional.dashboard())
  if (loading) return <LoadingSkeleton />
  if (error || !data) return <ErrorState message={error || 'No data'} onRetry={reload} />
  const counts: Record<string, number> = (data.counts as Record<string, number>) || {}
  const activity: any[] = (data.recent_activity as any[]) || []
  return (<>
    <PageHeader title="Dashboard" sub="Your knowledge command center." action={<button className="sb-btn" onClick={reload}>↻ Refresh</button>} />
    <div className="sb-grid sb-grid-4">
      <StatCard label="Sources" value={s(counts.sources ?? 0)} />
      <StatCard label="Documents" value={s(counts.documents ?? 0)} />
      <StatCard label="Projects" value={s(counts.projects ?? 0)} />
      <StatCard label="Tasks" value={s(counts.tasks ?? 0)} />
      <StatCard label="Memories" value={s(counts.memories ?? 0)} />
      <StatCard label="Entities" value={s(counts.entities ?? 0)} />
      <StatCard label="Research sessions" value={s(counts.research_sessions ?? 0)} />
      <StatCard label="Tasks done" value={s(counts.tasks_done ?? 0)} />
    </div>
    <div className="sb-card" style={{ marginTop: 16 }}>
      <h2 style={{ marginTop: 0 }}>Recent activity</h2>
      {activity.length ? <ul className="sb-list">{activity.map((a: any, i: number) => <li key={a.id || i}><span>{s(a.action)}</span><span className="sb-muted sb-small">{s(a.created_at || a.timestamp)}</span></li>)}</ul>
        : <EmptyState title="No activity yet" hint="Ingest a source or run research to see activity here." />}
    </div>
  </>)
}

// ---------- Library ----------
function LibraryPage() {
  const toast = useToast()
  const { data, loading, error, reload } = useFetch(() => apiSources.list())
  const [kind, setKind] = useState('note'); const [title, setTitle] = useState(''); const [url, setUrl] = useState(''); const [content, setContent] = useState('')
  const [busy, setBusy] = useState(false); const [filter, setFilter] = useState('')
  const create = async (e: React.FormEvent) => {
    e.preventDefault(); setBusy(true)
    try { const r = await apiSources.create({ kind, title: title || undefined, url: url || undefined, content }); toast.push(r.deduplicated ? 'Already existed (deduplicated)' : 'Source ingested', 'ok'); setContent(''); setTitle(''); setUrl(''); reload() }
    catch (err) { toast.push(errMsg(err), 'err') } finally { setBusy(false) }
  }
  const upload = async (files: FileList | null) => {
    if (!files?.length) return
    try {
      const token = localStorage.getItem('sb_token') || ''
      const fd = new FormData(); Array.from(files).forEach(f => fd.append('files', f))
      const res = await fetch('/api/sources/upload', { method: 'POST', headers: { Authorization: `Bearer ${token}` }, body: fd })
      const j = await res.json()
      if (!res.ok) throw new Error(j.detail || res.statusText)
      toast.push(`Uploaded ${j.uploaded} file(s)`, 'ok'); reload()
    } catch (err) { toast.push(errMsg(err), 'err') }
  }
  const kinds = ['note', 'url', 'pdf', 'markdown', 'article', 'transcript', 'upload']
  const rows = (data || []).filter(x => !filter || s(x.kind).toLowerCase().includes(filter.toLowerCase()) || s(x.title).toLowerCase().includes(filter.toLowerCase()))
  return (<>
    <PageHeader title="Library" sub="Ingest sources — duplicates are detected by content hash." />
    <div className="sb-grid sb-grid-2">
      <div className="sb-card">
        <h2 style={{ marginTop: 0 }}>Add a source</h2>
        <form onSubmit={create}>
          <label className="sb-label" htmlFor="kind">Kind</label>
          <select id="kind" className="sb-select" value={kind} onChange={e => setKind(e.target.value)}>{kinds.map(k => <option key={k} value={k}>{k}</option>)}</select>
          <label className="sb-label" htmlFor="title">Title</label>
          <input id="title" className="sb-input" value={title} onChange={e => setTitle(e.target.value)} />
          <label className="sb-label" htmlFor="url">URL</label>
          <input id="url" className="sb-input" type="url" value={url} onChange={e => setUrl(e.target.value)} />
          <label className="sb-label" htmlFor="content">Content</label>
          <textarea id="content" className="sb-textarea" required minLength={1} value={content} onChange={e => setContent(e.target.value)} placeholder="Paste notes, article text, transcript…" />
          <button className="sb-btn sb-btn-primary" style={{ marginTop: 14 }} disabled={busy}>{busy ? 'Ingesting…' : 'Ingest source'}</button>
        </form>
        <label className="sb-label" htmlFor="upload">Upload files (.pdf .md .txt, max 5 / 2MB each)</label>
        <input id="upload" type="file" accept=".pdf,.md,.txt" multiple onChange={e => upload(e.target.files)} />
      </div>
      <div className="sb-card">
        <div className="sb-row" style={{ justifyContent: 'space-between' }}>
          <h2 style={{ margin: 0 }}>Sources ({rows.length})</h2>
          <input className="sb-input" style={{ maxWidth: 220 }} placeholder="Filter…" aria-label="Filter sources" value={filter} onChange={e => setFilter(e.target.value)} />
        </div>
        {loading ? <LoadingSkeleton /> : error ? <ErrorState message={error} onRetry={reload} />
          : rows.length ? <ul className="sb-list">{rows.map(x => <li key={x.id}><span><Link to={`/sources/${x.id}`}>{s(x.title || x.id)}</Link> <Badge>{s(x.kind)}</Badge>{x.deduplicated ? <Badge tone="warn">dedup</Badge> : null}<div className="sb-small sb-muted">{s(x.chunks ?? 0)} chunks · {s(x.content_hash?.slice(0, 12))}</div></span><Link className="sb-btn" to={`/sources/${x.id}`}>Open</Link></li>)}</ul>
          : <EmptyState title="No sources yet" hint="Add your first source on the left." />}
      </div>
    </div>
  </>)
}

function SourceDetailPage() {
  const { id } = useParams(); const { data, loading, error, reload } = useFetch(() => apiSources.get(id || ''))
  if (loading) return <LoadingSkeleton />
  if (error || !data) return <ErrorState message={error || 'Not found'} onRetry={reload} />
  const chunks: any[] = data.chunks || []
  return (<><PageHeader title={s(data.title || 'Source')} sub={`${s(data.kind)} · hash ${s(data.content_hash)}`} action={<Link className="sb-btn" to="/library">← Library</Link>} />
    <div className="sb-card"><p className="sb-muted">{s(data.url)}</p><pre className="sb-pre">{JSON.stringify(data.meta || {}, null, 2)}</pre></div>
    <h2>Chunks ({chunks.length})</h2>{chunks.map((c: any) => <div key={c.id} className="sb-chunk"><div className="sb-small sb-muted">chunk {c.chunk_index}</div><p style={{ whiteSpace: 'pre-wrap' }}>{c.text}</p></div>)}</>)
}

// ---------- Search ----------
function SearchPage() {
  const [q, setQ] = useState(''); const [kind, setKind] = useState(''); const [res, setRes] = useState<any>(null); const [busy, setBusy] = useState(false); const [error, setError] = useState<string | null>(null)
  const run = async (e?: React.FormEvent) => { e?.preventDefault(); setBusy(true); setError(null); try { setRes(await apiSearch.search(q || ' ', kind)) } catch (err) { setError(errMsg(err)) } finally { setBusy(false) } }
  return (<><PageHeader title="Search" sub="Keyword search with citations — every hit is traceable." />
    <form onSubmit={run} className="sb-card">
      <div className="sb-form-grid">
        <div><label className="sb-label" htmlFor="q">Query</label><input id="q" className="sb-input" required value={q} onChange={e => setQ(e.target.value)} placeholder="e.g. spaced repetition" /></div>
        <div><label className="sb-label" htmlFor="sk">Kind filter (optional)</label><input id="sk" className="sb-input" value={kind} onChange={e => setKind(e.target.value)} placeholder="note / article / …" /></div>
      </div>
      <button className="sb-btn sb-btn-primary" style={{ marginTop: 14 }} disabled={busy}>{busy ? 'Searching…' : 'Search'}</button>
    </form>
    {error ? <ErrorState message={error} /> : res ? (res.results?.length ? res.results.map((r: any) => (
      <div key={r.document_id} className="sb-card" style={{ marginTop: 12 }}>
        <p>{highlight(r.text, q)}</p>
        <div className="sb-row"><span className="sb-code">{s(r.document_id)} · chunk {s(r.chunk_index)}</span><button className="sb-btn sb-btn-ghost" onClick={() => { navigator.clipboard?.writeText(JSON.stringify(r.citation || r, null, 2)); }}>Copy citation</button></div>
      </div>)) : <EmptyState title="No results" hint="Try broader terms or ingest more sources." />) : <EmptyState title="Run a search" hint="Enter a query above." />}</>)
}

// ---------- Research ----------
function ResearchPage() {
  const toast = useToast(); const [query, setQuery] = useState(''); const [out, setOut] = useState<any>(null); const [busy, setBusy] = useState(false); const [error, setError] = useState<string | null>(null)
  const run = async (e: React.FormEvent) => { e.preventDefault(); setBusy(true); setError(null); try { setOut(await apiResearch.run(query)); toast.push('Research complete — human approval required before acting', 'ok') } catch (err) { setError(errMsg(err)) } finally { setBusy(false) } }
  return (<><PageHeader title="Research" sub="Orchestrated multi-agent research. Nothing executes externally without your approval." />
    <form onSubmit={run} className="sb-card"><label className="sb-label" htmlFor="rq">Research question</label>
      <input id="rq" className="sb-input" required value={query} onChange={e => setQuery(e.target.value)} placeholder="What do my notes say about RAG?" />
      <button className="sb-btn sb-btn-primary" style={{ marginTop: 14 }} disabled={busy}>{busy ? 'Researching…' : 'Run research'}</button></form>
    {error ? <ErrorState message={error} /> : out ? (<>
      <div className="sb-banner"><strong>Human approval required.</strong> Review the report below. No GitHub issue, project push, or external action was taken automatically.{out.project_id ? <> Draft project: <Link to={`/projects/${out.project_id}`}>{s(out.project_id)}</Link></> : null}</div>
      <div className="sb-card"><h2 style={{ marginTop: 0 }}>Agent steps ({out.steps?.length})</h2>
        <div className="sb-timeline">{(out.steps || []).map((st: any, i: number) => <div className="step" key={i}><strong>{i + 1}. {s(st.agent)}</strong><pre className="sb-pre">{JSON.stringify(st, null, 2)}</pre></div>)}</div></div>
      <div className="sb-card" style={{ marginTop: 12 }}><h2 style={{ marginTop: 0 }}>Findings</h2>{(out.findings || []).map((f: any, i: number) => <p key={i}>{f.text}</p>)}
        <h3>Gaps</h3><ul>{(out.gaps || []).map((g: any, i: number) => <li key={i}>{s(g)}</li>)}</ul>
        <h3>Next actions</h3><ul>{(out.next_actions || []).map((a: any, i: number) => <li key={i}>{s(a)}</li>)}</ul></div>
    </>) : <EmptyState title="No research yet" hint="Ask a question above." />}</>)
}

// ---------- Agents ----------
function AgentsPage() {
  const toast = useToast(); const { data, loading, error, reload } = useFetch(() => apiAgents.list())
  const [agent, setAgent] = useState('orchestrator'); const [query, setQuery] = useState(''); const [out, setOut] = useState<any>(null); const [busy, setBusy] = useState(false)
  const run = async (e: React.FormEvent) => { e.preventDefault(); setBusy(true); try { setOut(await apiAgents.run(agent, query)); toast.push('Agent run complete', 'ok') } catch (err) { toast.push(errMsg(err), 'err') } finally { setBusy(false) } }
  return (<><PageHeader title="Agents" sub="Specialist agents with explicit roles and permissions." />
    {loading ? <LoadingSkeleton /> : error ? <ErrorState message={error} onRetry={reload} /> : <>
      <div className="sb-grid sb-grid-3">{(data?.agents || []).map((a: any) => <div key={a.name} className="sb-card"><h3 style={{ marginTop: 0 }}>{s(a.name)}</h3><p className="sb-muted">{s(a.role)}</p><p className="sb-small">Permissions: {(a.permissions || []).join(', ')}</p><button className="sb-btn" onClick={() => setAgent(a.name)}>Use in run form</button></div>)}</div>
      <form onSubmit={run} className="sb-card" style={{ marginTop: 16 }}>
        <label className="sb-label" htmlFor="ag">Agent</label><select id="ag" className="sb-select" value={agent} onChange={e => setAgent(e.target.value)}>{(data?.agents || []).map((a: any) => <option key={a.name} value={a.name}>{a.name}</option>)}</select>
        <label className="sb-label" htmlFor="aq">Query</label><input id="aq" className="sb-input" required value={query} onChange={e => setQuery(e.target.value)} />
        <button className="sb-btn sb-btn-primary" style={{ marginTop: 14 }} disabled={busy}>{busy ? 'Running…' : 'Run agent'}</button>
      </form>
      {out ? <div className="sb-card" style={{ marginTop: 12 }}><h2 style={{ marginTop: 0 }}>Output</h2><pre className="sb-pre">{JSON.stringify(out, null, 2)}</pre></div> : null}
    </>}</>)
}

// ---------- Projects ----------
function ProjectsPage() {
  const toast = useToast(); const { data, loading, error, reload } = useFetch(() => apiProjects.list())
  const [title, setTitle] = useState(''); const [desc, setDesc] = useState('')
  const create = async (e: React.FormEvent) => { e.preventDefault(); try { await apiProjects.create(title, desc); toast.push('Project created', 'ok'); reload() } catch (err) { toast.push(errMsg(err), 'err') } }
  return (<><PageHeader title="Projects" sub="Turn research into executable work." />
    <form onSubmit={create} className="sb-card"><label className="sb-label" htmlFor="pt">Title</label><input id="pt" className="sb-input" required value={title} onChange={e => setTitle(e.target.value)} />
      <label className="sb-label" htmlFor="pd">Description</label><textarea id="pd" className="sb-textarea" value={desc} onChange={e => setDesc(e.target.value)} />
      <button className="sb-btn sb-btn-primary" style={{ marginTop: 14 }}>Create project</button></form>
    {loading ? <LoadingSkeleton /> : error ? <ErrorState message={error} onRetry={reload} /> : (data?.length ? <ul className="sb-list" style={{ marginTop: 12 }}>{data.map((p: any) => <li key={p.id}><span><Link to={`/projects/${p.id}`}>{s(p.title)}</Link> <Badge>{s(p.status)}</Badge></span><Link className="sb-btn" to={`/projects/${p.id}`}>Open</Link></li>)}</ul> : <EmptyState title="No projects yet" hint="Create one above or run research." />)}</>)
}

function ProjectDetailPage() {
  const { id } = useParams(); const toast = useToast(); const { data, loading, error, reload } = useFetch(() => apiProjects.get(id || ''))
  const [t, setT] = useState({ title: '', body: '', status: 'todo', assignee: '' }); const [draft, setDraft] = useState<any>(null)
  const add = async (e: React.FormEvent) => { e.preventDefault(); try { await apiProjects.addTask(id || '', t); toast.push('Task added', 'ok'); setT({ title: '', body: '', status: 'todo', assignee: '' }); reload() } catch (err) { toast.push(errMsg(err), 'err') } }
  const mkDraft = async () => { try { setDraft(await apiProjects.issueDraft(id || '')) } catch (err) { toast.push(errMsg(err), 'err') } }
  if (loading) return <LoadingSkeleton />
  if (error || !data) return <ErrorState message={error || 'Not found'} onRetry={reload} />
  return (<><PageHeader title={s(data.title)} sub={s(data.description)} action={<Link className="sb-btn" to="/projects">← Projects</Link>} />
    <div className="sb-card"><h2 style={{ marginTop: 0 }}>Tasks ({data.tasks?.length || 0})</h2>
      {(data.tasks || []).map((x: any) => <p key={x.id}><Badge>{s(x.status)}</Badge> <strong>{s(x.title)}</strong>{x.assignee ? <> · @{s(x.assignee)}</> : null}</p>)}
      <form onSubmit={add}>
        <label className="sb-label" htmlFor="tt">New task title</label><input id="tt" className="sb-input" required value={t.title} onChange={e => setT({ ...t, title: e.target.value })} />
        <label className="sb-label" htmlFor="tb">Body</label><textarea id="tb" className="sb-textarea" value={t.body} onChange={e => setT({ ...t, body: e.target.value })} />
        <label className="sb-label" htmlFor="ts">Status</label><select id="ts" className="sb-select" value={t.status} onChange={e => setT({ ...t, status: e.target.value })}><option value="todo">todo</option><option value="doing">doing</option><option value="done">done</option></select>
        <label className="sb-label" htmlFor="ta">Assignee</label><input id="ta" className="sb-input" value={t.assignee} onChange={e => setT({ ...t, assignee: e.target.value })} />
        <button className="sb-btn sb-btn-primary" style={{ marginTop: 14 }}>Add task</button></form></div>
    <div className="sb-card" style={{ marginTop: 12 }}><h2 style={{ marginTop: 0 }}>GitHub issue draft (text only — nothing pushed)</h2>
      <button className="sb-btn" onClick={mkDraft}>Generate draft</button>
      {draft ? <pre className="sb-pre" style={{ marginTop: 10 }}>{draft.body}</pre> : null}</div></>)
}

// ---------- Integrations ----------
function IntegrationsPage() {
  const { data, loading, error, reload } = useFetch(() => apiIntegrations.list())
  return (<><PageHeader title="Integrations" sub="Connect your platforms. OAuth is per-provider and user-controlled." />
    {loading ? <LoadingSkeleton /> : error ? <ErrorState message={error} onRetry={reload} /> : <>
      <div className="sb-grid sb-grid-3">{(data?.integrations || []).map((x: any) => <div key={x.name} className="sb-card"><h3 style={{ marginTop: 0 }}>{s(x.name)}</h3><Badge tone={x.status === 'connected' ? 'ok' : 'warn'}>{s(x.status)}</Badge><p className="sb-small sb-muted" style={{ marginTop: 8 }}>{x.requires_oauth ? 'Requires OAuth credentials to ingest.' : 'Local ingestion only.'}</p></div>)}</div>
      <div className="sb-card" style={{ marginTop: 16 }}><h2 style={{ marginTop: 0 }}>Ingestion contract</h2><pre className="sb-pre">{JSON.stringify(data?.contract || {}, null, 2)}</pre><p className="sb-small sb-muted">Until OAuth is configured, adapters report not_configured rather than pretending to work.</p></div></>}</>)
}

// ---------- Graph ----------
function GraphPage() {
  const toast = useToast(); const { data, loading, error, reload } = useFetch(() => apiOptional.graph())
  const [name, setName] = useState(''); const [kind, setKind] = useState('concept')
  const add = async (e: React.FormEvent) => { e.preventDefault(); try { await apiOptional.graphAddEntity({ name, kind }); toast.push('Entity added', 'ok'); reload() } catch (err) { toast.push(errMsg(err), 'err') } }
  const entities: any[] = (data?.entities as any[]) || []; const rels: any[] = (data?.relationships as any[]) || []
  const pos = (i: number, n: number) => { const a = (2 * Math.PI * i) / Math.max(n, 1); return { x: 300 + 240 * Math.cos(a), y: 300 + 240 * Math.sin(a) } }
  const byId = new Map(entities.map(e => [e.id, e]))
  return (<><PageHeader title="Knowledge Graph" sub="Procedural entity / relationship browser." />
    <form onSubmit={add} className="sb-card"><div className="sb-form-grid"><div><label className="sb-label" htmlFor="en">Entity name</label><input id="en" className="sb-input" required value={name} onChange={e => setName(e.target.value)} /></div>
      <div><label className="sb-label" htmlFor="ek">Kind</label><input id="ek" className="sb-input" value={kind} onChange={e => setKind(e.target.value)} /></div></div>
      <button className="sb-btn sb-btn-primary" style={{ marginTop: 14 }}>Add entity</button></form>
    {loading ? <LoadingSkeleton /> : error ? <ErrorState message={error} onRetry={reload} /> : entities.length ? (<>
      <div className="sb-graph-wrap" style={{ marginTop: 12 }}><svg width={600} height={600} role="img" aria-label="Knowledge graph visualization" style={{ maxWidth: '100%' }}>
        {rels.map((r: any, i: number) => { const a = byId.get(r.source_entity_id), b = byId.get(r.target_entity_id); if (!a || !b) return null; const pa = pos(entities.indexOf(a), entities.length), pb = pos(entities.indexOf(b), entities.length); return <g key={r.id || i}><line x1={pa.x} y1={pa.y} x2={pb.x} y2={pb.y} stroke="var(--border)" /><text x={(pa.x + pb.x) / 2} y={(pa.y + pb.y) / 2} fill="var(--muted)" fontSize="11" textAnchor="middle">{s(r.relation)}</text></g> })}
        {entities.map((e: any, i: number) => { const p = pos(i, entities.length); return <g key={e.id}><circle cx={p.x} cy={p.y} r="34" fill="var(--surface2)" stroke="var(--accent)" /><text x={p.x} y={p.y + 4} textAnchor="middle" fill="var(--text)" fontSize="12">{s(e.name).slice(0, 14)}</text></g> })}
      </svg></div>
      <ul className="sb-list">{rels.map((r: any, i: number) => <li key={r.id || i}><span>{s(byId.get(r.source_entity_id)?.name)} → {s(byId.get(r.target_entity_id)?.name)}</span><Badge>{s(r.relation)}</Badge></li>)}</ul>
    </>) : <EmptyState title="Graph is empty" hint="Add an entity above or run research to extract entities." />}</>)
}

// ---------- Memory ----------
function MemoryPage() {
  const toast = useToast(); const { data, loading, error, reload } = useFetch(() => apiOptional.memoryList())
  const [key, setKey] = useState(''); const [value, setValue] = useState(''); const [editing, setEditing] = useState<any>(null); const [confirmId, setConfirmId] = useState<string | null>(null)
  const create = async (e: React.FormEvent) => { e.preventDefault(); try { await apiOptional.memoryCreate({ key, value }); toast.push('Memory saved', 'ok'); setKey(''); setValue(''); reload() } catch (err) { toast.push(errMsg(err), 'err') } }
  const saveEdit = async () => { try { await apiOptional.memoryUpdate(editing.id, { value: editing.value }); toast.push('Memory updated', 'ok'); setEditing(null); reload() } catch (err) { toast.push(errMsg(err), 'err') } }
  const del = async (id: string) => { try { await apiOptional.memoryDelete(id); toast.push('Deleted', 'ok'); setConfirmId(null); reload() } catch (err) { toast.push(errMsg(err), 'err') } }
  const items: any[] = Array.isArray(data) ? data : (data as any)?.items || []
  return (<><PageHeader title="Memory" sub="Inspectable, correctable personal memory. AI inferences are never stored as user facts without provenance." />
    <form onSubmit={create} className="sb-card"><div className="sb-form-grid"><div><label className="sb-label" htmlFor="mk">Key</label><input id="mk" className="sb-input" required value={key} onChange={e => setKey(e.target.value)} /></div>
      <div><label className="sb-label" htmlFor="mv">Value</label><input id="mv" className="sb-input" required value={value} onChange={e => setValue(e.target.value)} /></div></div>
      <button className="sb-btn sb-btn-primary" style={{ marginTop: 14 }}>Save memory</button></form>
    {loading ? <LoadingSkeleton /> : error ? <ErrorState message={error} onRetry={reload} /> : items.length ? <ul className="sb-list" style={{ marginTop: 12 }}>{items.map((m: any) => <li key={m.id}><span><strong>{s(m.key)}</strong><div className="sb-small sb-muted">{s(m.value)}</div></span><span className="sb-row"><button className="sb-btn" onClick={() => setEditing(m)}>Edit</button><button className="sb-btn sb-btn-danger" onClick={() => setConfirmId(m.id)}>Delete</button></span></li>)}</ul> : <EmptyState title="No memories yet" hint="Save one above." />}
    {editing ? <Modal title="Edit memory" onClose={() => setEditing(null)}><label className="sb-label" htmlFor="ev">Value</label><input id="ev" className="sb-input" value={editing.value} onChange={e => setEditing({ ...editing, value: e.target.value })} /><div className="sb-row" style={{ marginTop: 14 }}><button className="sb-btn sb-btn-primary" onClick={saveEdit}>Save</button><button className="sb-btn" onClick={() => setEditing(null)}>Cancel</button></div></Modal> : null}
    {confirmId ? <ConfirmDialog title="Delete memory?" body="This permanently deletes the memory. This cannot be undone." onConfirm={() => del(confirmId)} onCancel={() => setConfirmId(null)} /> : null}</>)
}

// ---------- Activity ----------
function ActivityPage() {
  const [page, setPage] = useState(1); const { data, loading, error, reload } = useFetch(() => apiOptional.audit(page, 20), [page])
  const events: any[] = data?.events || []
  return (<><PageHeader title="Activity & Audit" sub="Every important action is auditable." />
    {loading ? <LoadingSkeleton /> : error ? <ErrorState message={error} onRetry={reload} /> : events.length ? (<>
      <ul className="sb-list">{events.map((a: any, i: number) => <li key={a.id || i}><span><strong>{s(a.action)}</strong><div className="sb-small sb-muted">{s(a.target)} · {s(a.created_at || a.timestamp)}</div></span><span className="sb-small sb-muted">{JSON.stringify(a.detail || {})}</span></li>)}</ul>
      <div className="sb-pagination"><button className="sb-btn" disabled={page <= 1} onClick={() => setPage(p => p - 1)}>← Prev</button><span>Page {page}</span><button className="sb-btn" disabled={events.length < 20} onClick={() => setPage(p => p + 1)}>Next →</button></div>
    </>) : <EmptyState title="No audit events" hint="Actions you take will appear here." />}</>)
}

// ---------- Settings ----------
function SettingsPage() {
  const { theme, setTheme } = useApp()
  return (<><PageHeader title="Settings" sub="Appearance and session." />
    <div className="sb-card"><h2 style={{ marginTop: 0 }}>Appearance</h2>
      <div className="sb-row"><button className="sb-btn" aria-pressed={theme === 'dark'} onClick={() => setTheme('dark')}>🌙 Dark</button><button className="sb-btn" aria-pressed={theme === 'light'} onClick={() => setTheme('light')}>☀ Light</button></div></div>
    <div className="sb-card" style={{ marginTop: 12 }}><h2 style={{ marginTop: 0 }}>API</h2><p className="sb-muted">Base URL: <span className="sb-code">/api</span> (Vite proxy → http://localhost:8000)</p><p className="sb-small sb-muted">Health: <span className="sb-code">GET /api/health</span></p></div></>)
}

// ---------- Root ----------
export default function App() {
  return (
    <ThemeProvider><ToastProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/" element={<RequireAuth><DashboardPage /></RequireAuth>} />
          <Route path="/library" element={<RequireAuth><LibraryPage /></RequireAuth>} />
          <Route path="/sources/:id" element={<RequireAuth><SourceDetailPage /></RequireAuth>} />
          <Route path="/search" element={<RequireAuth><SearchPage /></RequireAuth>} />
          <Route path="/research" element={<RequireAuth><ResearchPage /></RequireAuth>} />
          <Route path="/agents" element={<RequireAuth><AgentsPage /></RequireAuth>} />
          <Route path="/projects" element={<RequireAuth><ProjectsPage /></RequireAuth>} />
          <Route path="/projects/:id" element={<RequireAuth><ProjectDetailPage /></RequireAuth>} />
          <Route path="/integrations" element={<RequireAuth><IntegrationsPage /></RequireAuth>} />
          <Route path="/graph" element={<RequireAuth><GraphPage /></RequireAuth>} />
          <Route path="/memory" element={<RequireAuth><MemoryPage /></RequireAuth>} />
          <Route path="/activity" element={<RequireAuth><ActivityPage /></RequireAuth>} />
          <Route path="/settings" element={<RequireAuth><SettingsPage /></RequireAuth>} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </ToastProvider></ThemeProvider>
  )
}
