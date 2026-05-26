import { z } from "zod";

export const PuzzleStateSchema = z.object({
  puzzle_id: z.string(),
  puzzle_number: z.number().int(),
  total_puzzles: z.number().int(),
  clues_revealed: z.number().int(),
  clues: z.array(z.string()),
  status: z.enum(["active", "solved", "failed"]),
  score: z.number().int().nullable(),
  time_bonus: z.number().int().nullable(),
  started_at: z.string().datetime(),
});

export type PuzzleState = z.infer<typeof PuzzleStateSchema>;

export const ResultPuzzleSchema = z.object({
  puzzle_id: z.string(),
  status: z.enum(["solved", "failed", "not_reached"]),
  clues_used: z.number().int().nullable(),
  score: z.number().int(),
  time_bonus: z.number().int(),
});

export type ResultPuzzle = z.infer<typeof ResultPuzzleSchema>;

export const ResultSchema = z.object({
  score: z.number().int(),
  puzzles_solved: z.number().int(),
  puzzles_failed: z.number().int(),
  puzzles_not_reached: z.number().int(),
  puzzles: z.array(ResultPuzzleSchema),
});

export type Result = z.infer<typeof ResultSchema>;

export const PlayResponseSchema = z.object({
  session_status: z.enum(["active", "completed", "abandoned"]),
  session_score: z.number().int(),
  puzzle: PuzzleStateSchema.nullable(),
  result: ResultSchema.nullable(),
});

export type PlayResponse = z.infer<typeof PlayResponseSchema>;

export const GuessRequestSchema = z.object({
  puzzle_id: z.string().min(1),
  guess: z.string().min(1),
});

export type GuessRequest = z.infer<typeof GuessRequestSchema>;

export const GuessResponseSchema = z.object({
  correct: z.boolean(),
  puzzle: PuzzleStateSchema,
  session_status: z.enum(["active", "completed", "abandoned"]),
  session_score: z.number().int(),
  result: ResultSchema.nullable(),
});

export type GuessResponse = z.infer<typeof GuessResponseSchema>;

export const AbandonResponseSchema = z.object({
  result: ResultSchema,
});

export type AbandonResponse = z.infer<typeof AbandonResponseSchema>;
