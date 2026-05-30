import type { PuzzleState } from "@/services/crossword/schema"

export const emptyPuzzle: PuzzleState = {
  puzzle_id: "story-empty",
  rows: 3,
  cols: 3,
  cells: [
    [
      { row: 0, col: 0, number: 1 },
      { row: 0, col: 1 },
      { row: 0, col: 2 },
    ],
    [{ row: 1, col: 0 }, null, null],
    [{ row: 2, col: 0 }, null, null],
  ],
  clues: [
    {
      entry_id: "across-1",
      number: 1,
      direction: "across",
      clue: "Feline pet",
      length: 3,
      start_row: 0,
      start_col: 0,
      solved: false,
    },
    {
      entry_id: "down-1",
      number: 1,
      direction: "down",
      clue: "Farm moo-er",
      length: 3,
      start_row: 0,
      start_col: 0,
      solved: false,
    },
  ],
  solved_count: 0,
  total_entries: 2,
  started_at: "2026-05-26T12:00:00.000Z",
}

export const inProgressPuzzle: PuzzleState = {
  ...emptyPuzzle,
  puzzle_id: "story-progress",
  solved_count: 1,
  clues: emptyPuzzle.clues.map((clue) =>
    clue.direction === "across"
      ? {
          ...clue,
          solved: true,
          answer: "CAT",
          cells: [
            { row: 0, col: 0 },
            { row: 0, col: 1 },
            { row: 0, col: 2 },
          ],
        }
      : clue
  ),
  cells: [
    [
      { row: 0, col: 0, number: 1, letter: "C" },
      { row: 0, col: 1, letter: "A" },
      { row: 0, col: 2, letter: "T" },
    ],
    [{ row: 1, col: 0 }, null, null],
    [{ row: 2, col: 0 }, null, null],
  ],
}

export const allSolvedPuzzle: PuzzleState = {
  ...inProgressPuzzle,
  puzzle_id: "story-all-solved",
  solved_count: 2,
  clues: emptyPuzzle.clues.map((clue) => ({
    ...clue,
    solved: true,
    answer: clue.direction === "across" ? "CAT" : "COW",
    cells:
      clue.direction === "across"
        ? [
            { row: 0, col: 0 },
            { row: 0, col: 1 },
            { row: 0, col: 2 },
          ]
        : [
            { row: 0, col: 0 },
            { row: 1, col: 0 },
            { row: 2, col: 0 },
          ],
  })),
  cells: [
    [
      { row: 0, col: 0, number: 1, letter: "C" },
      { row: 0, col: 1, letter: "A" },
      { row: 0, col: 2, letter: "T" },
    ],
    [{ row: 1, col: 0, letter: "O" }, null, null],
    [{ row: 2, col: 0, letter: "W" }, null, null],
  ],
}

export const activeHighlightCells = new Set(["0,0", "0,1", "0,2"])

export const missFlashCells = new Set(["1,0", "2,0"])

export const lockedCellsFromPuzzle = (puzzle: PuzzleState): Set<string> => {
  const locked = new Set<string>()
  for (const clue of puzzle.clues) {
    if (!clue.solved || !clue.cells) {
      continue
    }
    for (const cell of clue.cells) {
      locked.add(`${cell.row},${cell.col}`)
    }
  }
  for (const row of puzzle.cells) {
    for (const cell of row) {
      if (cell?.letter) {
        locked.add(`${cell.row},${cell.col}`)
      }
    }
  }
  return locked
}

export const draftInProgress: Record<string, string> = {
  "1,0": "X",
  "2,0": "Z",
}
