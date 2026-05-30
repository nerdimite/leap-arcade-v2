import { z } from "zod"

export const LoginRequestSchema = z.object({
  corp_id: z.string().min(1),
  event_code: z.string().min(1),
})

export type LoginRequest = z.infer<typeof LoginRequestSchema>

export const LoginOkResponseSchema = z.object({
  ok: z.literal(true),
})

export type LoginOkResponse = z.infer<typeof LoginOkResponseSchema>
