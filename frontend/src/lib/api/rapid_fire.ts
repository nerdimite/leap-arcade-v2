import type { z } from "zod";

import {
  type AbandonResponse,
  AbandonResponseSchema,
  AnswerRequestSchema,
  type AnswerResponse,
  AnswerResponseSchema,
  type PlayResponse,
  PlayResponseSchema,
} from "@/services/rapid_fire/schema";

export class RapidFireApiError extends Error {
  readonly status: number;

  constructor(status: number, message = "Rapid Fire request failed") {
    super(message);
    this.name = "RapidFireApiError";
    this.status = status;
  }
}

export type PostRapidFireOptions = {
  /** Absolute site origin, e.g. `https://example.com` — required for server-side fetch. */
  baseUrl?: string;
  /** Raw `Cookie` header (server components); browser omits this and uses `credentials: "include"`. */
  cookieHeader?: string;
};

function resolveOrigin(baseUrl?: string): string {
  if (baseUrl) {
    return baseUrl.replace(/\/$/, "");
  }
  if (typeof window !== "undefined" && window.location?.origin) {
    return window.location.origin;
  }
  return "http://localhost:3000";
}

function playHref(origin: string): string {
  return new URL("/api/games/rapid-fire/play", origin).href;
}

function answerHref(origin: string): string {
  return new URL("/api/games/rapid-fire/answer", origin).href;
}

function abandonHref(origin: string): string {
  return new URL("/api/games/rapid-fire/abandon", origin).href;
}

/** POST `/api/games/rapid-fire/play` (proxied to FastAPI). */
export async function postPlay(options: PostRapidFireOptions = {}): Promise<PlayResponse> {
  const origin = resolveOrigin(options.baseUrl);
  const headers: Record<string, string> = {
    accept: "application/json",
  };
  if (options.cookieHeader) {
    headers.cookie = options.cookieHeader;
  }

  const res = await fetch(playHref(origin), {
    method: "POST",
    headers,
    credentials: options.cookieHeader ? "omit" : "include",
  });

  if (!res.ok) {
    throw new RapidFireApiError(res.status);
  }

  const json: unknown = await res.json();
  return PlayResponseSchema.parse(json);
}

export type PostAnswerBody = z.input<typeof AnswerRequestSchema>;

/** POST `/api/games/rapid-fire/answer` (proxied to FastAPI). */
export async function postAnswer(
  input: PostAnswerBody,
  options: PostRapidFireOptions = {},
): Promise<AnswerResponse> {
  const origin = resolveOrigin(options.baseUrl);
  const body = AnswerRequestSchema.parse(input);

  const headers: Record<string, string> = {
    accept: "application/json",
    "content-type": "application/json",
  };
  if (options.cookieHeader) {
    headers.cookie = options.cookieHeader;
  }

  const res = await fetch(answerHref(origin), {
    method: "POST",
    headers,
    credentials: options.cookieHeader ? "omit" : "include",
    body: JSON.stringify({
      question_id: body.question_id,
      selected_option: body.selected_option,
      time_ms: body.time_ms,
    }),
  });

  if (!res.ok) {
    throw new RapidFireApiError(res.status);
  }

  const json: unknown = await res.json();
  return AnswerResponseSchema.parse(json);
}

/** POST `/api/games/rapid-fire/abandon` (proxied to FastAPI). */
export async function postAbandon(options: PostRapidFireOptions = {}): Promise<AbandonResponse> {
  const origin = resolveOrigin(options.baseUrl);
  const headers: Record<string, string> = {
    accept: "application/json",
  };
  if (options.cookieHeader) {
    headers.cookie = options.cookieHeader;
  }

  const res = await fetch(abandonHref(origin), {
    method: "POST",
    headers,
    credentials: options.cookieHeader ? "omit" : "include",
  });

  if (!res.ok) {
    throw new RapidFireApiError(res.status);
  }

  const json: unknown = await res.json();
  return AbandonResponseSchema.parse(json);
}
