"use client";

import { useReducer } from "react";

import type { AbandonResponse, GuessResponse, PlayResponse, PuzzleState, Result } from "@/services/pinpoint/schema";

export const PINPOINT_CLUE_COUNT = 5;

export type PinpointPhase = "playing" | "flashing" | "advancing" | "result";

export type PinpointState = {
  phase: PinpointPhase;
  puzzle: PuzzleState | null;
  result: Result | null;
  sessionScore: number;
  guess: string;
  errorMessage: string | null;
  shakeBadgeIndex: number | null;
  flashKind: "solved" | "failed" | null;
  flashBaseScore: number | null;
  flashTimeBonus: number | null;
};

export type PinpointAction =
  | { type: "SET_GUESS"; payload: { guess: string } }
  | { type: "GUESS_SUCCESS"; payload: GuessResponse }
  | { type: "GUESS_ERROR"; payload: { message: string } }
  | { type: "CLEAR_SHAKE" }
  | { type: "FLASH_COMPLETE" }
  | { type: "ADVANCE_SUCCESS"; payload: PlayResponse }
  | { type: "ADVANCE_ERROR"; payload: { message: string } }
  | { type: "ABANDON_SUCCESS"; payload: AbandonResponse };

export const pinpointInitialState: PinpointState = {
  phase: "playing",
  puzzle: null,
  result: null,
  sessionScore: 0,
  guess: "",
  errorMessage: null,
  shakeBadgeIndex: null,
  flashKind: null,
  flashBaseScore: null,
  flashTimeBonus: null,
};

export function initPinpointFromPlayResponse(play: PlayResponse): PinpointState {
  if (play.result) {
    return {
      ...pinpointInitialState,
      phase: "result",
      result: play.result,
      sessionScore: play.session_score,
    };
  }

  return {
    ...pinpointInitialState,
    phase: "playing",
    puzzle: play.puzzle,
    sessionScore: play.session_score,
  };
}

function terminalFlashFromPuzzle(puzzle: PuzzleState): Pick<
  PinpointState,
  "flashKind" | "flashBaseScore" | "flashTimeBonus"
> {
  const total = puzzle.score ?? 0;
  const timeBonus = puzzle.time_bonus ?? 0;
  return {
    flashKind: puzzle.status === "solved" ? "solved" : "failed",
    flashBaseScore: puzzle.status === "solved" ? total - timeBonus : 0,
    flashTimeBonus: puzzle.status === "solved" ? timeBonus : 0,
  };
}

export function pinpointReducer(state: PinpointState, action: PinpointAction): PinpointState {
  switch (action.type) {
    case "SET_GUESS": {
      if (state.phase !== "playing") {
        return state;
      }
      return {
        ...state,
        guess: action.payload.guess,
        errorMessage: null,
      };
    }
    case "GUESS_SUCCESS": {
      if (state.phase !== "playing") {
        return state;
      }

      const { puzzle, session_score: sessionScore } = action.payload;

      if (puzzle.status === "active") {
        return {
          ...state,
          puzzle,
          sessionScore,
          guess: "",
          shakeBadgeIndex: action.payload.correct ? null : puzzle.clues_revealed - 1,
        };
      }

      return {
        ...state,
        puzzle,
        sessionScore,
        guess: "",
        shakeBadgeIndex: null,
        phase: "flashing",
        ...terminalFlashFromPuzzle(puzzle),
      };
    }
    case "GUESS_ERROR": {
      if (state.phase !== "playing") {
        return state;
      }
      return {
        ...state,
        errorMessage: action.payload.message,
      };
    }
    case "CLEAR_SHAKE":
      return {
        ...state,
        shakeBadgeIndex: null,
      };
    case "FLASH_COMPLETE": {
      if (state.phase !== "flashing") {
        return state;
      }
      return {
        ...state,
        phase: "advancing",
      };
    }
    case "ADVANCE_SUCCESS": {
      if (state.phase !== "advancing") {
        return state;
      }

      const play = action.payload;

      if (play.result) {
        return {
          ...state,
          phase: "result",
          puzzle: null,
          result: play.result,
          sessionScore: play.session_score,
          flashKind: null,
          flashBaseScore: null,
          flashTimeBonus: null,
        };
      }

      return {
        ...state,
        phase: "playing",
        puzzle: play.puzzle,
        sessionScore: play.session_score,
        guess: "",
        flashKind: null,
        flashBaseScore: null,
        flashTimeBonus: null,
      };
    }
    case "ADVANCE_ERROR": {
      if (state.phase !== "advancing") {
        return state;
      }
      return {
        ...state,
        phase: "playing",
        errorMessage: action.payload.message,
        flashKind: null,
        flashBaseScore: null,
        flashTimeBonus: null,
      };
    }
    case "ABANDON_SUCCESS": {
      const { result } = action.payload;
      return {
        ...state,
        phase: "result",
        puzzle: null,
        result,
        sessionScore: result.score,
        guess: "",
        errorMessage: null,
        shakeBadgeIndex: null,
        flashKind: null,
        flashBaseScore: null,
        flashTimeBonus: null,
      };
    }
    default:
      return state;
  }
}

export function usePinpointReducer(initialPlay: PlayResponse) {
  return useReducer(pinpointReducer, initialPlay, initPinpointFromPlayResponse);
}
