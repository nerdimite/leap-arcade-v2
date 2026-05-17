"use client";

import { useReducer } from "react";

import type {
  WikiNavigateResponse,
  WikiPlayResponse,
  WikiPuzzleResult,
} from "@/services/wiki/schema";

export type WikiPhase = "loading" | "active" | "puzzleResult" | "terminal" | "error";

export type WikiState = {
  phase: WikiPhase;
  play: WikiPlayResponse | null;
  /** Client-local wall clock sync: server `time_remaining_ms` at last play / navigate active response. */
  timerRemainingMs: number | null;
  timerDeadlineAtMs: number | null;
  errorMessage: string | null;
  puzzleResult: WikiPuzzleResult | null;
  totalScoreAfterPuzzle: number | null;
  nextPuzzleAvailable: boolean | null;
};

export type WikiAction =
  | { type: "PLAY_OK"; payload: WikiPlayResponse }
  | { type: "PLAY_ERROR"; payload: { message: string } }
  | { type: "TICK"; payload: { nowMs: number } }
  | { type: "NAVIGATE_OK"; payload: WikiNavigateResponse }
  | { type: "NAVIGATE_ERROR"; payload: { message: string } };

export const wikiInitialState: WikiState = {
  phase: "loading",
  play: null,
  timerRemainingMs: null,
  timerDeadlineAtMs: null,
  errorMessage: null,
  puzzleResult: null,
  totalScoreAfterPuzzle: null,
  nextPuzzleAvailable: null,
};

function initFromPlay(play: WikiPlayResponse): WikiState {
  if (play.state === "active") {
    return {
      phase: "active",
      play,
      timerRemainingMs: play.current.time_remaining_ms,
      timerDeadlineAtMs: Date.now() + play.current.time_remaining_ms,
      errorMessage: null,
      puzzleResult: null,
      totalScoreAfterPuzzle: null,
      nextPuzzleAvailable: null,
    };
  }
  return {
    phase: "terminal",
    play,
    timerRemainingMs: null,
    timerDeadlineAtMs: null,
    errorMessage: null,
    puzzleResult: null,
    totalScoreAfterPuzzle: null,
    nextPuzzleAvailable: null,
  };
}

export function wikiReducer(state: WikiState, action: WikiAction): WikiState {
  switch (action.type) {
    case "PLAY_OK":
      return initFromPlay(action.payload);
    case "PLAY_ERROR":
      return {
        ...state,
        phase: "error",
        errorMessage: action.payload.message,
      };
    case "NAVIGATE_OK": {
      const p = action.payload;
      if (p.state === "active") {
        if (state.play?.state !== "active") {
          return state;
        }
        return {
          ...state,
          phase: "active",
          play: {
            ...state.play,
            current: p.current,
          },
          timerRemainingMs: p.current.time_remaining_ms,
          timerDeadlineAtMs: Date.now() + p.current.time_remaining_ms,
          puzzleResult: null,
          totalScoreAfterPuzzle: null,
          nextPuzzleAvailable: null,
          errorMessage: null,
        };
      }
      return {
        ...state,
        phase: "puzzleResult",
        puzzleResult: p.puzzle_result,
        totalScoreAfterPuzzle: p.total_score,
        nextPuzzleAvailable: p.next_puzzle_available,
        errorMessage: null,
      };
    }
    case "NAVIGATE_ERROR":
      return {
        ...state,
        phase: "error",
        errorMessage: action.payload.message,
      };
    case "TICK": {
      if (state.phase !== "active" || state.timerRemainingMs == null || state.timerDeadlineAtMs == null) {
        return state;
      }
      const next = Math.max(0, state.timerDeadlineAtMs - action.payload.nowMs);
      return {
        ...state,
        timerRemainingMs: next,
        timerDeadlineAtMs: state.timerDeadlineAtMs,
      };
    }
    default:
      return state;
  }
}

export function useWikiReducer(initialPlay: WikiPlayResponse) {
  return useReducer(wikiReducer, wikiInitialState, () => initFromPlay(initialPlay));
}
