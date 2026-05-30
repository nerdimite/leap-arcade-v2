import { z } from "zod"

export const PlayerSessionSchema = z.object({
  game_id: z.string(),
  status: z.enum(["active", "completed", "abandoned"]),
  score: z.number().nullable(),
})

export type PlayerSession = z.infer<typeof PlayerSessionSchema>

export const PlayerSessionsResponseSchema = z.array(PlayerSessionSchema)

export type PlayerSessionsResponse = z.infer<
  typeof PlayerSessionsResponseSchema
>
