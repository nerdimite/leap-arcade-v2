import type { z } from "zod"

import {
  FindRequestSchema,
  type FindResponse,
  FindResponseSchema,
  type PlayResponse,
  PlayResponseSchema,
  type SubmitResponse,
  SubmitResponseSchema,
} from "@/services/word_hunt/schema"

export class WordHuntApiError extends Error {
  readonly status: number

  constructor(status: number, message = "Word Hunt request failed") {
    super(message)
    this.name = "WordHuntApiError"
    this.status = status
  }
}

export type PostWordHuntOptions = {
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
  return new URL("/api/games/word-hunt/play", origin).href
}

function findHref(origin: string): string {
  return new URL("/api/games/word-hunt/find", origin).href
}

function submitHref(origin: string): string {
  return new URL("/api/games/word-hunt/submit", origin).href
}

function buildHeaders(cookieHeader?: string): Record<string, string> {
  const headers: Record<string, string> = {
    accept: "application/json",
  }
  if (cookieHeader) {
    headers.cookie = cookieHeader
  }
  return headers
}

export async function postPlay(
  options: PostWordHuntOptions = {}
): Promise<PlayResponse> {
  const origin = resolveOrigin(options.baseUrl)
  const res = await fetch(playHref(origin), {
    method: "POST",
    headers: buildHeaders(options.cookieHeader),
    credentials: options.cookieHeader ? "omit" : "include",
  })

  if (!res.ok) {
    throw new WordHuntApiError(res.status)
  }

  const json: unknown = await res.json()
  return PlayResponseSchema.parse(json)
}

export type PostFindBody = z.input<typeof FindRequestSchema>

export async function postFind(
  input: PostFindBody,
  options: PostWordHuntOptions = {}
): Promise<FindResponse> {
  const origin = resolveOrigin(options.baseUrl)
  const body = FindRequestSchema.parse(input)

  const headers = buildHeaders(options.cookieHeader)
  headers["content-type"] = "application/json"

  const res = await fetch(findHref(origin), {
    method: "POST",
    headers,
    credentials: options.cookieHeader ? "omit" : "include",
    body: JSON.stringify(body),
  })

  if (!res.ok) {
    throw new WordHuntApiError(res.status)
  }

  const json: unknown = await res.json()
  return FindResponseSchema.parse(json)
}

export async function postSubmit(
  options: PostWordHuntOptions = {}
): Promise<SubmitResponse> {
  const origin = resolveOrigin(options.baseUrl)
  const res = await fetch(submitHref(origin), {
    method: "POST",
    headers: buildHeaders(options.cookieHeader),
    credentials: options.cookieHeader ? "omit" : "include",
  })

  if (!res.ok) {
    throw new WordHuntApiError(res.status)
  }

  const json: unknown = await res.json()
  return SubmitResponseSchema.parse(json)
}
