import type { z } from "zod"

import {
  type AbandonResponse,
  AbandonResponseSchema,
  GuessRequestSchema,
  type GuessResponse,
  GuessResponseSchema,
  type PlayResponse,
  PlayResponseSchema,
} from "@/services/pinpoint/schema"

export class PinpointApiError extends Error {
  readonly status: number

  constructor(status: number, message = "Pinpoint request failed") {
    super(message)
    this.name = "PinpointApiError"
    this.status = status
  }
}

export type PostPinpointOptions = {
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
  return new URL("/api/games/pinpoint/play", origin).href
}

function guessHref(origin: string): string {
  return new URL("/api/games/pinpoint/guess", origin).href
}

function abandonHref(origin: string): string {
  return new URL("/api/games/pinpoint/abandon", origin).href
}

/** POST `/api/games/pinpoint/play` (proxied to FastAPI). */
export async function postPinpointPlay(
  options: PostPinpointOptions = {}
): Promise<PlayResponse> {
  const origin = resolveOrigin(options.baseUrl)
  const headers: Record<string, string> = {
    accept: "application/json",
  }
  if (options.cookieHeader) {
    headers.cookie = options.cookieHeader
  }

  const res = await fetch(playHref(origin), {
    method: "POST",
    headers,
    credentials: options.cookieHeader ? "omit" : "include",
  })

  if (!res.ok) {
    throw new PinpointApiError(res.status)
  }

  const json: unknown = await res.json()
  return PlayResponseSchema.parse(json)
}

export type PostGuessBody = z.input<typeof GuessRequestSchema>

/** POST `/api/games/pinpoint/guess` (proxied to FastAPI). */
export async function postPinpointGuess(
  input: PostGuessBody,
  options: PostPinpointOptions = {}
): Promise<GuessResponse> {
  const origin = resolveOrigin(options.baseUrl)
  const body = GuessRequestSchema.parse(input)

  const headers: Record<string, string> = {
    accept: "application/json",
    "content-type": "application/json",
  }
  if (options.cookieHeader) {
    headers.cookie = options.cookieHeader
  }

  const res = await fetch(guessHref(origin), {
    method: "POST",
    headers,
    credentials: options.cookieHeader ? "omit" : "include",
    body: JSON.stringify(body),
  })

  if (!res.ok) {
    throw new PinpointApiError(res.status)
  }

  const json: unknown = await res.json()
  return GuessResponseSchema.parse(json)
}

/** POST `/api/games/pinpoint/abandon` (proxied to FastAPI). */
export async function postPinpointAbandon(
  options: PostPinpointOptions = {}
): Promise<AbandonResponse> {
  const origin = resolveOrigin(options.baseUrl)
  const headers: Record<string, string> = {
    accept: "application/json",
  }
  if (options.cookieHeader) {
    headers.cookie = options.cookieHeader
  }

  const res = await fetch(abandonHref(origin), {
    method: "POST",
    headers,
    credentials: options.cookieHeader ? "omit" : "include",
  })

  if (!res.ok) {
    throw new PinpointApiError(res.status)
  }

  const json: unknown = await res.json()
  return AbandonResponseSchema.parse(json)
}
