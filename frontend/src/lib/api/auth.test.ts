import { HttpResponse, http } from "msw"
import { describe, expect, it } from "vitest"

import { server } from "@/test/msw-server"

import { postLogin } from "./auth"

describe("postLogin", () => {
  it("posts corp_id and event_code to Next login route", async () => {
    server.use(
      http.post(
        ({ request }) =>
          new URL(request.url).pathname.endsWith("/api/auth/login"),
        async ({ request }) => {
          expect(request.headers.get("content-type")).toContain(
            "application/json"
          )
          expect(await request.json()).toEqual({
            corp_id: "player1",
            event_code: "code",
          })
          return HttpResponse.json({ ok: true })
        }
      )
    )

    await postLogin({ corp_id: "player1", event_code: "code" })
  })

  it("throws LoginApiError on 401 with server body", async () => {
    server.use(
      http.post(
        ({ request }) =>
          new URL(request.url).pathname.endsWith("/api/auth/login"),
        () => HttpResponse.json({ message: "nope" }, { status: 401 })
      )
    )

    await expect(
      postLogin({ corp_id: "x", event_code: "y" })
    ).rejects.toMatchObject({
      status: 401,
    })
  })
})
