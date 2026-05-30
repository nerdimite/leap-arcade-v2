// @vitest-environment happy-dom

import { cleanup, render, screen } from "@testing-library/react"
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest"

import type { PuzzleState } from "@/services/pinpoint/schema"

import { PinpointView } from "./PinpointView"

const samplePuzzle: PuzzleState = {
  puzzle_id: "p1",
  puzzle_number: 1,
  total_puzzles: 3,
  clues_revealed: 5,
  clues: ["a", "b", "c", "d", "e"],
  status: "failed",
  score: 0,
  time_bonus: null,
  started_at: "2026-05-26T12:00:00.000Z",
}

describe("PinpointView", () => {
  beforeEach(() => {
    // Pin reduced-motion so the solved-overlay score count-up settles synchronously.
    vi.stubGlobal("matchMedia", (query: string) => ({
      matches: true,
      media: query,
      onchange: null,
      addEventListener: vi.fn(),
      removeEventListener: vi.fn(),
      addListener: vi.fn(),
      removeListener: vi.fn(),
      dispatchEvent: vi.fn(),
    }))
  })

  afterEach(() => {
    cleanup()
    vi.unstubAllGlobals()
  })

  it("never renders answer or answer_aliases when leaked onto puzzle state", () => {
    const leakedPuzzle = {
      ...samplePuzzle,
      answer: "cloud computing",
      answer_aliases: ["cloud", "computing"],
    } as PuzzleState & { answer: string; answer_aliases: string[] }

    render(
      <PinpointView
        viewState={{
          status: "playing",
          sessionScore: 0,
          puzzle: leakedPuzzle,
          guess: "",
          inputDisabled: false,
          overlay: null,
          shakeBadgeIndex: null,
          errorMessage: null,
        }}
        onGuessChange={vi.fn()}
        onSubmitGuess={vi.fn()}
      />
    )

    expect(screen.queryByText("cloud computing")).toBeNull()
    expect(screen.queryByText("cloud")).toBeNull()
    expect(screen.queryByText("computing")).toBeNull()
  })

  it("disables input while flashing overlay is visible", () => {
    render(
      <PinpointView
        viewState={{
          status: "playing",
          sessionScore: 100,
          puzzle: {
            ...samplePuzzle,
            status: "solved",
            score: 466,
            time_bonus: 66,
          },
          guess: "",
          inputDisabled: true,
          overlay: {
            kind: "solved",
            baseScore: 400,
            timeBonus: 66,
            cluesUsed: 3,
          },
          shakeBadgeIndex: null,
          errorMessage: null,
        }}
        onGuessChange={vi.fn()}
        onSubmitGuess={vi.fn()}
      />
    )

    expect(screen.getByRole("textbox")).toBeDisabled()
    expect(screen.getByRole("button", { name: "Guess" })).toBeDisabled()
    expect(screen.getByRole("status")).toHaveTextContent("+466")
  })
})
