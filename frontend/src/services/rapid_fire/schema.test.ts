import { describe, expect, it } from "vitest"

import {
  AbandonResponseSchema,
  AnswerResponseSchema,
  PlayResponseSchema,
  QuestionSchema,
} from "./schema"

const sampleQuestion = {
  id: "q1",
  question: "Sample?",
  options: ["A", "B", "C", "D"],
  time_limit_ms: 15_000,
}

describe("PlayResponseSchema", () => {
  it("parses active branch with required fields", () => {
    const raw = {
      status: "active",
      game_session_id: "gs-1",
      questions_answered: 0,
      questions_total: 15,
      question: sampleQuestion,
    }
    const parsed = PlayResponseSchema.parse(raw)
    expect(parsed.status).toBe("active")
    if (parsed.status !== "active") {
      throw new Error("expected active")
    }
    expect(parsed.game_session_id).toBe("gs-1")
    expect(parsed.questions_answered).toBe(0)
    expect(parsed.questions_total).toBe(15)
    expect(QuestionSchema.parse(parsed.question)).toEqual(sampleQuestion)
  })
})

describe("AbandonResponseSchema", () => {
  it("parses { result: { score, correct_count, wrong_count, skipped_count, time_taken_seconds } }", () => {
    const raw = {
      result: {
        score: 40,
        correct_count: 2,
        wrong_count: 1,
        skipped_count: 3,
        time_taken_seconds: 12.5,
      },
    }
    const parsed = AbandonResponseSchema.parse(raw)
    expect(parsed.result).toEqual(raw.result)
  })
})

describe("AnswerResponseSchema", () => {
  it("parses terminal answer with result and null next_question", () => {
    const raw = {
      correct: true,
      correct_option: 2,
      correct_answer_text: "B",
      current_score: 120,
      questions_answered: 15,
      questions_remaining: 0,
      next_question: null,
      result: {
        score: 120,
        correct_count: 10,
        wrong_count: 4,
        skipped_count: 1,
        time_taken_seconds: 42.5,
      },
    }
    const parsed = AnswerResponseSchema.parse(raw)
    expect(parsed.next_question).toBeNull()
    expect(parsed.result).toEqual(raw.result)
  })
})
