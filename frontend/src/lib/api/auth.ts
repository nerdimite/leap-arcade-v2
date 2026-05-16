import type { z } from "zod";

import type { LoginOkResponse } from "@/services/auth/schema";
import { LoginOkResponseSchema, LoginRequestSchema } from "@/services/auth/schema";

export type LoginPayload = z.input<typeof LoginRequestSchema>;

export class LoginApiError extends Error {
  readonly status: number;

  constructor(status: number, message = "Login failed") {
    super(message);
    this.name = "LoginApiError";
    this.status = status;
  }
}

function loginRequestUrl(): string {
  if (typeof window !== "undefined" && window.location?.origin) {
    return new URL("/api/auth/login", window.location.origin).href;
  }
  return "http://localhost:3000/api/auth/login";
}

/** POST `/api/auth/login`; sets httpOnly cookie without exposing the JWT body. */
export async function postLogin(input: LoginPayload): Promise<LoginOkResponse> {
  const body = LoginRequestSchema.parse(input);

  const res = await fetch(loginRequestUrl(), {
    method: "POST",
    headers: {
      "content-type": "application/json",
      accept: "application/json",
    },
    body: JSON.stringify(body),
  });

  if (!res.ok) {
    throw new LoginApiError(res.status);
  }

  const json: unknown = await res.json();
  return LoginOkResponseSchema.parse(json);
}
