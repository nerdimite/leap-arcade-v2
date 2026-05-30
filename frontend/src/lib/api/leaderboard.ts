import {
  type LeaderboardResponse,
  LeaderboardResponseSchema,
} from "@/services/leaderboard/schema"

export const LEADERBOARD_QUERY_KEY = ["leaderboard"] as const

export class LeaderboardApiError extends Error {
  readonly status: number

  constructor(status: number, message = "Failed to load leaderboard") {
    super(message)
    this.name = "LeaderboardApiError"
    this.status = status
  }
}

function leaderboardUrl(): string {
  if (typeof window !== "undefined" && window.location?.origin) {
    return new URL("/api/leaderboard", window.location.origin).href
  }
  return "http://localhost:3000/api/leaderboard"
}

/** GET `/api/leaderboard` — forwards to FastAPI with Bearer from httpOnly cookie. */
export async function getLeaderboard(
  init?: RequestInit
): Promise<LeaderboardResponse> {
  const res = await fetch(leaderboardUrl(), {
    ...init,
    method: "GET",
    headers: {
      accept: "application/json",
      ...init?.headers,
    },
    cache: "no-store",
  })

  if (!res.ok) {
    throw new LeaderboardApiError(res.status)
  }

  const json: unknown = await res.json()
  return LeaderboardResponseSchema.parse(json)
}
