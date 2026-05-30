import type {
  WikiNavigateResponse,
  WikiPlayResponse,
} from "@/services/wiki/schema"
import {
  WikiNavigateResponseSchema,
  WikiPlayResponseSchema,
} from "@/services/wiki/schema"

export class WikiApiError extends Error {
  readonly status: number

  constructor(status: number, message = "Wiki request failed") {
    super(message)
    this.name = "WikiApiError"
    this.status = status
  }
}

export type PostWikiPlayOptions = {
  baseUrl?: string
  cookieHeader?: string
}

function resolveOrigin(baseUrl?: string): string {
  if (baseUrl) {
    return baseUrl.replace(/\/$/, "")
  }
  if (typeof window !== "undefined" && window.location?.origin) {
    return window.location.origin
  }
  return "http://localhost:3000"
}

function playHref(origin: string): string {
  return new URL("/api/games/wiki/play", origin).href
}

/** POST `/api/games/wiki/play` (proxied to FastAPI). */
export async function postWikiPlay(
  options: PostWikiPlayOptions = {}
): Promise<WikiPlayResponse> {
  const origin = resolveOrigin(options.baseUrl)
  const headers: Record<string, string> = {
    accept: "application/json",
  }
  if (options.cookieHeader) {
    headers.cookie = options.cookieHeader
  }

  const res = await fetch(playHref(origin), {
    method: "POST",
    headers,
    credentials: options.cookieHeader ? "omit" : "include",
  })

  if (!res.ok) {
    throw new WikiApiError(res.status)
  }

  const json: unknown = await res.json()
  return WikiPlayResponseSchema.parse(json)
}

function navigateHref(origin: string): string {
  return new URL("/api/games/wiki/navigate", origin).href
}

function backHref(origin: string): string {
  return new URL("/api/games/wiki/back", origin).href
}

function abandonHref(origin: string): string {
  return new URL("/api/games/wiki/abandon", origin).href
}

/** POST `/api/games/wiki/navigate` (proxied to FastAPI). */
export async function postWikiNavigate(
  title: string,
  options: PostWikiPlayOptions = {}
): Promise<WikiNavigateResponse> {
  const origin = resolveOrigin(options.baseUrl)
  const headers: Record<string, string> = {
    accept: "application/json",
    "content-type": "application/json",
  }
  if (options.cookieHeader) {
    headers.cookie = options.cookieHeader
  }

  const res = await fetch(navigateHref(origin), {
    method: "POST",
    headers,
    credentials: options.cookieHeader ? "omit" : "include",
    body: JSON.stringify({ title }),
  })

  if (!res.ok) {
    throw new WikiApiError(res.status)
  }

  const json: unknown = await res.json()
  return WikiNavigateResponseSchema.parse(json)
}

/** POST `/api/games/wiki/back` (proxied to FastAPI). */
export async function postWikiBack(
  options: PostWikiPlayOptions = {}
): Promise<WikiNavigateResponse> {
  const origin = resolveOrigin(options.baseUrl)
  const headers: Record<string, string> = {
    accept: "application/json",
  }
  if (options.cookieHeader) {
    headers.cookie = options.cookieHeader
  }

  const res = await fetch(backHref(origin), {
    method: "POST",
    headers,
    credentials: options.cookieHeader ? "omit" : "include",
  })

  if (!res.ok) {
    throw new WikiApiError(res.status)
  }

  const json: unknown = await res.json()
  return WikiNavigateResponseSchema.parse(json)
}

/** POST `/api/games/wiki/abandon` — same terminal shape as play when state is abandoned. */
export async function postWikiAbandon(
  options: PostWikiPlayOptions = {}
): Promise<WikiPlayResponse> {
  const origin = resolveOrigin(options.baseUrl)
  const headers: Record<string, string> = {
    accept: "application/json",
  }
  if (options.cookieHeader) {
    headers.cookie = options.cookieHeader
  }

  const res = await fetch(abandonHref(origin), {
    method: "POST",
    headers,
    credentials: options.cookieHeader ? "omit" : "include",
  })

  if (!res.ok) {
    throw new WikiApiError(res.status)
  }

  const json: unknown = await res.json()
  return WikiPlayResponseSchema.parse(json)
}

function timeoutHref(origin: string): string {
  return new URL("/api/games/wiki/timeout", origin).href
}

/** POST `/api/games/wiki/timeout` — server timer sync / authoritative timeout. */
export async function postWikiTimeout(
  options: PostWikiPlayOptions = {}
): Promise<WikiPlayResponse> {
  const origin = resolveOrigin(options.baseUrl)
  const headers: Record<string, string> = {
    accept: "application/json",
  }
  if (options.cookieHeader) {
    headers.cookie = options.cookieHeader
  }

  const res = await fetch(timeoutHref(origin), {
    method: "POST",
    headers,
    credentials: options.cookieHeader ? "omit" : "include",
  })

  if (!res.ok) {
    throw new WikiApiError(res.status)
  }

  const json: unknown = await res.json()
  return WikiPlayResponseSchema.parse(json)
}
