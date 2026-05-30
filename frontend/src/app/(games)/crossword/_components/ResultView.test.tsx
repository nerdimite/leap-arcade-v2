// @vitest-environment happy-dom

import { cleanup, render, screen } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { afterEach, describe, expect, it, vi } from "vitest"

import type { Result } from "@/services/crossword/schema"

import { ResultView } from "./ResultView"

const solvedOnlyResult: Result = {
  score: 350,
  solved_count: 2,
  total_entries: 5,
  base_score: 200,
  time_bonus: 150,
  time_elapsed_ms: 125_000,
  solved_entries: [
    {
      entry_id: "e1",
      number: 7,
      direction: "across",
      clue: "Database property ensuring all-or-nothing commits",
      answer: "ATOMICITY",
      cells: [{ row: 0, col: 0 }],
    },
    {
      entry_id: "e2",
      number: 3,
      direction: "down",
      clue: "Container orchestrator",
      answer: "K8S",
      cells: [{ row: 1, col: 2 }],
    },
  ],
}

describe("ResultView", () => {
  afterEach(() => {
    cleanup()
  })

  it("renders total score, breakdown, stats, solved entries, and back action", () => {
    const onBackToLobby = vi.fn()

    render(
      <ResultView result={solvedOnlyResult} onBackToLobby={onBackToLobby} />
    )

    expect(screen.getByText("350")).toBeInTheDocument()
    expect(
      screen.getByText(/200 \(= 2 × 100\) \+ 150 = 350/)
    ).toBeInTheDocument()
    expect(screen.getByText(/2 \/ 5/)).toBeInTheDocument()
    expect(screen.getByText("2:05")).toBeInTheDocument()
    expect(screen.getByText("7 Across")).toBeInTheDocument()
    expect(screen.getByText("ATOMICITY")).toBeInTheDocument()
    expect(
      screen.getByText(/Database property ensuring all-or-nothing commits/)
    ).toBeInTheDocument()
    expect(screen.getByText("3 Down")).toBeInTheDocument()
    expect(screen.getByText("K8S")).toBeInTheDocument()
    expect(screen.getByText(/Container orchestrator/)).toBeInTheDocument()
  })

  it("falls back to score-only when bonus fields are absent", () => {
    const legacyResult = {
      score: 100,
      solved_count: 1,
      total_entries: 5,
      solved_entries: [solvedOnlyResult.solved_entries[0]],
    } as Result

    render(<ResultView result={legacyResult} onBackToLobby={vi.fn()} />)

    expect(screen.getByText("100")).toBeInTheDocument()
    expect(screen.queryByText(/\+.*=/)).toBeNull()
    expect(screen.getByText(/1 \/ 5/)).toBeInTheDocument()
  })

  it("never renders unsolved entry answers when payload includes only solved entries", () => {
    render(<ResultView result={solvedOnlyResult} onBackToLobby={vi.fn()} />)

    expect(screen.queryByText("KUBERNETES")).toBeNull()
    expect(screen.queryByText("LINUX")).toBeNull()
    expect(screen.queryByText("Missed")).toBeNull()
  })

  it("calls onBackToLobby when Back to Lobby is clicked", async () => {
    const onBackToLobby = vi.fn()
    const user = userEvent.setup()

    render(
      <ResultView result={solvedOnlyResult} onBackToLobby={onBackToLobby} />
    )

    await user.click(screen.getByRole("button", { name: /back to lobby/i }))
    expect(onBackToLobby).toHaveBeenCalledOnce()
  })
})
