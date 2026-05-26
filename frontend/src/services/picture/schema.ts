import { z } from "zod";

export const PuzzleSchema = z.object({
  id: z.string(),
  image_filename: z.string(),
  puzzles_answered: z.number().int(),
  puzzles_total: z.number().int(),
});

export type Puzzle = z.infer<typeof PuzzleSchema>;

export const ResultPuzzleSchema = z.object({
  puzzle_id: z.string(),
  image_filename: z.string(),
  status: z.enum(["correct", "skipped", "not_reached", "wrong"]),
  score_earned: z.number().int(),
});

export type ResultPuzzle = z.infer<typeof ResultPuzzleSchema>;

export const ResultSchema = z.object({
  score: z.number().int(),
  accuracy_score: z.number().int(),
  time_bonus: z.number().int(),
  time_remaining_seconds: z.number().int(),
  puzzles: z.array(ResultPuzzleSchema),
});

export type Result = z.infer<typeof ResultSchema>;

export const AbandonResponseSchema = z.object({
  result: ResultSchema,
});

export type AbandonResponse = z.infer<typeof AbandonResponseSchema>;

export const PlayResponseSchema = z.discriminatedUnion("status", [
  z.object({
    status: z.literal("active"),
    game_session_id: z.string(),
    puzzles_answered: z.number().int(),
    puzzles_total: z.number().int(),
    session_started_at: z.string(),
    time_limit_ms: z.number().int(),
    puzzle: PuzzleSchema,
  }),
  z.object({
    status: z.literal("completed"),
    result: ResultSchema,
  }),
  z.object({
    status: z.literal("abandoned"),
    result: ResultSchema,
  }),
]);

export type PlayResponse = z.infer<typeof PlayResponseSchema>;

export const AnswerRequestSchema = z.object({
  puzzle_id: z.string().min(1),
  submitted_answer: z.string().nullable(),
});

export type AnswerRequest = z.infer<typeof AnswerRequestSchema>;

export const AnswerResponseSchema = z.object({
  correct: z.boolean(),
  score_earned: z.number().int(),
  current_score: z.number().int(),
  puzzles_solved: z.number().int(),
  puzzles_remaining: z.number().int(),
  next_puzzle: PuzzleSchema.nullable(),
  result: ResultSchema.nullable(),
});

export type AnswerResponse = z.infer<typeof AnswerResponseSchema>;
