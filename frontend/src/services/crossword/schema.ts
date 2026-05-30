import { z } from "zod";

export const CellCoordinateSchema = z.object({
  row: z.number(),
  col: z.number(),
});

export const CellSkeletonSchema = z.object({
  row: z.number(),
  col: z.number(),
  number: z.number().nullable().optional(),
  letter: z.string().nullable().optional(),
});

export const ClueSchema = z.object({
  entry_id: z.string(),
  number: z.number(),
  direction: z.string(),
  clue: z.string(),
  length: z.number(),
  start_row: z.number(),
  start_col: z.number(),
  solved: z.boolean(),
  answer: z.string().nullable().optional(),
  cells: z.array(CellCoordinateSchema).nullable().optional(),
});

export const PuzzleStateSchema = z.object({
  puzzle_id: z.string(),
  rows: z.number(),
  cols: z.number(),
  cells: z.array(z.array(CellSkeletonSchema.nullable())),
  clues: z.array(ClueSchema),
  solved_count: z.number(),
  total_entries: z.number(),
  started_at: z.string(),
});

export const SolvedEntrySchema = z.object({
  entry_id: z.string(),
  number: z.number(),
  direction: z.string(),
  clue: z.string(),
  answer: z.string(),
  cells: z.array(CellCoordinateSchema),
});

export const ResultSchema = z.object({
  score: z.number(),
  base_score: z.number(),
  time_bonus: z.number(),
  time_elapsed_ms: z.number(),
  solved_count: z.number(),
  total_entries: z.number(),
  solved_entries: z.array(SolvedEntrySchema),
});

export const PlayResponseSchema = z.object({
  session_status: z.string(),
  session_score: z.number(),
  puzzle: PuzzleStateSchema.nullable(),
  result: ResultSchema.nullable(),
});

export const CheckRequestSchema = z.object({
  entry_id: z.string(),
  letters: z.string(),
});

export const CheckResponseSchema = z.object({
  correct: z.boolean(),
  entry: SolvedEntrySchema.nullable(),
  session_status: z.string(),
  session_score: z.number(),
  result: ResultSchema.nullable(),
});

export const SubmitResponseSchema = z.object({
  result: ResultSchema,
});

export type CellCoordinate = z.infer<typeof CellCoordinateSchema>;
export type CellSkeleton = z.infer<typeof CellSkeletonSchema>;
export type Clue = z.infer<typeof ClueSchema>;
export type PuzzleState = z.infer<typeof PuzzleStateSchema>;
export type SolvedEntry = z.infer<typeof SolvedEntrySchema>;
export type Result = z.infer<typeof ResultSchema>;
export type PlayResponse = z.infer<typeof PlayResponseSchema>;
export type CheckRequest = z.infer<typeof CheckRequestSchema>;
export type CheckResponse = z.infer<typeof CheckResponseSchema>;
export type SubmitResponse = z.infer<typeof SubmitResponseSchema>;
