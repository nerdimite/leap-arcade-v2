import type { Meta, StoryObj } from "@storybook/nextjs-vite"
import { fn } from "storybook/test"

import type { Result } from "@/services/crossword/schema"

import {
  activeHighlightCells,
  allSolvedPuzzle,
  draftInProgress,
  inProgressPuzzle,
  lockedCellsFromPuzzle,
  missFlashCells,
} from "../_lib/storyFixtures"
import { CrosswordView } from "./CrosswordView"

const inProgressDisplayLetter = (row: number, col: number) =>
  inProgressPuzzle.cells[row]?.[col]?.letter ??
  draftInProgress[`${row},${col}`] ??
  ""

const activeEntryId = inProgressPuzzle.clues[0]?.entry_id ?? null

const sampleResult: Result = {
  score: 350,
  base_score: 200,
  time_bonus: 150,
  time_elapsed_ms: 125_000,
  solved_count: 2,
  total_entries: 5,
  solved_entries: [
    {
      entry_id: "7-across",
      number: 7,
      direction: "across",
      clue: "Database property ensuring all-or-nothing commits.",
      answer: "ATOMICITY",
      cells: [],
    },
    {
      entry_id: "3-down",
      number: 3,
      direction: "down",
      clue: "Container orchestrator, abbreviated.",
      answer: "K8S",
      cells: [],
    },
  ],
}

const meta = {
  component: CrosswordView,
  parameters: { layout: "fullscreen" },
  args: {
    onCellClick: fn(),
    onClueClick: fn(),
    onSubmit: fn(),
    onBackToLobby: fn(),
  },
} satisfies Meta<typeof CrosswordView>

export default meta

type Story = StoryObj<typeof meta>

export const Playing: Story = {
  args: {
    viewState: {
      status: "playing",
      puzzle: inProgressPuzzle,
      sessionScore: 100,
      displayLetter: inProgressDisplayLetter,
      lockedCells: lockedCellsFromPuzzle(inProgressPuzzle),
      selectedCell: { row: 1, col: 0 },
      activeEntryCells: new Set(["1,0", "2,0"]),
      missFlashCells: new Set(),
      activeEntryId,
      showScoreIncrement: false,
      submitDisabled: false,
    },
  },
}

export const WrongFlash: Story = {
  args: {
    viewState: {
      status: "playing",
      puzzle: inProgressPuzzle,
      sessionScore: 100,
      displayLetter: inProgressDisplayLetter,
      lockedCells: lockedCellsFromPuzzle(inProgressPuzzle),
      selectedCell: { row: 2, col: 0 },
      activeEntryCells: new Set(["1,0", "2,0"]),
      missFlashCells,
      activeEntryId,
      showScoreIncrement: false,
      submitDisabled: false,
    },
  },
}

export const SolvedEntry: Story = {
  args: {
    viewState: {
      status: "playing",
      puzzle: allSolvedPuzzle,
      sessionScore: 300,
      displayLetter: (row, col) =>
        allSolvedPuzzle.cells[row]?.[col]?.letter ?? "",
      lockedCells: lockedCellsFromPuzzle(allSolvedPuzzle),
      selectedCell: { row: 0, col: 0 },
      activeEntryCells: activeHighlightCells,
      missFlashCells: new Set(),
      activeEntryId: allSolvedPuzzle.clues[0]?.entry_id ?? null,
      showScoreIncrement: true,
      submitDisabled: false,
    },
  },
}

export const ResultStory: Story = {
  name: "Result",
  args: {
    viewState: { status: "result", result: sampleResult },
  },
}
