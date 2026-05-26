import type { Coordinates } from "@/services/word_hunt/schema";

import { isSingleCellTrace, snapTraceFromPointer } from "../_lib/traceSnap";

export type WordHuntDragState = {
  dragStart: { row: number; col: number } | null;
  dragPreview: Coordinates | null;
  pendingCommit: Coordinates | null;
  missFlash: Coordinates | null;
  showScoreIncrement: boolean;
  landAnimation: Coordinates | null;
};

export type WordHuntDragAction =
  | { type: "DRAG_START"; payload: { row: number; col: number } }
  | { type: "DRAG_MOVE"; payload: { row: number; col: number; rows: number; cols: number } }
  | { type: "DRAG_END"; payload: { rows: number; cols: number } }
  | { type: "CLEAR_PENDING_COMMIT" }
  | { type: "FIND_MISS"; payload: { trace: Coordinates } }
  | { type: "MISS_FLASH_COMPLETE" }
  | { type: "FIND_HIT"; payload: { trace: Coordinates } }
  | { type: "SCORE_INCREMENT_COMPLETE" }
  | { type: "LAND_ANIMATION_COMPLETE" }
  | { type: "RESET_DRAG" };

export const wordHuntDragInitialState: WordHuntDragState = {
  dragStart: null,
  dragPreview: null,
  pendingCommit: null,
  missFlash: null,
  showScoreIncrement: false,
  landAnimation: null,
};

export function wordHuntDragReducer(
  state: WordHuntDragState,
  action: WordHuntDragAction,
): WordHuntDragState {
  switch (action.type) {
    case "DRAG_START":
      return {
        ...state,
        dragStart: { row: action.payload.row, col: action.payload.col },
        dragPreview: null,
      };

    case "DRAG_MOVE": {
      if (state.dragStart === null) {
        return state;
      }
      const preview = snapTraceFromPointer(
        state.dragStart.row,
        state.dragStart.col,
        action.payload.row,
        action.payload.col,
        action.payload.rows,
        action.payload.cols,
      );
      return {
        ...state,
        dragPreview: preview,
      };
    }

    case "DRAG_END": {
      if (state.dragPreview === null || isSingleCellTrace(state.dragPreview)) {
        return {
          ...state,
          dragStart: null,
          dragPreview: null,
        };
      }
      return {
        ...state,
        dragStart: null,
        dragPreview: null,
        pendingCommit: state.dragPreview,
      };
    }

    case "CLEAR_PENDING_COMMIT":
      return {
        ...state,
        pendingCommit: null,
      };

    case "FIND_MISS":
      return {
        ...state,
        missFlash: action.payload.trace,
      };

    case "MISS_FLASH_COMPLETE":
      return {
        ...state,
        missFlash: null,
      };

    case "FIND_HIT":
      return {
        ...state,
        showScoreIncrement: true,
        landAnimation: action.payload.trace,
      };

    case "SCORE_INCREMENT_COMPLETE":
      return {
        ...state,
        showScoreIncrement: false,
      };

    case "LAND_ANIMATION_COMPLETE":
      return {
        ...state,
        landAnimation: null,
      };

    case "RESET_DRAG":
      return {
        ...state,
        dragStart: null,
        dragPreview: null,
      };

    default:
      return state;
  }
}
