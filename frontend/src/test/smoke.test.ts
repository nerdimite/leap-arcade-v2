import { HttpResponse, http } from "msw"
import { describe, expect, it } from "vitest"

import { server } from "./msw-server"

describe("test stack", () => {
  it("runs a trivial assertion", () => {
    expect(1 + 1).toBe(2)
  })

  it("msw intercepts fetch", async () => {
    server.use(
      http.get("https://msw-smoke.test/ping", () =>
        HttpResponse.json({ hello: "world" })
      )
    )

    const res = await fetch("https://msw-smoke.test/ping")
    expect(await res.json()).toEqual({ hello: "world" })
  })
})
