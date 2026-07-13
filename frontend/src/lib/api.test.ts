import { afterEach, describe, expect, it, vi } from 'vitest'

import { getLifePulse, getOverview } from './api'


describe('API client', () => {
  afterEach(() => {
    vi.useRealTimers()
    vi.unstubAllGlobals()
  })

  it('aborts requests that exceed the configured timeout', async () => {
    vi.useFakeTimers()
    vi.stubGlobal(
      'fetch',
      vi.fn(() =>
        Promise.reject(new DOMException('Aborted', 'AbortError')),
      ),
    )

    const request = getOverview()
    await vi.advanceTimersByTimeAsync(15_001)

    await expect(request).rejects.toThrow('Ariva API timeout after 15000ms')
  })

  it('surfaces JSON error detail from the backend', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn(() =>
        Promise.resolve(
          new Response(JSON.stringify({ detail: 'Rate limit exceeded' }), {
            headers: { 'Content-Type': 'application/json' },
            status: 429,
            statusText: 'Too Many Requests',
          }),
        ),
      ),
    )

    await expect(getOverview()).rejects.toThrow('Ariva API 429: Rate limit exceeded')
  })

  it('adds bearer tokens for authenticated account requests', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn((...args: Parameters<typeof fetch>) => {
        const init = args[1]
        const headers = new Headers(init?.headers)
        expect(headers.get('Authorization')).toBe('Bearer test-token')
        return Promise.resolve(
          new Response(
            JSON.stringify({
              generated_at: '2026-05-21T06:10:00Z',
              profile: {
                id: 1,
                auth_sub: 'test-user',
                email: 'test@ariva.local',
                display_name: 'Ariva Test User',
                photo_url: null,
                default_locale: 'en',
                district: 'Colombo',
                profile: 'commuter',
                created_at: '2026-05-21T06:10:00Z',
                updated_at: '2026-05-21T06:10:00Z',
              },
              overview: {},
              saved_items: [],
              alert_rules: [],
              notifications: [],
              unread_count: 0,
            }),
            { headers: { 'Content-Type': 'application/json' } },
          ),
        )
      }),
    )

    await expect(getLifePulse('test-token')).resolves.toMatchObject({ unread_count: 0 })
  })
})
