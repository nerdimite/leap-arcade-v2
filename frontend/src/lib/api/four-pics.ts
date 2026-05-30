import type { z } from "zod"

import {
  type AbandonResponse,
  AbandonResponseSchema,
  AnswerRequestSchema,
  type AnswerResponse,
  AnswerResponseSchema,
  type PlayResponse,
  PlayResponseSchema,
} from "@/services/four_pics/schema"

export class FourPicsApiError extends Error {
  readonly status: number

  constructor(status: number, message = "Four Pics request failed") {
    super(message)
    this.name = "FourPicsApiError"
    this.status = status
  }
}

export type PostFourPicsOptions = {
  baseUrl?: string
  cookieHeader?: string
}

function resolveOrigin(baseUrl?: string): string {
  if (baseUrl) {
    return baseUrl.replace(/\/$/, "")
  }
  if (typeof window !== "undefined" && window.location?.origin) {
    return window.location.origin
  }
  return "http://localhost:3000"
}

function playHref(origin: string): string {
  return new URL("/api/games/four-pics/play", origin).href
}

function answerHref(origin: string): string {
  return new URL("/api/games/four-pics/answer", origin).href
}

function abandonHref(origin: string): string {
  return new URL("/api/games/four-pics/abandon", origin).href
}

export async function postPlay(
  options: PostFourPicsOptions = {}
): Promise<PlayResponse> {
  const origin = resolveOrigin(options.baseUrl)
  const headers: Record<string, string> = { accept: "application/json" }
  if (options.cookieHeader) {
    headers.cookie = options.cookieHeader
  }

  const res = await fetch(playHref(origin), {
    method: "POST",
    headers,
    credentials: options.cookieHeader ? "omit" : "include",
  })

  if (!res.ok) {
    throw new FourPicsApiError(res.status)
  }

  const json: unknown = await res.json()
  return PlayResponseSchema.parse(json)
}

export type PostAnswerBody = z.input<typeof AnswerRequestSchema>

export async function postAnswer(
  input: PostAnswerBody,
  options: PostFourPicsOptions = {}
): Promise<AnswerResponse> {
  const origin = resolveOrigin(options.baseUrl)
  const body = AnswerRequestSchema.parse(input)

  const headers: Record<string, string> = {
    accept: "application/json",
    "content-type": "application/json",
  }
  if (options.cookieHeader) {
    headers.cookie = options.cookieHeader
  }

  const res = await fetch(answerHref(origin), {
    method: "POST",
    headers,
    credentials: options.cookieHeader ? "omit" : "include",
    body: JSON.stringify(body),
  })

  if (!res.ok) {
    throw new FourPicsApiError(res.status)
  }

  const json: unknown = await res.json()
  return AnswerResponseSchema.parse(json)
}

/** POST `/api/games/four-pics/abandon` (proxied to FastAPI). */
export async function postAbandon(
  options: PostFourPicsOptions = {}
): Promise<AbandonResponse> {
  const origin = resolveOrigin(options.baseUrl)
  const headers: Record<string, string> = { accept: "application/json" }
  if (options.cookieHeader) {
    headers.cookie = options.cookieHeader
  }

  const res = await fetch(abandonHref(origin), {
    method: "POST",
    headers,
    credentials: options.cookieHeader ? "omit" : "include",
  })

  if (!res.ok) {
    throw new FourPicsApiError(res.status)
  }

  const json: unknown = await res.json()
  return AbandonResponseSchema.parse(json)
}
