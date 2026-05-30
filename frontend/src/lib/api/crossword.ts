import type { z } from "zod";

import {
  type CheckRequest,
  CheckRequestSchema,
  type CheckResponse,
  CheckResponseSchema,
  type PlayResponse,
  PlayResponseSchema,
  type SubmitResponse,
  SubmitResponseSchema,
} from "@/services/crossword/schema";

export class CrosswordApiError extends Error {
  readonly status: number;

  constructor(status: number, message = "Crossword request failed") {
    super(message);
    this.name = "CrosswordApiError";
    this.status = status;
  }
}

export type PostCrosswordOptions = {
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
  return new URL("/api/games/crossword/play", origin).href;
}

function checkHref(origin: string): string {
  return new URL("/api/games/crossword/check", origin).href;
}

function submitHref(origin: string): string {
  return new URL("/api/games/crossword/submit", origin).href;
}

function buildHeaders(cookieHeader?: string): Record<string, string> {
  const headers: Record<string, string> = {
    accept: "application/json",
  };
  if (cookieHeader) {
    headers.cookie = cookieHeader;
  }
  return headers;
}

export async function postPlay(options: PostCrosswordOptions = {}): Promise<PlayResponse> {
  const origin = resolveOrigin(options.baseUrl);
  const res = await fetch(playHref(origin), {
    method: "POST",
    headers: buildHeaders(options.cookieHeader),
    credentials: options.cookieHeader ? "omit" : "include",
  });

  if (!res.ok) {
    throw new CrosswordApiError(res.status);
  }

  const json: unknown = await res.json();
  return PlayResponseSchema.parse(json);
}

export type PostCheckBody = z.input<typeof CheckRequestSchema>;

export async function postCheck(
  input: PostCheckBody,
  options: PostCrosswordOptions = {},
): Promise<CheckResponse> {
  const origin = resolveOrigin(options.baseUrl);
  const body = CheckRequestSchema.parse(input);

  const headers = buildHeaders(options.cookieHeader);
  headers["content-type"] = "application/json";

  const res = await fetch(checkHref(origin), {
    method: "POST",
    headers,
    credentials: options.cookieHeader ? "omit" : "include",
    body: JSON.stringify(body),
  });

  if (!res.ok) {
    throw new CrosswordApiError(res.status);
  }

  const json: unknown = await res.json();
  return CheckResponseSchema.parse(json);
}

export async function postSubmit(options: PostCrosswordOptions = {}): Promise<SubmitResponse> {
  const origin = resolveOrigin(options.baseUrl);
  const res = await fetch(submitHref(origin), {
    method: "POST",
    headers: buildHeaders(options.cookieHeader),
    credentials: options.cookieHeader ? "omit" : "include",
  });

  if (!res.ok) {
    throw new CrosswordApiError(res.status);
  }

  const json: unknown = await res.json();
  return SubmitResponseSchema.parse(json);
}
