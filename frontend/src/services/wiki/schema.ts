import { z } from "zod"

export const WikiPuzzleResultSchema = z.object({
  round_id: z.string(),
  puzzle_index: z.number().int(),
  clue: z.string(),
  target_title: z.string(),
  optimal_click_count: z.number().int(),
  steps_taken: z.number().int(),
  time_ms: z.number().int().nullable().optional(),
  score: z.number().int(),
  status: z.enum(["active", "completed", "timed_out", "abandoned"]),
})

export type WikiPuzzleResult = z.infer<typeof WikiPuzzleResultSchema>

export const WikiActivePuzzleSchema = z.object({
  game_session_id: z.string(),
  attempt_id: z.string(),
  round_id: z.string(),
  puzzle_index: z.number().int(),
  puzzle_count: z.number().int(),
  clue: z.string(),
  current_title: z.string(),
  time_limit_ms: z.number().int(),
  time_remaining_ms: z.number().int(),
  steps_taken: z.number().int(),
  click_path: z.array(z.string()),
  article_html: z.string(),
  back_enabled: z.boolean(),
})

export type WikiActivePuzzle = z.infer<typeof WikiActivePuzzleSchema>

export const WikiPlayResponseSchema = z.discriminatedUnion("state", [
  z.object({
    state: z.literal("active"),
    total_score: z.number().int(),
    completed_count: z.number().int(),
    current: WikiActivePuzzleSchema,
    completed_attempts: z.array(WikiPuzzleResultSchema),
  }),
  z.object({
    state: z.literal("completed"),
    total_score: z.number().int(),
    results: z.array(WikiPuzzleResultSchema),
  }),
  z.object({
    state: z.literal("abandoned"),
    total_score: z.number().int(),
    results: z.array(WikiPuzzleResultSchema),
  }),
])

export type WikiPlayResponse = z.infer<typeof WikiPlayResponseSchema>

export const WikiNavigateRequestSchema = z.object({
  title: z.string().min(1),
})

export const WikiNavigateResponseSchema = z.discriminatedUnion("state", [
  z.object({
    state: z.literal("active"),
    current: WikiActivePuzzleSchema,
  }),
  z.object({
    state: z.literal("puzzle_completed"),
    puzzle_result: WikiPuzzleResultSchema,
    next_puzzle_available: z.boolean(),
    total_score: z.number().int(),
  }),
])

export type WikiNavigateResponse = z.infer<typeof WikiNavigateResponseSchema>
