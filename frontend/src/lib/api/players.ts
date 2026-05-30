import {
  type PlayerSessionsResponse,
  PlayerSessionsResponseSchema,
} from "@/services/players/schema"

export const PLAYER_SESSIONS_QUERY_KEY = ["players", "me", "sessions"] as const

export class PlayerSessionsApiError extends Error {
  readonly status: number

  constructor(status: number, message = "Failed to load sessions") {
    super(message)
    this.name = "PlayerSessionsApiError"
    this.status = status
  }
}

function playerSessionsUrl(): string {
  if (typeof window !== "undefined" && window.location?.origin) {
    return new URL("/api/players/me/sessions", window.location.origin).href
  }
  return "http://localhost:3000/api/players/me/sessions"
}

/** GET `/api/players/me/sessions` — forwards to FastAPI with Bearer from httpOnly cookie. */
export async function getPlayerSessions(
  init?: RequestInit
): Promise<PlayerSessionsResponse> {
  const res = await fetch(playerSessionsUrl(), {
    ...init,
    method: "GET",
    headers: {
      accept: "application/json",
      ...init?.headers,
    },
    cache: "no-store",
  })

  if (!res.ok) {
    throw new PlayerSessionsApiError(res.status)
  }

  const json: unknown = await res.json()
  return PlayerSessionsResponseSchema.parse(json)
}
