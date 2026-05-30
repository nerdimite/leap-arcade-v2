import { HttpResponse, http } from "msw"
import { describe, expect, it } from "vitest"

import { server } from "@/test/msw-server"

import { getPlayerSessions, PlayerSessionsApiError } from "./players"

describe("getPlayerSessions", () => {
  it("GETs /api/players/me/sessions and parses the body", async () => {
    server.use(
      http.get(
        ({ request }) =>
          new URL(request.url).pathname.endsWith("/api/players/me/sessions"),
        () =>
          HttpResponse.json([
            { game_id: "rapid_fire", status: "active", score: null },
            { game_id: "wiki", status: "completed", score: 350 },
          ])
      )
    )

    const rows = await getPlayerSessions()
    expect(rows).toEqual([
      { game_id: "rapid_fire", status: "active", score: null },
      { game_id: "wiki", status: "completed", score: 350 },
    ])
  })

  it("throws PlayerSessionsApiError when the server returns 401", async () => {
    server.use(
      http.get(
        ({ request }) =>
          new URL(request.url).pathname.endsWith("/api/players/me/sessions"),
        () => HttpResponse.json({ detail: "nope" }, { status: 401 })
      )
    )

    await expect(getPlayerSessions()).rejects.toMatchObject({ status: 401 })
    await expect(getPlayerSessions()).rejects.toBeInstanceOf(
      PlayerSessionsApiError
    )
  })
})
