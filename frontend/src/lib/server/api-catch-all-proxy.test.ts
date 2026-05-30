import { NextRequest } from "next/server"
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest"

import { forwardApiToBackend } from "./api-catch-all-proxy"

describe("forwardApiToBackend", () => {
  const originalFetch = globalThis.fetch

  beforeEach(() => {
    vi.restoreAllMocks()
  })

  afterEach(() => {
    globalThis.fetch = originalFetch
  })

  it("forwards GET to FastAPI with Authorization from token cookie", async () => {
    const fetchMock = vi.fn(
      async () => new Response(JSON.stringify({ ok: true }), { status: 200 })
    )
    globalThis.fetch = fetchMock as unknown as typeof fetch

    const req = new NextRequest("http://localhost:3000/api/leaderboard", {
      method: "GET",
      headers: { cookie: "token=my.jwt.token" },
    })

    await forwardApiToBackend(req, ["leaderboard"], {
      backendOrigin: "http://fastapi:8000",
    })

    expect(fetchMock).toHaveBeenCalledTimes(1)
    const first = fetchMock.mock.calls[0]
    expect(first).toBeDefined()
    const [url, init] = first as unknown as [URL | string, RequestInit]
    expect(String(url)).toBe("http://fastapi:8000/leaderboard")
    const headers = new Headers(init.headers)
    expect(headers.get("Authorization")).toBe("Bearer my.jwt.token")
  })

  it("forwards POST with body intact", async () => {
    const fetchMock = vi.fn(async () => new Response(null, { status: 204 }))
    globalThis.fetch = fetchMock as unknown as typeof fetch

    const req = new NextRequest(
      "http://localhost:3000/api/games/rapid-fire/play",
      {
        method: "POST",
        headers: {
          cookie: "token=tok",
          "content-type": "application/json",
        },
        body: JSON.stringify({ game_session_id: "abc" }),
      }
    )

    await forwardApiToBackend(req, ["games", "rapid-fire", "play"], {
      backendOrigin: "http://fastapi:8000",
    })

    expect(fetchMock).toHaveBeenCalledTimes(1)
    const firstPost = fetchMock.mock.calls[0]
    expect(firstPost).toBeDefined()
    const [, init] = firstPost as unknown as [string, RequestInit]
    expect(init.method).toBe("POST")
    const posted = init.body
    expect(typeof posted).toBe("object")
    expect(new TextDecoder().decode(posted as ArrayBuffer)).toBe(
      JSON.stringify({ game_session_id: "abc" })
    )
    const headers = new Headers(init.headers)
    expect(headers.get("Authorization")).toBe("Bearer tok")
    expect(headers.get("content-type")).toContain("application/json")
  })

  it("strips the browser-only /api prefix for nested FastAPI paths", async () => {
    const fetchMock = vi.fn(
      async () => new Response(JSON.stringify([]), { status: 200 })
    )
    globalThis.fetch = fetchMock as unknown as typeof fetch

    const req = new NextRequest(
      "http://localhost:3000/api/players/me/sessions",
      {
        method: "GET",
        headers: { cookie: "token=player.jwt" },
      }
    )

    await forwardApiToBackend(req, ["players", "me", "sessions"], {
      backendOrigin: "http://fastapi:8000",
    })

    expect(fetchMock).toHaveBeenCalledTimes(1)
    const first = fetchMock.mock.calls[0]
    expect(first).toBeDefined()
    const [url] = first as unknown as [URL | string, RequestInit]
    expect(String(url)).toBe("http://fastapi:8000/players/me/sessions")
  })

  it("returns 401 when token cookie is absent (non-login path)", async () => {
    const fetchMock = vi.fn()
    globalThis.fetch = fetchMock as unknown as typeof fetch

    const req = new NextRequest("http://localhost:3000/api/leaderboard", {
      method: "GET",
    })

    const res = await forwardApiToBackend(req, ["leaderboard"], {
      backendOrigin: "http://fastapi:8000",
    })

    expect(res.status).toBe(401)
    expect(fetchMock).not.toHaveBeenCalled()
  })
})
