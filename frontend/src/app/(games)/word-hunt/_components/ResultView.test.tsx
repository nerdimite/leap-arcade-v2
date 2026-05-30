// @vitest-environment happy-dom

import { cleanup, render, screen } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { afterEach, describe, expect, it, vi } from "vitest"

import type { Result } from "@/services/word_hunt/schema"

import { ResultView } from "./ResultView"

const foundOnlyResult: Result = {
  score: 350,
  found_count: 2,
  total_words: 5,
  base_score: 200,
  time_bonus: 150,
  time_elapsed_ms: 125_000,
  found_words: [
    {
      word_id: "w1",
      word: "CLOUD",
      clue: "Fluffy data center metaphor",
      coordinates: { start_row: 0, start_col: 0, end_row: 0, end_col: 4 },
    },
    {
      word_id: "w2",
      word: "DOCKER",
      clue: "Container captain",
      coordinates: { start_row: 1, start_col: 0, end_row: 1, end_col: 5 },
    },
  ],
}

describe("ResultView", () => {
  afterEach(() => {
    cleanup()
  })

  it("renders total score, breakdown, stats, found words, and back action", () => {
    const onBackToLobby = vi.fn()
    const result: Result = {
      ...foundOnlyResult,
      base_score: 200,
      time_bonus: 150,
      time_elapsed_ms: 125_000,
    }

    render(<ResultView result={result} onBackToLobby={onBackToLobby} />)

    expect(screen.getByText("350")).toBeInTheDocument()
    expect(
      screen.getByText(/200 \(= 2 × 100\) \+ 150 = 350/)
    ).toBeInTheDocument()
    expect(screen.getByText(/2 \/ 5/)).toBeInTheDocument()
    expect(screen.getByText("2:05")).toBeInTheDocument()
    expect(screen.getByText("CLOUD")).toBeInTheDocument()
    expect(screen.getByText(/Fluffy data center metaphor/)).toBeInTheDocument()
    expect(screen.getByText("DOCKER")).toBeInTheDocument()
    expect(screen.getByText(/Container captain/)).toBeInTheDocument()
  })

  it("falls back to score-only when bonus fields are absent", () => {
    const legacyResult = {
      score: 350,
      found_count: 2,
      total_words: 5,
      found_words: foundOnlyResult.found_words,
    } as Result

    render(<ResultView result={legacyResult} onBackToLobby={vi.fn()} />)

    expect(screen.getByText("350")).toBeInTheDocument()
    expect(screen.queryByText(/\+.*=/)).toBeNull()
    expect(screen.getByText(/2 \/ 5/)).toBeInTheDocument()
  })

  it("never renders unfound hidden words when payload includes only found words", () => {
    render(<ResultView result={foundOnlyResult} onBackToLobby={vi.fn()} />)

    expect(screen.queryByText("KUBERNETES")).toBeNull()
    expect(screen.queryByText("LINUX")).toBeNull()
    expect(screen.queryByText("Missed")).toBeNull()
  })

  it("calls onBackToLobby when Back to Lobby is clicked", async () => {
    const onBackToLobby = vi.fn()
    const user = userEvent.setup()

    render(
      <ResultView result={foundOnlyResult} onBackToLobby={onBackToLobby} />
    )

    await user.click(screen.getByRole("button", { name: /back to lobby/i }))
    expect(onBackToLobby).toHaveBeenCalledOnce()
  })
})
