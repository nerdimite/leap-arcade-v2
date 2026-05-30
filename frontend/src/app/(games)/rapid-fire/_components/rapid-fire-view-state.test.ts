import { describe, expect, it } from "vitest"

import type { Result } from "@/services/rapid_fire/schema"

import {
  type RapidFireState,
  rapidFireInitialState,
} from "../_hooks/useRapidFireReducer"
import { toRapidFireViewState } from "./rapid-fire-view-state"

const sampleQuestion = {
  id: "q1",
  question: "Sample?",
  options: ["A", "B", "C", "D"],
  time_limit_ms: 10_000,
}

const sampleResult: Result = {
  score: 42,
  correct_count: 5,
  wrong_count: 3,
  skipped_count: 2,
  time_taken_seconds: 88.5,
}

function baseState(overrides: Partial<RapidFireState> = {}): RapidFireState {
  return {
    status: "question",
    sessionId: "gs",
    questionsAnswered: 0,
    questionsTotal: 15,
    currentQuestion: sampleQuestion,
    currentScore: 0,
    submittedOption: null,
    pendingTimeMs: null,
    lastCorrect: null,
    lastCorrectOption: null,
    lastScoreDelta: 0,
    pendingNextQuestion: null,
    pendingResult: null,
    result: null,
    errorMessage: null,
    ...overrides,
  }
}

describe("toRapidFireViewState", () => {
  it("maps idle to loading header fields", () => {
    expect(toRapidFireViewState(rapidFireInitialState, null)).toEqual({
      status: "loading",
      currentScore: 0,
      questionsAnswered: 0,
      questionsTotal: 0,
    })
  })

  it("maps loading status", () => {
    const state = baseState({
      status: "loading",
      currentQuestion: null,
      questionsTotal: 0,
      questionsAnswered: 0,
      currentScore: 0,
    })
    expect(toRapidFireViewState(state, null)).toEqual({
      status: "loading",
      currentScore: 0,
      questionsAnswered: 0,
      questionsTotal: 0,
    })
  })

  it("maps question status with timerBarPct default 100 when null", () => {
    const state = baseState({ status: "question" })
    expect(toRapidFireViewState(state, null)).toEqual({
      status: "question",
      question: sampleQuestion,
      timerBarPct: 100,
      currentScore: 0,
      questionsAnswered: 0,
      questionsTotal: 15,
      locked: false,
      submittedOption: null,
      lastCorrect: null,
      lastCorrectOption: null,
    })
  })

  it("maps question status with explicit timerBarPct", () => {
    const state = baseState({ status: "question", currentScore: 7 })
    expect(toRapidFireViewState(state, 72.5)).toEqual({
      status: "question",
      question: sampleQuestion,
      timerBarPct: 72.5,
      currentScore: 7,
      questionsAnswered: 0,
      questionsTotal: 15,
      locked: false,
      submittedOption: null,
      lastCorrect: null,
      lastCorrectOption: null,
    })
  })

  it("collapses submitting to locked question with timerBarPct default 0 when null", () => {
    const state = baseState({
      status: "submitting",
      submittedOption: 2,
      pendingTimeMs: 500,
    })
    expect(toRapidFireViewState(state, null)).toEqual({
      status: "question",
      question: sampleQuestion,
      timerBarPct: 0,
      currentScore: 0,
      questionsAnswered: 0,
      questionsTotal: 15,
      locked: true,
      submittedOption: 2,
      lastCorrect: null,
      lastCorrectOption: null,
    })
  })

  it("collapses submitting with explicit timerBarPct", () => {
    const state = baseState({
      status: "submitting",
      submittedOption: 1,
      pendingTimeMs: 200,
    })
    expect(toRapidFireViewState(state, 15)).toEqual({
      status: "question",
      question: sampleQuestion,
      timerBarPct: 15,
      currentScore: 0,
      questionsAnswered: 0,
      questionsTotal: 15,
      locked: true,
      submittedOption: 1,
      lastCorrect: null,
      lastCorrectOption: null,
    })
  })

  it("maps feedback status", () => {
    const state = baseState({
      status: "feedback",
      submittedOption: 3,
      lastCorrect: false,
      lastCorrectOption: 1,
      currentScore: 4,
      lastScoreDelta: 0,
    })
    expect(toRapidFireViewState(state, null)).toEqual({
      status: "feedback",
      question: sampleQuestion,
      lastCorrect: false,
      lastCorrectOption: 1,
      submittedOption: 3,
      currentScore: 4,
      scoreDelta: 0,
      questionsAnswered: 0,
      questionsTotal: 15,
    })
  })

  it("maps result status", () => {
    const state = baseState({
      status: "result",
      currentQuestion: null,
      result: sampleResult,
    })
    expect(toRapidFireViewState(state, null)).toEqual({
      status: "result",
      result: sampleResult,
    })
  })

  it("maps error status with message fallback", () => {
    const state = baseState({
      status: "error",
      currentQuestion: null,
      errorMessage: null,
    })
    expect(toRapidFireViewState(state, null)).toEqual({
      status: "error",
      message: "Something went wrong.",
    })
  })

  it("maps error status with explicit message", () => {
    const state = baseState({
      status: "error",
      currentQuestion: null,
      errorMessage: "Network failed",
    })
    expect(toRapidFireViewState(state, null)).toEqual({
      status: "error",
      message: "Network failed",
    })
  })
})
