import { z } from "zod"

const LeaderboardEntryApiSchema = z.object({
  rank: z.number().int(),
  /** Backend field name; same value as JWT `sub` / corp id. */
  player_id: z.string(),
  display_name: z.string(),
  total_score: z.number().int(),
  games_completed: z.number().int(),
})

export const LeaderboardEntrySchema = LeaderboardEntryApiSchema.transform(
  (row) => ({
    rank: row.rank,
    corp_id: row.player_id,
    display_name: row.display_name,
    total_score: row.total_score,
    games_completed: row.games_completed,
  })
)

export type LeaderboardEntry = z.infer<typeof LeaderboardEntrySchema>

export const LeaderboardResponseSchema = z.object({
  entries: z.array(LeaderboardEntrySchema),
  total_players: z.number().int(),
})

export type LeaderboardResponse = z.infer<typeof LeaderboardResponseSchema>
