import { describe, expect, it } from "vitest";

import type { PuzzleState } from "@/services/crossword/schema";

import { cellKey, collectEntryCellKeys } from "../_lib/crosswordGrid";
import {
  crosswordPlayInitialState,
  crosswordPlayReducer,
  getActiveClueEntryId,
} from "./crosswordPlayReducer";

function miniPuzzle(overrides: Partial<PuzzleState> = {}): PuzzleState {
  return {
    puzzle_id: "mini",
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
        clue: "Feline",
        length: 3,
        start_row: 0,
        start_col: 0,
        solved: false,
      },
      {
        entry_id: "down-1",
        number: 1,
        direction: "down",
        clue: "Farm animal",
        length: 3,
        start_row: 0,
        start_col: 0,
        solved: false,
      },
    ],
    solved_count: 0,
    total_entries: 2,
    started_at: "2026-05-26T12:00:00.000Z",
    ...overrides,
  };
}

function withPuzzle(puzzle: PuzzleState = miniPuzzle()) {
  return crosswordPlayReducer(crosswordPlayInitialState, {
    type: "SET_PUZZLE",
    payload: { puzzle },
  });
}

describe("crosswordPlayReducer", () => {
  it("selects a cell and uppercases typed letters while advancing across", () => {
    let state = withPuzzle();
    state = crosswordPlayReducer(state, {
      type: "SELECT_CELL",
      payload: { row: 0, col: 0 },
    });
    state = crosswordPlayReducer(state, {
      type: "TYPE_LETTER",
      payload: { letter: "c" },
    });

    expect(state.draft[cellKey(0, 0)]).toBe("C");
    expect(state.cursor).toEqual({ row: 0, col: 1 });
  });

  it("toggles direction on a shared cell when re-selected", () => {
    let state = withPuzzle();
    state = crosswordPlayReducer(state, {
      type: "SELECT_CELL",
      payload: { row: 0, col: 0 },
    });
    expect(state.direction).toBe("across");

    state = crosswordPlayReducer(state, {
      type: "SELECT_CELL",
      payload: { row: 0, col: 0 },
    });
    expect(state.direction).toBe("down");
  });

  it("forces direction on a single-membership cell", () => {
    let state = withPuzzle();
    state = crosswordPlayReducer(state, {
      type: "SELECT_CELL",
      payload: { row: 0, col: 1 },
    });
    expect(state.direction).toBe("across");
    expect(getActiveClueEntryId(state)).toBe("across-1");
  });

  it("moves the cursor with arrow keys and sets direction from axis", () => {
    let state = withPuzzle();
    state = crosswordPlayReducer(state, {
      type: "SELECT_CELL",
      payload: { row: 0, col: 0 },
    });
    state = crosswordPlayReducer(state, {
      type: "ARROW",
      payload: { deltaRow: 1, deltaCol: 0 },
    });

    expect(state.cursor).toEqual({ row: 1, col: 0 });
    expect(state.direction).toBe("down");
  });

  it("clears the current cell on backspace and retreats when empty", () => {
    let state = withPuzzle();
    state = crosswordPlayReducer(state, {
      type: "SELECT_CELL",
      payload: { row: 0, col: 1 },
    });
    state = crosswordPlayReducer(state, {
      type: "TYPE_LETTER",
      payload: { letter: "A" },
    });
    state = crosswordPlayReducer(state, { type: "BACKSPACE" });
    expect(state.draft[cellKey(0, 1)]).toBeUndefined();

    state = crosswordPlayReducer(state, { type: "BACKSPACE" });
    expect(state.cursor).toEqual({ row: 0, col: 0 });
    expect(state.draft[cellKey(0, 0)]).toBeUndefined();
  });

  it("does not clear locked cells on backspace", () => {
    const puzzle = miniPuzzle({
      clues: [
        {
          entry_id: "across-1",
          number: 1,
          direction: "across",
          clue: "Feline",
          length: 3,
          start_row: 0,
          start_col: 0,
          solved: true,
          answer: "CAT",
          cells: [
            { row: 0, col: 0 },
            { row: 0, col: 1 },
            { row: 0, col: 2 },
          ],
        },
        {
          entry_id: "down-1",
          number: 1,
          direction: "down",
          clue: "Farm animal",
          length: 3,
          start_row: 0,
          start_col: 0,
          solved: false,
        },
      ],
      solved_count: 1,
    });

    let state = withPuzzle(puzzle);
    state = crosswordPlayReducer(state, {
      type: "SELECT_CELL",
      payload: { row: 0, col: 0 },
    });
    state = crosswordPlayReducer(state, { type: "BACKSPACE" });

    expect(state.cursor).toEqual({ row: 0, col: 0 });
    expect(state.context?.lockedCells.has(cellKey(0, 0))).toBe(true);
  });

  it("jumps to the first open cell when a clue is selected", () => {
    let state = withPuzzle();
    state = crosswordPlayReducer(state, {
      type: "SELECT_CLUE",
      payload: { entryId: "down-1" },
    });

    expect(state.cursor).toEqual({ row: 0, col: 0 });
    expect(state.direction).toBe("down");
  });

  it("queues checks for both entries when a shared cell completes them", () => {
    let state = withPuzzle();
    state = crosswordPlayReducer(state, {
      type: "SELECT_CELL",
      payload: { row: 0, col: 2 },
    });

    const acrossKeys = collectEntryCellKeys(state.context!.cluesById["across-1"]);
    const acrossLetters = ["C", "A", "T"];
    for (const [index, key] of acrossKeys.entries()) {
      const { row, col } = { row: Number(key.split(",")[0]), col: Number(key.split(",")[1]) };
      state = crosswordPlayReducer(state, {
        type: "SELECT_CELL",
        payload: { row, col },
      });
      state = crosswordPlayReducer(state, {
        type: "TYPE_LETTER",
        payload: { letter: acrossLetters[index] ?? "X" },
      });
    }

    expect(state.checkQueue).toContain("across-1");

    state = crosswordPlayReducer(state, {
      type: "SELECT_CELL",
      payload: { row: 1, col: 0 },
    });
    state = crosswordPlayReducer(state, {
      type: "TYPE_LETTER",
      payload: { letter: "O" },
    });
    state = crosswordPlayReducer(state, {
      type: "SELECT_CELL",
      payload: { row: 2, col: 0 },
    });
    state = crosswordPlayReducer(state, {
      type: "TYPE_LETTER",
      payload: { letter: "W" },
    });

    expect(state.checkQueue).toContain("across-1");
    expect(state.checkQueue).toContain("down-1");
  });

  it("dedupes in-flight checks per entry id", () => {
    let state = withPuzzle();
    state = crosswordPlayReducer(state, {
      type: "CHECK_STARTED",
      payload: { entryId: "across-1" },
    });
    state = crosswordPlayReducer(state, {
      type: "CHECK_STARTED",
      payload: { entryId: "across-1" },
    });

    expect(state.pendingCheckEntryIds).toEqual(["across-1"]);
  });

  it("shows score increment on hit and miss flash on wrong entry", () => {
    let state = withPuzzle();
    state = crosswordPlayReducer(state, {
      type: "CHECK_HIT",
      payload: { entryId: "across-1" },
    });
    expect(state.showScoreIncrement).toBe(true);

    state = crosswordPlayReducer(state, {
      type: "CHECK_MISS",
      payload: { entryId: "down-1" },
    });
    expect(state.missFlashEntryIds).toEqual(["down-1"]);

    state = crosswordPlayReducer(state, { type: "MISS_FLASH_COMPLETE" });
    expect(state.missFlashEntryIds).toEqual([]);
  });
});
