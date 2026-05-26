import { z } from "zod";

export const CoordinatesSchema = z.object({
  start_row: z.number(),
  start_col: z.number(),
  end_row: z.number(),
  end_col: z.number(),
});

export const ClueSchema = z.object({
  word_id: z.string(),
  clue: z.string(),
  found: z.boolean(),
  word: z.string().nullable().optional(),
  coordinates: CoordinatesSchema.nullable().optional(),
});

export const PuzzleStateSchema = z.object({
  puzzle_id: z.string(),
  rows: z.number(),
  cols: z.number(),
  grid: z.array(z.array(z.string())),
  clues: z.array(ClueSchema),
  found_count: z.number(),
  total_words: z.number(),
  started_at: z.string(),
});

export const FoundWordSchema = z.object({
  word_id: z.string(),
  word: z.string(),
  clue: z.string(),
  coordinates: CoordinatesSchema,
});

export const ResultSchema = z.object({
  score: z.number(),
  base_score: z.number(),
  time_bonus: z.number(),
  time_elapsed_ms: z.number(),
  found_count: z.number(),
  total_words: z.number(),
  found_words: z.array(FoundWordSchema),
});

export const PlayResponseSchema = z.object({
  session_status: z.string(),
  session_score: z.number(),
  puzzle: PuzzleStateSchema.nullable(),
  result: ResultSchema.nullable(),
});

export const FindRequestSchema = z.object({
  start_row: z.number().int().min(0),
  start_col: z.number().int().min(0),
  end_row: z.number().int().min(0),
  end_col: z.number().int().min(0),
});

export const FindResponseSchema = z.object({
  matched: z.boolean(),
  word: FoundWordSchema.nullable(),
  session_status: z.string(),
  session_score: z.number(),
  result: ResultSchema.nullable(),
});

export const SubmitResponseSchema = z.object({
  result: ResultSchema,
});

export type Coordinates = z.infer<typeof CoordinatesSchema>;
export type Clue = z.infer<typeof ClueSchema>;
export type PuzzleState = z.infer<typeof PuzzleStateSchema>;
export type FoundWord = z.infer<typeof FoundWordSchema>;
export type Result = z.infer<typeof ResultSchema>;
export type PlayResponse = z.infer<typeof PlayResponseSchema>;
export type FindRequest = z.infer<typeof FindRequestSchema>;
export type FindResponse = z.infer<typeof FindResponseSchema>;
export type SubmitResponse = z.infer<typeof SubmitResponseSchema>;
