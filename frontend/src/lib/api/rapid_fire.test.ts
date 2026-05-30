import { HttpResponse, http } from "msw"
import { describe, expect, it } from "vitest"

import { server } from "@/test/msw-server"

import { postAbandon, postAnswer, postPlay } from "./rapid_fire"

const sampleQuestion = {
  id: "q1",
  question: "Sample?",
  options: ["A", "B", "C", "D"],
  time_limit_ms: 15_000,
}

describe("postPlay", () => {
  it("sends cookie and Authorization-free JSON POST; returns parsed PlayResponse", async () => {
    server.use(
      http.post(
        ({ request }) =>
          new URL(request.url).pathname.endsWith("/api/games/rapid-fire/play"),
        async ({ request }) => {
          expect(request.headers.get("cookie")).toBe("token=abc")
          expect(request.headers.get("accept")).toBe("application/json")
          const active = {
            status: "active",
            game_session_id: "gs",
            questions_answered: 0,
            questions_total: 15,
            question: sampleQuestion,
          }
          return HttpResponse.json(active)
        }
      )
    )

    const res = await postPlay({
      baseUrl: "http://localhost:3000",
      cookieHeader: "token=abc",
    })
    expect(res.status).toBe("active")
    if (res.status === "active") {
      expect(res.game_session_id).toBe("gs")
    }
  })
})

describe("postAnswer", () => {
  it("sends question_id, selected_option, time_ms JSON body", async () => {
    server.use(
      http.post(
        ({ request }) =>
          new URL(request.url).pathname.endsWith(
            "/api/games/rapid-fire/answer"
          ),
        async ({ request }) => {
          expect(request.headers.get("content-type")).toContain(
            "application/json"
          )
          expect(await request.json()).toEqual({
            question_id: "q1",
            selected_option: 3,
            time_ms: 1200,
          })
          return HttpResponse.json({
            correct: false,
            correct_option: 2,
            correct_answer_text: "B",
            current_score: 5,
            questions_answered: 1,
            questions_remaining: 14,
            next_question: sampleQuestion,
            result: null,
          })
        }
      )
    )

    const res = await postAnswer(
      {
        question_id: "q1",
        selected_option: 3,
        time_ms: 1200,
      },
      { baseUrl: "http://localhost:3000", cookieHeader: "token=abc" }
    )
    expect(res.correct).toBe(false)
    expect(res.next_question?.id).toBe("q1")
  })
})

describe("postAbandon", () => {
  it("returns parsed AbandonResponse; handler invoked once per call", async () => {
    let calls = 0
    server.use(
      http.post(
        ({ request }) =>
          new URL(request.url).pathname.endsWith(
            "/api/games/rapid-fire/abandon"
          ),
        () => {
          calls += 1
          return HttpResponse.json({
            result: {
              score: 25,
              correct_count: 1,
              wrong_count: 0,
              skipped_count: 2,
              time_taken_seconds: 30,
            },
          })
        }
      )
    )

    const res = await postAbandon({
      baseUrl: "http://localhost:3000",
      cookieHeader: "token=abc",
    })
    expect(calls).toBe(1)
    expect(res.result.score).toBe(25)
    expect(res.result.skipped_count).toBe(2)
  })
})
