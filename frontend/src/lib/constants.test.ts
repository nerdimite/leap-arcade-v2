import { describe, expect, it } from "vitest";

import {
  FEEDBACK_DURATION_MS,
  FOUR_PICS_ANSWER_OVERLAY_MS,
  FOUR_PICS_BASE_SCORE,
  FOUR_PICS_TIME_DECAY_MS,
  LEADERBOARD_POLL_INTERVAL_MS,
  QUESTION_START_DELAY_MS,
} from "./constants";

describe("constants", () => {
  it("exports timing values required by the PRD", () => {
    expect(FEEDBACK_DURATION_MS).toBe(1500);
    expect(QUESTION_START_DELAY_MS).toBe(500);
    expect(LEADERBOARD_POLL_INTERVAL_MS).toBe(5000);
  });

  it("exports Four Pics overlay and scoring constants", () => {
    expect(FOUR_PICS_ANSWER_OVERLAY_MS).toBe(2000);
    expect(FOUR_PICS_BASE_SCORE).toBe(100);
    expect(FOUR_PICS_TIME_DECAY_MS).toBe(30_000);
  });
});
