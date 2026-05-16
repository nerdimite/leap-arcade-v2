import { describe, expect, it } from "vitest";

import { LeaderboardEntrySchema, LeaderboardResponseSchema } from "./schema";

describe("LeaderboardEntrySchema", () => {
  it("parses a valid API entry into corp_id form", () => {
    const parsed = LeaderboardEntrySchema.parse({
      rank: 1,
      player_id: "alice",
      display_name: "Alice",
      total_score: 100,
      games_completed: 2,
    });
    expect(parsed).toEqual({
      rank: 1,
      corp_id: "alice",
      display_name: "Alice",
      total_score: 100,
      games_completed: 2,
    });
  });

  it("rejects entries missing total_score", () => {
    const result = LeaderboardEntrySchema.safeParse({
      rank: 1,
      player_id: "alice",
      display_name: "Alice",
      games_completed: 0,
    });
    expect(result.success).toBe(false);
  });
});

describe("LeaderboardResponseSchema", () => {
  it("parses leaderboard payload", () => {
    const parsed = LeaderboardResponseSchema.parse({
      entries: [
        {
          rank: 1,
          player_id: "a",
          display_name: "A",
          total_score: 10,
          games_completed: 1,
        },
      ],
      total_players: 1,
    });
    expect(parsed.total_players).toBe(1);
    expect(parsed.entries[0]?.corp_id).toBe("a");
  });
});
