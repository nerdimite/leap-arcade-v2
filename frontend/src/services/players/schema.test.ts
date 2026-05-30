import { describe, expect, it } from "vitest"

import { PlayerSessionSchema, PlayerSessionsResponseSchema } from "./schema"

describe("PlayerSessionSchema", () => {
  it("parses session row with null score", () => {
    const parsed = PlayerSessionSchema.parse({
      game_id: "rapid_fire",
      status: "active",
      score: null,
    })
    expect(parsed).toEqual({
      game_id: "rapid_fire",
      status: "active",
      score: null,
    })
  })

  it("parses session row with numeric score", () => {
    const parsed = PlayerSessionSchema.parse({
      game_id: "rapid_fire",
      status: "completed",
      score: 350,
    })
    expect(parsed.score).toBe(350)
  })
})

describe("PlayerSessionsResponseSchema", () => {
  it("parses a list of sessions", () => {
    const parsed = PlayerSessionsResponseSchema.parse([
      { game_id: "wiki", status: "active", score: null },
      { game_id: "rapid_fire", status: "completed", score: 350 },
    ])
    expect(parsed).toHaveLength(2)
  })
})
