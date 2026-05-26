import { describe, expect, it } from "vitest";

import type { Coordinates } from "@/services/word_hunt/schema";

import {
  wordHuntDragInitialState,
  wordHuntDragReducer,
} from "./useWordHuntDragReducer";

describe("wordHuntDragReducer", () => {
  it("rejects a length-1 commit when drag ends without moving", () => {
    let state = wordHuntDragReducer(wordHuntDragInitialState, {
      type: "DRAG_START",
      payload: { row: 2, col: 2 },
    });

    state = wordHuntDragReducer(state, {
      type: "DRAG_END",
      payload: { rows: 10, cols: 10 },
    });

    expect(state.pendingCommit).toBeNull();
  });

  it("surfaces a valid multi-cell trace to the parent on drag end", () => {
    let state = wordHuntDragReducer(wordHuntDragInitialState, {
      type: "DRAG_START",
      payload: { row: 0, col: 0 },
    });

    state = wordHuntDragReducer(state, {
      type: "DRAG_MOVE",
      payload: { row: 0, col: 3, rows: 10, cols: 10 },
    });

    state = wordHuntDragReducer(state, {
      type: "DRAG_END",
      payload: { rows: 10, cols: 10 },
    });

    expect(state.pendingCommit).toEqual({
      start_row: 0,
      start_col: 0,
      end_row: 0,
      end_col: 3,
    });
  });

  it("stores a miss flash trace and clears it when the flash completes", () => {
    const trace: Coordinates = {
      start_row: 0,
      start_col: 0,
      end_row: 0,
      end_col: 4,
    };

    let state = wordHuntDragReducer(wordHuntDragInitialState, {
      type: "FIND_MISS",
      payload: { trace },
    });

    expect(state.missFlash).toEqual(trace);

    state = wordHuntDragReducer(state, { type: "MISS_FLASH_COMPLETE" });
    expect(state.missFlash).toBeNull();
  });

  it("shows a score increment on hit and clears it after animation", () => {
    const trace: Coordinates = {
      start_row: 0,
      start_col: 0,
      end_row: 0,
      end_col: 5,
    };

    let state = wordHuntDragReducer(wordHuntDragInitialState, {
      type: "FIND_HIT",
      payload: { trace },
    });

    expect(state.showScoreIncrement).toBe(true);
    expect(state.landAnimation).toEqual(trace);

    state = wordHuntDragReducer(state, { type: "SCORE_INCREMENT_COMPLETE" });
    expect(state.showScoreIncrement).toBe(false);

    state = wordHuntDragReducer(state, { type: "LAND_ANIMATION_COMPLETE" });
    expect(state.landAnimation).toBeNull();
  });
});
