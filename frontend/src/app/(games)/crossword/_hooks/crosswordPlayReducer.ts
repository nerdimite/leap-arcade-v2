import type { PuzzleState } from "@/services/crossword/schema";

import {
  buildPuzzleContext,
  cellKey,
  collectEntryCellKeys,
  findOpenCellInDirection,
  firstOpenCellInEntry,
  getActiveEntryId,
  getCellLetter,
  isEntryComplete,
  isSharedCell,
  nextCellInEntry,
  resolveDirectionForCell,
  type CrosswordDirection,
  type PuzzleContext,
} from "../_lib/crosswordGrid";

export type CrosswordPlayState = {
  context: PuzzleContext | null;
  cursor: { row: number; col: number } | null;
  direction: CrosswordDirection;
  draft: Record<string, string>;
  missFlashEntryIds: string[];
  solveFlashEntryIds: string[];
  showScoreIncrement: boolean;
  pendingCheckEntryIds: string[];
  checkQueue: string[];
};

export type CrosswordPlayAction =
  | { type: "SET_PUZZLE"; payload: { puzzle: PuzzleState } }
  | { type: "SELECT_CELL"; payload: { row: number; col: number } }
  | { type: "TOGGLE_DIRECTION" }
  | { type: "TYPE_LETTER"; payload: { letter: string } }
  | { type: "ARROW"; payload: { deltaRow: number; deltaCol: number } }
  | { type: "BACKSPACE" }
  | { type: "SELECT_CLUE"; payload: { entryId: string } }
  | { type: "CLEAR_CHECK_QUEUE" }
  | { type: "CHECK_STARTED"; payload: { entryId: string } }
  | { type: "CHECK_FINISHED"; payload: { entryId: string } }
  | { type: "CHECK_HIT"; payload: { entryId: string } }
  | { type: "CHECK_MISS"; payload: { entryId: string } }
  | { type: "MISS_FLASH_COMPLETE" }
  | { type: "SOLVE_FLASH_COMPLETE" }
  | { type: "SCORE_INCREMENT_COMPLETE" };

export const crosswordPlayInitialState: CrosswordPlayState = {
  context: null,
  cursor: null,
  direction: "across",
  draft: {},
  missFlashEntryIds: [],
  solveFlashEntryIds: [],
  showScoreIncrement: false,
  pendingCheckEntryIds: [],
  checkQueue: [],
};

function enqueueCompletedEntries(
  state: CrosswordPlayState,
  editedKeys: string[],
): string[] {
  if (!state.context) {
    return [];
  }
  const candidateIds = new Set<string>();
  for (const key of editedKeys) {
    const member = state.context.membership[key];
    if (!member) {
      continue;
    }
    if (member.acrossEntryId) {
      candidateIds.add(member.acrossEntryId);
    }
    if (member.downEntryId) {
      candidateIds.add(member.downEntryId);
    }
  }

  const queue: string[] = [];
  for (const entryId of candidateIds) {
    if (
      isEntryComplete(state.context, state.draft, entryId) &&
      !state.pendingCheckEntryIds.includes(entryId) &&
      !state.checkQueue.includes(entryId)
    ) {
      queue.push(entryId);
    }
  }
  return queue;
}

function advanceCursorForTyping(
  state: CrosswordPlayState,
  from: { row: number; col: number },
): { row: number; col: number } | null {
  if (!state.context) {
    return null;
  }
  const entryId = getActiveEntryId(state.context, from, state.direction);
  if (!entryId) {
    return null;
  }
  const clue = state.context.cluesById[entryId];
  if (!clue) {
    return null;
  }

  let current: { row: number; col: number } | null = from;
  while (current) {
    const next = nextCellInEntry(state.context, clue, current, true);
    if (!next) {
      return current;
    }
    const key = cellKey(next.row, next.col);
    if (!state.context.lockedCells.has(key)) {
      return next;
    }
    current = next;
  }
  return from;
}

