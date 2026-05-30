import { describe, expect, it } from "vitest"

import { LEADERBOARD_POLL_INTERVAL_MS } from "@/lib/constants"

import { getLeaderboardQueryOptions } from "./query-options"

describe("getLeaderboardQueryOptions", () => {
  it("sets refetchInterval to LEADERBOARD_POLL_INTERVAL_MS", () => {
    expect(getLeaderboardQueryOptions().refetchInterval).toBe(
      LEADERBOARD_POLL_INTERVAL_MS
    )
  })
})
