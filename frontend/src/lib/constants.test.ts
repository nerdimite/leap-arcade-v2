import { describe, expect, it } from "vitest";

import {
  FEEDBACK_DURATION_MS,
  LEADERBOARD_POLL_INTERVAL_MS,
  QUESTION_START_DELAY_MS,
} from "./constants";

describe("constants", () => {
  it("exports timing values required by the PRD", () => {
    expect(FEEDBACK_DURATION_MS).toBe(1500);
    expect(QUESTION_START_DELAY_MS).toBe(500);
    expect(LEADERBOARD_POLL_INTERVAL_MS).toBe(5000);
  });
});
