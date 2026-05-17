import { describe, expect, it } from "vitest";

import type { WikiPlayResponse } from "@/services/wiki/schema";

import type { WikiState } from "../_hooks/useWikiReducer";
import { wikiInitialState } from "../_hooks/useWikiReducer";
import { toWikiViewState, type WikiViewState } from "./wiki-view-state";

function activePlay(): Extract<WikiPlayResponse, { state: "active" }> {
  return {
    state: "active",
    total_score: 10,
    completed_count: 2,
    completed_attempts: [],
    current: {
      game_session_id: "gs",
      attempt_id: "a1",
      round_id: "r1",
      puzzle_index: 3,
      puzzle_count: 5,
      clue: "Find it",
      current_title: "Start",
      time_limit_ms: 180_000,
      time_remaining_ms: 45_000,
      steps_taken: 2,
      click_path: ["A", "B"],
      article_html: "<p>x</p>",
      back_enabled: true,
    },
  };
}

const sampleResult = {
  round_id: "r1",
  puzzle_index: 1,
  clue: "C",
  target_title: "T",
  optimal_click_count: 2,
  steps_taken: 2,
  time_ms: 1000 as number | null | undefined,
  score: 100,
  status: "completed" as const,
};

const uiDefaults = {
  pathRoot: "Root",
  navPending: false,
  continuePending: false,
};

describe("toWikiViewState", () => {
  it("maps loading phase to none (fallback)", () => {
    expect(
      toWikiViewState(
        { ...wikiInitialState, phase: "loading", play: null },
        uiDefaults,
      ),
    ).toEqual({ status: "none" });
  });

  it("maps loading phase with non-active play (impossible reducer shape) to none", () => {
    const terminalPlay: WikiPlayResponse = {
      state: "completed",
      total_score: 0,
      results: [],
    };
    expect(
      toWikiViewState(
        { ...wikiInitialState, phase: "loading", play: terminalPlay },
        uiDefaults,
      ),
    ).toEqual({ status: "none" });
  });

  it("maps active phase with missing play to none", () => {
    expect(
      toWikiViewState(
        {
          ...wikiInitialState,
          phase: "active",
          play: null,
          timerRemainingMs: 5000,
          timerDeadlineAtMs: Date.now() + 5000,
        },
        uiDefaults,
      ),
    ).toEqual({ status: "none" });
  });

  it("maps active phase with terminal play snapshot to none", () => {
    const play: WikiPlayResponse = {
      state: "completed",
      total_score: 99,
      results: [sampleResult],
    };
    expect(
      toWikiViewState({ ...wikiInitialState, phase: "active", play }, uiDefaults),
    ).toEqual({ status: "none" });
  });

  it("maps active phase + active play to active view including pathRoot and pendings", () => {
    const play = activePlay();
    const state: WikiState = {
      ...wikiInitialState,
      phase: "active",
      play,
      timerRemainingMs: 12_000,
      timerDeadlineAtMs: Date.now() + 12_000,
    };
    const expected: WikiViewState = {
      status: "active",
      current: play.current,
      pathRoot: "CustomRoot",
      timerRemainingMs: 12_000,
      completedCount: 2,
      totalScore: 10,
      navPending: true,
    };
    expect(
      toWikiViewState(state, {
        ...uiDefaults,
        pathRoot: "CustomRoot",
        navPending: true,
      }),
    ).toEqual(expected);
  });

  it("uses article time_remaining when timerRemainingMs is null", () => {
    const play = activePlay();
    const state: WikiState = {
      ...wikiInitialState,
      phase: "active",
      play,
      timerRemainingMs: null,
      timerDeadlineAtMs: null,
    };
    const v = toWikiViewState(state, uiDefaults);
    expect(v.status).toBe("active");
    if (v.status === "active") {
      expect(v.timerRemainingMs).toBe(play.current.time_remaining_ms);
    }
  });

  it("maps puzzleResult phase with null puzzleResult to none", () => {
    expect(
      toWikiViewState(
        {
          ...wikiInitialState,
          phase: "puzzleResult",
          puzzleResult: null,
          totalScoreAfterPuzzle: null,
          nextPuzzleAvailable: null,
        },
        uiDefaults,
      ),
    ).toEqual({ status: "none" });
  });

  it("maps puzzleResult phase when puzzleResult is defined", () => {
    const state: WikiState = {
      ...wikiInitialState,
      phase: "puzzleResult",
      puzzleResult: sampleResult,
      totalScoreAfterPuzzle: 180,
      nextPuzzleAvailable: true,
    };
    expect(toWikiViewState(state, { ...uiDefaults, continuePending: true })).toEqual({
      status: "puzzleResult",
      result: sampleResult,
      totalScore: 180,
      hasNext: true,
      continuePending: true,
    });
  });

  it("defaults total score after puzzle when totalScoreAfterPuzzle missing", () => {
    const state: WikiState = {
      ...wikiInitialState,
      phase: "puzzleResult",
      puzzleResult: sampleResult,
      totalScoreAfterPuzzle: null,
      nextPuzzleAvailable: false,
    };
    expect(toWikiViewState(state, uiDefaults)).toEqual({
      status: "puzzleResult",
      result: sampleResult,
      totalScore: sampleResult.score,
      hasNext: false,
      continuePending: false,
    });
  });

  it("maps terminal phase with completed play", () => {
    const state: WikiState = {
      ...wikiInitialState,
      phase: "terminal",
      play: { state: "completed", total_score: 420, results: [sampleResult] },
    };
    expect(toWikiViewState(state, uiDefaults)).toEqual({
      status: "finalCompleted",
      totalScore: 420,
      results: [sampleResult],
    });
  });

  it("maps terminal phase with abandoned play", () => {
    const results = [sampleResult];
    const state: WikiState = {
      ...wikiInitialState,
      phase: "terminal",
      play: { state: "abandoned", total_score: 100, results },
    };
    expect(toWikiViewState(state, uiDefaults)).toEqual({
      status: "finalAbandoned",
      totalScore: 100,
      results,
    });
  });

  it("maps terminal phase with unexpected active play snapshot to none", () => {
    const state: WikiState = {
      ...wikiInitialState,
      phase: "terminal",
      play: activePlay(),
    };
    expect(toWikiViewState(state, uiDefaults)).toEqual({ status: "none" });
  });

  it("maps terminal phase with null play to none", () => {
    expect(
      toWikiViewState({ ...wikiInitialState, phase: "terminal", play: null }, uiDefaults),
    ).toEqual({ status: "none" });
  });

  it("maps error phase with message fallback trimmed to client copy", () => {
    expect(
      toWikiViewState(
        {
          ...wikiInitialState,
          phase: "error",
          errorMessage: null,
        },
        uiDefaults,
      ),
    ).toEqual({ status: "error", message: "Something went wrong" });
  });

  it("maps error phase with explicit message", () => {
    expect(
      toWikiViewState(
        {
          ...wikiInitialState,
          phase: "error",
          errorMessage: "Network failed",
        },
        uiDefaults,
      ),
    ).toEqual({ status: "error", message: "Network failed" });
  });
});
