import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { ApiError, apiAuth, apiSearch, setToken, getToken } from './client'

const jsonResponse = (body: unknown, ok = true, status = 200) => {
  return {
    ok,
    status,
    statusText: ok ? 'OK' : 'Error',
    text: async () => JSON.stringify(body),
  } as Response
}

describe('ApiError parsing', () => {
  beforeEach(() => {
    localStorage.clear()
  })

  it('parses FastAPI detail field on error', async () => {
    vi.stubGlobal('fetch', vi.fn(async () => jsonResponse({ detail: 'Not found' }, false, 404)))
    await expect(apiAuth.login('a@b.com', 'password123')).rejects.toThrowError(ApiError)
    try {
      await apiAuth.login('a@b.com', 'password123')
      throw new Error('unreachable')
    } catch (e) {
      expect(e).toBeInstanceOf(ApiError)
      const err = e as ApiError
      expect(err.status).toBe(404)
      expect(err.message).toBe('Not found')
      expect(err.body).toContain('Not found')
    }
  })

  it('falls back to raw text when body is not JSON', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn(async () => ({ ok: false, status: 500, statusText: 'Server Error', text: async () => 'plain failure' }) as Response),
    )
    await expect(apiAuth.login('a@b.com', 'password123')).rejects.toMatchObject({
      name: 'ApiError',
      status: 500,
      message: 'plain failure',
    })
  })

  it('wraps network errors as ApiError with status 0', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn(async () => {
        throw new TypeError('failed to fetch')
      }),
    )
    await expect(apiAuth.login('a@b.com', 'password123')).rejects.toMatchObject({
      name: 'ApiError',
      status: 0,
    })
    try {
      await apiAuth.login('a@b.com', 'password123')
      throw new Error('unreachable')
    } catch (e) {
      expect((e as ApiError).message).toContain('Network error')
    }
  })

  it('returns parsed JSON on success', async () => {
    vi.stubGlobal('fetch', vi.fn(async () => jsonResponse({ access_token: 'tok', token_type: 'bearer' })))
    const r = await apiAuth.login('a@b.com', 'password123')
    expect(r.access_token).toBe('tok')
  })
})

describe('token header', () => {
  beforeEach(() => {
    localStorage.clear()
  })
  afterEach(() => {
    vi.unstubAllGlobals()
  })

  it('setToken/getToken round-trips via localStorage', () => {
    setToken('secret123')
    expect(getToken()).toBe('secret123')
    setToken(null)
    expect(getToken()).toBeNull()
  })

  it('attaches Authorization Bearer header when token present', async () => {
    setToken('secret123')
    const fetchMock = vi.fn(async () => jsonResponse({ query: 'q', count: 0, results: [], citations: [] }))
    vi.stubGlobal('fetch', fetchMock)
    await apiSearch.search('hello')
    const init = (fetchMock.mock.calls[0] as unknown as [string, RequestInit])[1]
    expect((init.headers as Record<string, string>).Authorization).toBe('Bearer secret123')
  })

  it('omits Authorization header when no token', async () => {
    const fetchMock = vi.fn(async () => jsonResponse({ query: 'q', count: 0, results: [], citations: [] }))
    vi.stubGlobal('fetch', fetchMock)
    await apiSearch.search('hello')
    const init = (fetchMock.mock.calls[0] as unknown as [string, RequestInit])[1]
    expect((init.headers as Record<string, string>).Authorization).toBeUndefined()
  })
})

describe('search URL building', () => {
  beforeEach(() => {
    localStorage.clear()
  })
  afterEach(() => {
    vi.unstubAllGlobals()
  })

  it('builds /api/search?q=...&limit=... with encoding', async () => {
    const fetchMock = vi.fn(async () => jsonResponse({ query: 'spaced repetition', count: 0, results: [], citations: [] }))
    vi.stubGlobal('fetch', fetchMock)
    await apiSearch.search('spaced repetition')
    expect((fetchMock.mock.calls[0] as unknown as [string, RequestInit])[0]).toBe('/api/search?q=spaced+repetition&limit=20')
  })

  it('adds kind param only when provided and respects limit', async () => {
    const fetchMock = vi.fn(async () => jsonResponse({ query: 'x', count: 0, results: [], citations: [] }))
    vi.stubGlobal('fetch', fetchMock)
    await apiSearch.search('x', 'note', 5)
    const url = (fetchMock.mock.calls[0] as unknown as [string, RequestInit])[0]
    expect(url).toContain('kind=note')
    expect(url).toContain('limit=5')
  })

  it('omits kind param when empty', async () => {
    const fetchMock = vi.fn(async () => jsonResponse({ query: 'x', count: 0, results: [], citations: [] }))
    vi.stubGlobal('fetch', fetchMock)
    await apiSearch.search('x', '')
    const url = (fetchMock.mock.calls[0] as unknown as [string, RequestInit])[0]
    expect(url).not.toContain('kind=')
  })
})
