/** Maps wiki reducer phase + play payload to dumb view variants (ADR-0005 §4). */

import type { WikiActivePuzzle, WikiPuzzleResult } from "@/services/wiki/schema";

import type { WikiState } from "../_hooks/useWikiReducer";

export type WikiViewState =
  | { status: "finalCompleted"; totalScore: number; results: WikiPuzzleResult[] }
  | { status: "finalAbandoned"; totalScore: number; results: WikiPuzzleResult[] }
  | { status: "error"; message: string }
  | {
      status: "puzzleResult";
      result: WikiPuzzleResult;
      totalScore: number;
      hasNext: boolean;
      continuePending: boolean;
    }
  | {
      status: "active";
      current: WikiActivePuzzle;
      pathRoot: string;
      timerRemainingMs: number;
      completedCount: number;
      totalScore: number;
      navPending: boolean;
    }
  | { status: "none" };

export function toWikiViewState(
  state: WikiState,
  ui: { pathRoot: string; navPending: boolean; continuePending: boolean },
): WikiViewState {
  if (state.phase === "terminal" && state.play != null) {
    const play = state.play;
    if (play.state === "completed") {
      return {
        status: "finalCompleted",
        totalScore: play.total_score,
        results: play.results,
      };
    }
    if (play.state === "abandoned") {
      return {
        status: "finalAbandoned",
        totalScore: play.total_score,
        results: play.results,
      };
    }
  }

  if (state.phase === "error") {
    return {
      status: "error",
      message: state.errorMessage ?? "Something went wrong",
    };
  }

  if (state.phase === "puzzleResult") {
    if (state.puzzleResult == null) {
      return { status: "none" };
    }
    const total = state.totalScoreAfterPuzzle ?? state.puzzleResult.score;
    const hasNext = state.nextPuzzleAvailable === true;
    return {
      status: "puzzleResult",
      result: state.puzzleResult,
      totalScore: total,
      hasNext,
      continuePending: ui.continuePending,
    };
  }

  if (state.phase === "active" && state.play?.state === "active") {
    const { current, completed_count, total_score } = state.play;
    const timerRemainingMs = state.timerRemainingMs ?? current.time_remaining_ms;
    return {
      status: "active",
      current,
      pathRoot: ui.pathRoot,
      timerRemainingMs,
      completedCount: completed_count,
      totalScore: total_score,
      navPending: ui.navPending,
    };
  }

  return { status: "none" };
}
