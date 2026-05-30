import { z } from "zod"

export const QuestionSchema = z.object({
  id: z.string(),
  question: z.string(),
  options: z.array(z.string()).length(4),
  time_limit_ms: z.number().int(),
})

export type Question = z.infer<typeof QuestionSchema>

export const ResultSchema = z.object({
  score: z.number().int(),
  correct_count: z.number().int(),
  wrong_count: z.number().int(),
  skipped_count: z.number().int(),
  time_taken_seconds: z.number(),
})

export type Result = z.infer<typeof ResultSchema>

export const PlayResponseSchema = z.discriminatedUnion("status", [
  z.object({
    status: z.literal("active"),
    game_session_id: z.string(),
    questions_answered: z.number().int(),
    questions_total: z.number().int(),
    question: QuestionSchema,
  }),
  z.object({
    status: z.literal("completed"),
    result: ResultSchema,
  }),
  z.object({
    status: z.literal("abandoned"),
    result: ResultSchema,
  }),
])

export type PlayResponse = z.infer<typeof PlayResponseSchema>

export const AnswerRequestSchema = z.object({
  question_id: z.string().min(1),
  selected_option: z.number().int().min(1).max(4).nullable(),
  time_ms: z.number().int().min(0),
})

export type AnswerRequest = z.infer<typeof AnswerRequestSchema>

export const AnswerResponseSchema = z.object({
  correct: z.boolean(),
  correct_option: z.number().int(),
  correct_answer_text: z.string(),
  current_score: z.number().int(),
  questions_answered: z.number().int(),
  questions_remaining: z.number().int(),
  next_question: QuestionSchema.nullable(),
  result: ResultSchema.nullable(),
})

export type AnswerResponse = z.infer<typeof AnswerResponseSchema>

export const AbandonResponseSchema = z.object({
  result: ResultSchema,
})

export type AbandonResponse = z.infer<typeof AbandonResponseSchema>
