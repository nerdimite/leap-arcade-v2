// @vitest-environment happy-dom

import {
  cleanup,
  fireEvent,
  render,
  screen,
  waitFor,
} from "@testing-library/react"
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest"

import { QueryClientProviderWrapper } from "@/components/query-client-provider"
import type { PlayResponse } from "@/services/word_hunt/schema"

import { WordHuntClient } from "./WordHuntClient"

const { setIsDirty, navigateSafe, postSubmit, postFind, postPlay } = vi.hoisted(
  () => ({
    setIsDirty: vi.fn(),
    navigateSafe: vi.fn(),
    postSubmit: vi.fn(),
    postFind: vi.fn(),
    postPlay: vi.fn(),
  })
)

vi.mock("@/hooks/use-navigation-guard", () => ({
  useNavigationGuard: () => ({
    setIsDirty,
    registerBeforeNavigateConfirm: () => () => {},
    navigateSafe,
  }),
}))

vi.mock("@/lib/api/word-hunt", () => ({
  postSubmit,
  postFind,
  postPlay,
}))

function devopsPlay(): PlayResponse {
  return {
    session_status: "active",
    session_score: 0,
    puzzle: {
      puzzle_id: "p1",
      rows: 1,
      cols: 6,
      grid: [["D", "E", "V", "O", "P", "S"]],
      clues: [
        {
          word_id: "w1",
          clue: "Culture where dev and ops stop pointing fingers.",
          found: false,
        },
      ],
      found_count: 0,
      total_words: 1,
      started_at: "2026-05-26T12:00:00.000Z",
    },
    result: null,
  }
}

function cellButton(letter: string): HTMLButtonElement {
  const button = screen.getByRole("button", { name: letter })
  if (!(button instanceof HTMLButtonElement)) {
    throw new Error(`Expected button for ${letter}`)
  }
  return button
}

describe("WordHuntClient drag commit", () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  afterEach(() => {
    cleanup()
  })

  it("submits a find after drag ends and updates the score", async () => {
    const refreshed = {
      ...devopsPlay(),
      session_score: 100,
      puzzle: {
        ...devopsPlay().puzzle!,
        found_count: 1,
        clues: [
          {
            word_id: "w1",
            clue: "Culture where dev and ops stop pointing fingers.",
            found: true,
            word: "DEVOPS",
            coordinates: { start_row: 0, start_col: 0, end_row: 0, end_col: 5 },
          },
        ],
      },
    }

    postFind.mockResolvedValue({
      matched: true,
      word: {
        word_id: "w1",
        word: "DEVOPS",
        clue: "Culture where dev and ops stop pointing fingers.",
        coordinates: { start_row: 0, start_col: 0, end_row: 0, end_col: 5 },
      },
      session_status: "active",
      session_score: 100,
      result: null,
    })
    postPlay.mockResolvedValue(refreshed)

    render(
      <QueryClientProviderWrapper>
        <WordHuntClient initialPlay={devopsPlay()} />
      </QueryClientProviderWrapper>
    )

    const start = cellButton("D")
    const end = cellButton("S")

    const elementFromPoint = vi
      .spyOn(document, "elementFromPoint")
      .mockImplementation((x) => (x >= 50 ? end : start))

    fireEvent.pointerDown(start, { pointerId: 1, clientX: 0, clientY: 0 })
    fireEvent.pointerMove(window, {
      pointerId: 1,
      clientX: 100,
      clientY: 0,
      buttons: 1,
    })
    fireEvent.pointerUp(window, { pointerId: 1, clientX: 100, clientY: 0 })

    elementFromPoint.mockRestore()

    await waitFor(() => {
      expect(postFind).toHaveBeenCalledWith({
        start_row: 0,
        start_col: 0,
        end_row: 0,
        end_col: 5,
      })
    })

    await waitFor(() => {
      expect(screen.getByText(/Score: 100/)).toBeInTheDocument()
    })
  })
})
