import { z } from "zod"

export const QuestionStateSchema = z.object({
  question_id: z.string(),
  question_number: z.number().int(),
  total_questions: z.number().int(),
  image_paths: z.array(z.string()).length(4),
  status: z.literal("active"),
  started_at: z.string(),
})

export type QuestionState = z.infer<typeof QuestionStateSchema>

export const ResultQuestionSchema = z.object({
  question_id: z.string(),
  status: z.enum(["correct", "wrong", "not_reached"]),
  score: z.number().int(),
  time_bonus: z.number().int(),
})

export type ResultQuestion = z.infer<typeof ResultQuestionSchema>

export const ResultSchema = z.object({
  score: z.number().int(),
  questions_correct: z.number().int(),
  questions_wrong: z.number().int(),
  questions_not_reached: z.number().int(),
  questions: z.array(ResultQuestionSchema),
})

export type Result = z.infer<typeof ResultSchema>

export const PlayResponseSchema = z.object({
  session_status: z.enum(["active", "completed", "abandoned"]),
  session_score: z.number().int(),
  question: QuestionStateSchema.nullable(),
  result: ResultSchema.nullable(),
})

export type PlayResponse = z.infer<typeof PlayResponseSchema>

export const AnswerRequestSchema = z.object({
  question_id: z.string().min(1),
  selected_index: z.number().int().min(0).max(3),
  time_ms: z.number().int().min(0),
})

export type AnswerRequest = z.infer<typeof AnswerRequestSchema>

export const AnswerResponseSchema = z.object({
  correct: z.boolean(),
  score: z.number().int(),
  time_bonus: z.number().int(),
  session_status: z.enum(["active", "completed"]),
  session_score: z.number().int(),
  question: QuestionStateSchema.nullable(),
  result: ResultSchema.nullable(),
})

export type AnswerResponse = z.infer<typeof AnswerResponseSchema>

export const AbandonResponseSchema = z.object({
  result: ResultSchema,
})

export type AbandonResponse = z.infer<typeof AbandonResponseSchema>
