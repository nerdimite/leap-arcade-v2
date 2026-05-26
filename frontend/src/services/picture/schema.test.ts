import { describe, expect, it } from "vitest";

import { PlayResponseSchema, ResultSchema } from "./schema";

const sampleResult = {
  score: 212,
  accuracy_score: 150,
  time_bonus: 62,
  time_remaining_seconds: 134,
  puzzles: [
    {
      puzzle_id: "p1",
      image_filename: "huggingface.png",
      status: "correct" as const,
      score_earned: 150,
    },
    {
      puzzle_id: "p2",
      image_filename: "nlp.png",
      status: "skipped" as const,
      score_earned: 0,
    },
    {
      puzzle_id: "p3",
      image_filename: "large_language_model.png",
      status: "not_reached" as const,
      score_earned: 0,
    },
  ],
};

describe("ResultSchema", () => {
  it("parses backend result payloads without answer fields", () => {
    const parsed = ResultSchema.parse(sampleResult);
    expect(parsed.score).toBe(212);
    expect(parsed.puzzles).toHaveLength(3);
    expect(parsed.puzzles[0]?.status).toBe("correct");
    expect(Object.keys(parsed)).not.toContain("canonical_answer");
  });

  it("accepts wrong puzzle status for forward-compatible APIs", () => {
    const parsed = ResultSchema.parse({
      ...sampleResult,
      puzzles: [
        {
          puzzle_id: "p1",
          image_filename: "x.png",
          status: "wrong",
          score_earned: 0,
        },
      ],
    });
    expect(parsed.puzzles[0]?.status).toBe("wrong");
  });
});

describe("PlayResponseSchema", () => {
  it("parses completed branch with result only (no puzzle shell)", () => {
    const raw = {
      status: "completed",
      result: sampleResult,
    };
    const parsed = PlayResponseSchema.parse(raw);
    expect(parsed.status).toBe("completed");
    if (parsed.status !== "completed") {
      throw new Error("expected completed");
    }
    expect(parsed.result).toEqual(sampleResult);
    expect("puzzle" in parsed).toBe(false);
    expect("session_started_at" in parsed).toBe(false);
  });
});