function retreatCursorForBackspace(
  state: CrosswordPlayState,
  from: { row: number; col: number },
): { row: number; col: number } | null {
  if (!state.context) {
    return null;
  }
  const entryId = getActiveEntryId(state.context, from, state.direction);
  if (!entryId) {
    return null;
  }
  const clue = state.context.cluesById[entryId];
  if (!clue) {
    return null;
  }

  let current: { row: number; col: number } | null = from;
  while (current) {
    const prev = nextCellInEntry(state.context, clue, current, false);
    if (!prev) {
      return null;
    }
    const key = cellKey(prev.row, prev.col);
    if (!state.context.lockedCells.has(key)) {
      return prev;
    }
    current = prev;
  }
  return null;
}

export function crosswordPlayReducer(
  state: CrosswordPlayState,
  action: CrosswordPlayAction,
): CrosswordPlayState {
  switch (action.type) {
    case "SET_PUZZLE": {
      const context = buildPuzzleContext(action.payload.puzzle);
      const draft: Record<string, string> = {};
      for (const [key, letter] of Object.entries(state.draft)) {
        if (!context.lockedCells.has(key)) {
          draft[key] = letter;
        }
      }
      return {
        ...state,
        context,
        draft,
        pendingCheckEntryIds: [],
        checkQueue: [],
        missFlashEntryIds: [],
      };
    }

    case "SELECT_CELL": {
      if (!state.context) {
        return state;
      }
      const { row, col } = action.payload;
      const key = cellKey(row, col);
      if (!state.context.openCells.has(key)) {
        return state;
      }

      const sameCell =
        state.cursor?.row === row && state.cursor?.col === col;

      if (sameCell && isSharedCell(state.context, row, col)) {
        return {
          ...state,
          direction: state.direction === "across" ? "down" : "across",
        };
      }

      const direction = resolveDirectionForCell(
        state.context,
        row,
        col,
        sameCell ? state.direction : state.direction,
      );

      return {
        ...state,
        cursor: { row, col },
        direction,
      };
    }

    case "TOGGLE_DIRECTION": {
      if (!state.context || !state.cursor) {
        return state;
      }
      if (!isSharedCell(state.context, state.cursor.row, state.cursor.col)) {
        return {
          ...state,
          direction: resolveDirectionForCell(
            state.context,
            state.cursor.row,
            state.cursor.col,
            state.direction,
          ),
        };
      }
      return {
        ...state,
        direction: state.direction === "across" ? "down" : "across",
      };
    }

    case "TYPE_LETTER": {
      if (!state.context || !state.cursor) {
        return state;
      }
      const letter = action.payload.letter.toUpperCase();
      if (!/^[A-Z]$/.test(letter)) {
        return state;
      }

      const startKey = cellKey(state.cursor.row, state.cursor.col);
      let cursor = state.cursor;
      let draft = state.draft;
      const editedKeys: string[] = [];

      if (state.context.lockedCells.has(startKey)) {
        const advanced = advanceCursorForTyping(state, cursor);
        if (!advanced || (advanced.row === cursor.row && advanced.col === cursor.col)) {
          return state;
        }
        cursor = advanced;
      } else {
        const key = cellKey(cursor.row, cursor.col);
        draft = { ...state.draft, [key]: letter };
        editedKeys.push(key);
        const advanced = advanceCursorForTyping({ ...state, draft }, cursor);
        cursor = advanced ?? cursor;
      }

      const nextState: CrosswordPlayState = {
        ...state,
        draft,
        cursor,
      };
      const checkQueue = enqueueCompletedEntries(nextState, editedKeys);
      return {
        ...nextState,
        checkQueue: [...state.checkQueue, ...checkQueue],
      };
    }

    case "ARROW": {
      if (!state.context || !state.cursor) {
        return state;
      }
      const next = findOpenCellInDirection(
        state.context,
        state.cursor,
        action.payload.deltaRow,
        action.payload.deltaCol,
      );
      if (!next) {
        return state;
      }
      const direction =
        action.payload.deltaRow === 0
          ? "across"
          : action.payload.deltaCol === 0
            ? "down"
            : state.direction;
      return {
        ...state,
        cursor: next,
        direction: resolveDirectionForCell(
          state.context,
          next.row,
          next.col,
          direction,
        ),
      };
    }

    case "BACKSPACE": {
      if (!state.context || !state.cursor) {
        return state;
      }
      const key = cellKey(state.cursor.row, state.cursor.col);
      if (state.context.lockedCells.has(key)) {
        const retreated = retreatCursorForBackspace(state, state.cursor);
        if (!retreated) {
          return state;
        }
        return {
          ...state,
          cursor: retreated,
        };
      }

      const currentLetter = state.draft[key];
      if (currentLetter) {
        const draft = { ...state.draft };
        delete draft[key];
        return { ...state, draft };
      }

      const retreated = retreatCursorForBackspace(state, state.cursor);
      if (!retreated) {
        return state;
      }
      const retreatKey = cellKey(retreated.row, retreated.col);
      if (state.context.lockedCells.has(retreatKey)) {
        return { ...state, cursor: retreated };
      }
      const draft = { ...state.draft };
      delete draft[retreatKey];
      return {
        ...state,
        cursor: retreated,
        draft,
      };
    }

    case "SELECT_CLUE": {
      if (!state.context) {
        return state;
      }
      const clue = state.context.cluesById[action.payload.entryId];
      if (!clue) {
        return state;
      }
      const firstOpen = firstOpenCellInEntry(state.context, clue.entry_id);
      if (!firstOpen) {
        return state;
      }
      return {
        ...state,
        cursor: firstOpen,
        direction: clue.direction as CrosswordDirection,
      };
    }

    case "CLEAR_CHECK_QUEUE":
      return { ...state, checkQueue: [] };

    case "CHECK_STARTED":
      if (state.pendingCheckEntryIds.includes(action.payload.entryId)) {
        return state;
      }
      return {
        ...state,
        pendingCheckEntryIds: [...state.pendingCheckEntryIds, action.payload.entryId],
      };

    case "CHECK_FINISHED":
      return {
        ...state,
        pendingCheckEntryIds: state.pendingCheckEntryIds.filter(
          (id) => id !== action.payload.entryId,
        ),
      };

    case "CHECK_HIT": {
      if (!state.context) {
        return state;
      }
      const clue = state.context.cluesById[action.payload.entryId];
      if (!clue) {
        return state;
      }
      const keys = collectEntryCellKeys(clue);
      const draft = { ...state.draft };
      for (const k of keys) {
        delete draft[k];
      }
      return {
        ...state,
        draft,
        showScoreIncrement: true,
        solveFlashEntryIds: state.solveFlashEntryIds.includes(action.payload.entryId)
          ? state.solveFlashEntryIds
          : [...state.solveFlashEntryIds, action.payload.entryId],
      };
    }

    case "CHECK_MISS":
      return {
        ...state,
        missFlashEntryIds: state.missFlashEntryIds.includes(action.payload.entryId)
          ? state.missFlashEntryIds
          : [...state.missFlashEntryIds, action.payload.entryId],
      };

    case "MISS_FLASH_COMPLETE":
      return { ...state, missFlashEntryIds: [] };

    case "SOLVE_FLASH_COMPLETE":
      return { ...state, solveFlashEntryIds: [] };

    case "SCORE_INCREMENT_COMPLETE":
      return { ...state, showScoreIncrement: false };

    default:
      return state;
  }
}

export function getDisplayLetter(
  state: CrosswordPlayState,
  key: string,
): string {
  if (!state.context) {
    return "";
  }
  return getCellLetter(state.context, state.draft, key);
}

export function getActiveClueEntryId(state: CrosswordPlayState): string | null {
  if (!state.context) {
    return null;
  }
  return getActiveEntryId(state.context, state.cursor, state.direction);
}
