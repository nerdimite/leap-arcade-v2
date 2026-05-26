import { describe, expect, it } from "vitest";

import type { GuessResponse, PlayResponse, PuzzleState } from "@/services/pinpoint/schema";

import {
  initPinpointFromPlayResponse,
  pinpointInitialState,
  pinpointReducer,
  type PinpointState,
} from "./usePinpointReducer";

const samplePuzzle: PuzzleState = {
  puzzle_id: "p1",
  puzzle_number: 1,
  total_puzzles: 3,
  clues_revealed: 1,
  clues: ["cloud"],
  status: "active",
  score: null,
  time_bonus: null,
  started_at: "2026-05-26T12:00:00.000Z",
};

function guessResponse(
  partial: Partial<GuessResponse> & Pick<GuessResponse, "puzzle">,
): GuessResponse {
  return {
    correct: false,
    session_status: "active",
    session_score: 0,
    result: null,
    ...partial,
  };
}

describe("pinpointReducer", () => {
  it("initialises playing from an active play response", () => {
    const state = initPinpointFromPlayResponse({
      session_status: "active",
      session_score: 0,
      puzzle: samplePuzzle,
      result: null,
    });
    expect(state.phase).toBe("playing");
    expect(state.puzzle?.puzzle_id).toBe("p1");
  });

  it("initialises result from a completed play response", () => {
    const state = initPinpointFromPlayResponse({
      session_status: "completed",
      session_score: 500,
      puzzle: null,
      result: {
        score: 500,
        puzzles_solved: 1,
        puzzles_failed: 0,
        puzzles_not_reached: 0,
        puzzles: [],
      },
    });
    expect(state.phase).toBe("result");
    expect(state.result?.score).toBe(500);
  });

  it("playing → flashing on terminal puzzle guess", () => {
    let state = initPinpointFromPlayResponse({
      session_status: "active",
      session_score: 0,
      puzzle: samplePuzzle,
      result: null,
    });

    state = pinpointReducer(
      state,
      {
        type: "GUESS_SUCCESS",
        payload: guessResponse({
          correct: true,
          session_score: 400,
          puzzle: {
            ...samplePuzzle,
            clues_revealed: 2,
            clues: ["cloud", "server"],
            status: "solved",
            score: 400,
          },
        }),
      },
    );

    expect(state.phase).toBe("flashing");
    expect(state.flashKind).toBe("solved");
    expect(state.flashBaseScore).toBe(400);
    expect(state.flashTimeBonus).toBe(0);
    expect(state.guess).toBe("");
  });

  it("playing → flashing on failed puzzle", () => {
    let state = initPinpointFromPlayResponse({
      session_status: "active",
      session_score: 0,
      puzzle: samplePuzzle,
      result: null,
    });

    state = pinpointReducer(
      state,
      {
        type: "GUESS_SUCCESS",
        payload: guessResponse({
          puzzle: {
            ...samplePuzzle,
            clues_revealed: 5,
            clues: ["a", "b", "c", "d", "e"],
            status: "failed",
            score: 0,
          },
        }),
      },
    );

    expect(state.phase).toBe("flashing");
    expect(state.flashKind).toBe("failed");
    expect(state.flashBaseScore).toBe(0);
    expect(state.flashTimeBonus).toBe(0);
  });

  it("flashing → advancing on FLASH_COMPLETE", () => {
    let state = pinpointInitialState;
    state = {
      ...state,
      phase: "flashing",
      puzzle: { ...samplePuzzle, status: "solved", score: 300, time_bonus: 0 },
      flashKind: "solved",
      flashBaseScore: 300,
      flashTimeBonus: 0,
    };

    state = pinpointReducer(state, { type: "FLASH_COMPLETE" });
    expect(state.phase).toBe("advancing");
  });

  it("advancing → playing on ADVANCE_SUCCESS with next puzzle", () => {
    let state = pinpointInitialState;
    state = {
      ...state,
      phase: "advancing",
      sessionScore: 300,
    };

    const nextPuzzle: PuzzleState = {
      ...samplePuzzle,
      puzzle_id: "p2",
      puzzle_number: 2,
    };

    state = pinpointReducer(state, {
      type: "ADVANCE_SUCCESS",
      payload: {
        session_status: "active",
        session_score: 300,
        puzzle: nextPuzzle,
        result: null,
      } satisfies PlayResponse,
    });

    expect(state.phase).toBe("playing");
    expect(state.puzzle?.puzzle_id).toBe("p2");
    expect(state.flashKind).toBeNull();
  });

  it("advancing → result on ADVANCE_SUCCESS when session completes", () => {
    let state = pinpointInitialState;
    state = { ...state, phase: "advancing" };

    const result = {
      score: 800,
      puzzles_solved: 2,
      puzzles_failed: 1,
      puzzles_not_reached: 0,
      puzzles: [],
    };

    state = pinpointReducer(state, {
      type: "ADVANCE_SUCCESS",
      payload: {
        session_status: "completed",
        session_score: 800,
        puzzle: null,
        result,
      },
    });

    expect(state.phase).toBe("result");
    expect(state.result).toEqual(result);
    expect(state.puzzle).toBeNull();
  });

  it("sets shakeBadgeIndex on wrong guess while puzzle stays active", () => {
    let state = initPinpointFromPlayResponse({
      session_status: "active",
      session_score: 0,
      puzzle: samplePuzzle,
      result: null,
    });

    state = pinpointReducer(
      state,
      {
        type: "GUESS_SUCCESS",
        payload: guessResponse({
          puzzle: {
            ...samplePuzzle,
            clues_revealed: 2,
            clues: ["cloud", "server"],
            status: "active",
            score: null,
          },
        }),
      },
    );

    expect(state.phase).toBe("playing");
    expect(state.shakeBadgeIndex).toBe(1);
  });

  it("ignores GUESS_SUCCESS while flashing", () => {
    const flashing = {
      ...pinpointInitialState,
      phase: "flashing" as const,
      puzzle: samplePuzzle,
      flashKind: "solved" as const,
      flashBaseScore: 400,
      flashTimeBonus: 0,
    };

    const next = pinpointReducer(flashing, {
      type: "GUESS_SUCCESS",
      payload: guessResponse({ puzzle: samplePuzzle }),
    });

    expect(next).toEqual(flashing);
  });

  it("ignores SET_GUESS while flashing", () => {
    const flashing = {
      ...pinpointInitialState,
      phase: "flashing" as const,
      puzzle: samplePuzzle,
      flashKind: "failed" as const,
      flashBaseScore: 0,
      flashTimeBonus: 0,
    };

    const next = pinpointReducer(flashing, {
      type: "SET_GUESS",
      payload: { guess: "typed" },
    });

    expect(next).toEqual(flashing);
  });

  it("clears shakeBadgeIndex on CLEAR_SHAKE", () => {
    let state: PinpointState = {
      ...pinpointInitialState,
      phase: "playing",
      puzzle: samplePuzzle,
      shakeBadgeIndex: 2,
    };

    state = pinpointReducer(state, { type: "CLEAR_SHAKE" });
    expect(state.shakeBadgeIndex).toBeNull();
  });
});
