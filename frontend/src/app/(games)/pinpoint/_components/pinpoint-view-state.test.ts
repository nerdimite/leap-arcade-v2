import { describe, expect, it } from "vitest"

import type { PuzzleState } from "@/services/pinpoint/schema"

import { pinpointInitialState } from "../_hooks/usePinpointReducer"
import { toPinpointViewState } from "./pinpoint-view-state"

const samplePuzzle: PuzzleState = {
  puzzle_id: "p1",
  puzzle_number: 1,
  total_puzzles: 3,
  clues_revealed: 2,
  clues: ["cloud", "server"],
  status: "active",
  score: null,
  time_bonus: null,
  started_at: "2026-05-26T12:00:00.000Z",
}

describe("toPinpointViewState", () => {
  it("maps playing with input enabled", () => {
    expect(
      toPinpointViewState(
        {
          ...pinpointInitialState,
          phase: "playing",
          puzzle: samplePuzzle,
          sessionScore: 100,
          guess: "test",
        },
        false
      )
    ).toEqual({
      status: "playing",
      sessionScore: 100,
      puzzle: samplePuzzle,
      guess: "test",
      inputDisabled: false,
      overlay: null,
      shakeBadgeIndex: null,
      errorMessage: null,
    })
  })

  it("maps flashing with overlay and disabled input", () => {
    expect(
      toPinpointViewState(
        {
          ...pinpointInitialState,
          phase: "flashing",
          puzzle: {
            ...samplePuzzle,
            status: "solved",
            score: 466,
            time_bonus: 66,
          },
          sessionScore: 466,
          flashKind: "solved",
          flashBaseScore: 400,
          flashTimeBonus: 66,
        },
        false
      )
    ).toEqual({
      status: "playing",
      sessionScore: 466,
      puzzle: { ...samplePuzzle, status: "solved", score: 466, time_bonus: 66 },
      guess: "",
      inputDisabled: true,
      overlay: { kind: "solved", baseScore: 400, timeBonus: 66, cluesUsed: 2 },
      shakeBadgeIndex: null,
      errorMessage: null,
    })
  })

  it("maps advancing to loading even when puzzle is still present", () => {
    expect(
      toPinpointViewState(
        {
          ...pinpointInitialState,
          phase: "advancing",
          puzzle: { ...samplePuzzle, status: "solved", score: 400 },
        },
        true
      )
    ).toEqual({ status: "loading" })
  })

  it("maps result phase", () => {
    const result = {
      score: 500,
      puzzles_solved: 1,
      puzzles_failed: 0,
      puzzles_not_reached: 0,
      puzzles: [],
    }

    expect(
      toPinpointViewState(
        {
          ...pinpointInitialState,
          phase: "result",
          result,
        },
        false
      )
    ).toEqual({
      status: "result",
      result,
    })
  })
})
