import type { z } from "zod";

import {
  type AbandonResponse,
  AbandonResponseSchema,
  AnswerRequestSchema,
  type AnswerResponse,
  AnswerResponseSchema,
  type PlayResponse,
  PlayResponseSchema,
} from "@/services/picture/schema";

export class PictureApiError extends Error {
  readonly status: number;

  constructor(status: number, message = "Picture Illustration request failed") {
    super(message);
    this.name = "PictureApiError";
    this.status = status;
  }
}

export type PostPictureOptions = {
  baseUrl?: string;
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
  return new URL("/api/games/picture/play", origin).href;
}

function answerHref(origin: string): string {
  return new URL("/api/games/picture/answer", origin).href;
}

function abandonHref(origin: string): string {
  return new URL("/api/games/picture/abandon", origin).href;
}

/** POST `/api/games/picture/play` (proxied to FastAPI). */
export async function postPlay(options: PostPictureOptions = {}): Promise<PlayResponse> {
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
    throw new PictureApiError(res.status);
  }

  const json: unknown = await res.json();
  return PlayResponseSchema.parse(json);
}

export type PostAnswerBody = z.input<typeof AnswerRequestSchema>;

/** POST `/api/games/picture/answer` (proxied to FastAPI). */
export async function postPictureAnswer(
  input: PostAnswerBody,
  options: PostPictureOptions = {},
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
      puzzle_id: body.puzzle_id,
      submitted_answer: body.submitted_answer,
    }),
  });

  if (!res.ok) {
    throw new PictureApiError(res.status);
  }

  const json: unknown = await res.json();
  return AnswerResponseSchema.parse(json);
}

export type PostPictureAbandonOptions = PostPictureOptions & {
  keepalive?: boolean;
};

/** POST `/api/games/picture/abandon` — timer expiry, navigation guard, or tab close (keepalive). */
export async function postPictureAbandon(
  options: PostPictureAbandonOptions = {},
): Promise<AbandonResponse> {
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
    keepalive: options.keepalive ?? false,
  });

  if (!res.ok) {
    throw new PictureApiError(res.status);
  }

  const json: unknown = await res.json();
  return AbandonResponseSchema.parse(json);
}
