import { describe, expect, it } from "vitest";

import type {
  WikiActivePuzzle,
  WikiNavigateResponse,
  WikiPlayResponse,
  WikiPuzzleResult,
} from "@/services/wiki/schema";

import { wikiInitialState, wikiReducer } from "./useWikiReducer";

function baseCurrent(overrides: Partial<WikiActivePuzzle> = {}): WikiActivePuzzle {
  return {
    game_session_id: "gs",
    attempt_id: "att1",
    round_id: "r1",
    puzzle_index: 1,
    puzzle_count: 5,
    clue: "Clue",
    current_title: "Start",
    time_limit_ms: 120_000,
    time_remaining_ms: 120_000,
    steps_taken: 0,
    click_path: [],
    article_html: "<p>x</p>",
    back_enabled: false,
    ...overrides,
  };
}

function activePlay(o: {
  current: WikiActivePuzzle;
  total_score?: number;
  completed_count?: number;
  completed_attempts?: WikiPuzzleResult[];
}): Extract<WikiPlayResponse, { state: "active" }> {
  return {
    state: "active",
    total_score: o.total_score ?? 0,
    completed_count: o.completed_count ?? 0,
    completed_attempts: o.completed_attempts ?? [],
    current: o.current,
  };
}

const samplePuzzleResult: WikiPuzzleResult = {
  round_id: "r1",
  puzzle_index: 1,
  clue: "Clue",
  target_title: "Target",
  optimal_click_count: 1,
  steps_taken: 1,
  time_ms: 10,
  score: 200,
  status: "completed",
};

describe("wikiReducer", () => {
  it("TICK decrements displayed timer while phase stays active (e.g. during navigation loading)", () => {
    const s0 = wikiReducer(wikiInitialState, {
      type: "PLAY_OK",
      payload: activePlay({
        current: baseCurrent({ time_remaining_ms: 10_000 }),
      }),
    });
    expect(s0.timerRemainingMs).toBe(10_000);
    expect(s0.timerDeadlineAtMs).not.toBeNull();
    const t0 = s0.timerDeadlineAtMs;
    if (t0 == null) {
      throw new Error("expected timer deadline");
    }
    const s1 = wikiReducer(s0, { type: "TICK", payload: { nowMs: t0 - 7000 } });
    expect(s1.timerRemainingMs).toBe(7000);
    expect(s1.phase).toBe("active");
  });

  it("navigate puzzle_completed then PLAY_OK resumes active next puzzle", () => {
    let s = wikiReducer(wikiInitialState, {
      type: "PLAY_OK",
      payload: activePlay({
        current: baseCurrent({ puzzle_index: 1, attempt_id: "a1", round_id: "r1" }),
      }),
    });
    expect(s.phase).toBe("active");

    const nav: WikiNavigateResponse = {
      state: "puzzle_completed",
      puzzle_result: samplePuzzleResult,
      next_puzzle_available: true,
      total_score: 200,
    };
    s = wikiReducer(s, { type: "NAVIGATE_OK", payload: nav });
    expect(s.phase).toBe("puzzleResult");
    expect(s.nextPuzzleAvailable).toBe(true);

    const nextPlay = activePlay({
      total_score: 200,
      completed_count: 1,
      completed_attempts: [samplePuzzleResult],
      current: baseCurrent({
        puzzle_index: 2,
        attempt_id: "a2",
        round_id: "r2",
        clue: "Next clue",
        current_title: "S2",
      }),
    });

    s = wikiReducer(s, { type: "PLAY_OK", payload: nextPlay });
    expect(s.phase).toBe("active");
    expect(s.play?.state === "active" && s.play.current.puzzle_index).toBe(2);
    expect(s.puzzleResult).toBeNull();
  });

  it("final puzzle_completed then PLAY_OK enters terminal with results", () => {
    let s = wikiReducer(wikiInitialState, {
      type: "PLAY_OK",
      payload: activePlay({
        current: baseCurrent({ puzzle_index: 5, attempt_id: "a5" }),
        completed_count: 4,
      }),
    });

    const nav: WikiNavigateResponse = {
      state: "puzzle_completed",
      puzzle_result: { ...samplePuzzleResult, puzzle_index: 5, round_id: "r5" },
      next_puzzle_available: false,
      total_score: 1000,
    };
    s = wikiReducer(s, { type: "NAVIGATE_OK", payload: nav });
    expect(s.phase).toBe("puzzleResult");
    expect(s.nextPuzzleAvailable).toBe(false);

    const terminal: WikiPlayResponse = {
      state: "completed",
      total_score: 1000,
      results: [
        { ...samplePuzzleResult, puzzle_index: 1, round_id: "r1" },
        { ...samplePuzzleResult, puzzle_index: 2, round_id: "r2", score: 200 },
        { ...samplePuzzleResult, puzzle_index: 3, round_id: "r3", score: 200 },
        { ...samplePuzzleResult, puzzle_index: 4, round_id: "r4", score: 200 },
        { ...samplePuzzleResult, puzzle_index: 5, round_id: "r5", score: 200 },
      ],
    };

    s = wikiReducer(s, { type: "PLAY_OK", payload: terminal });
    expect(s.phase).toBe("terminal");
    expect(s.play?.state).toBe("completed");
    expect(s.play?.state === "completed" && s.play.results.length).toBe(5);
  });
});
