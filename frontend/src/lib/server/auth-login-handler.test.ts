import { NextRequest } from "next/server";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { handleAuthLogin } from "./auth-login-handler";

describe("handleAuthLogin", () => {
  const originalFetch = globalThis.fetch;

  beforeEach(() => {
    vi.restoreAllMocks();
    delete process.env.BACKEND_INTERNAL_ORIGIN;
  });

  afterEach(() => {
    globalThis.fetch = originalFetch;
  });

  it("sets httpOnly strict token cookie and returns only { ok: true } on upstream success", async () => {
    const fetchMock = vi.fn(async () => {
      return new Response(
        JSON.stringify({
          access_token: "jwt.payload.here",
          token_type: "bearer",
          player: {
            id: "p",
            corp_id: "p",
            display_name: "P",
          },
        }),
        { status: 200, headers: { "content-type": "application/json" } },
      );
    });
    globalThis.fetch = fetchMock as unknown as typeof fetch;

    const req = new NextRequest("http://localhost:3000/api/auth/login", {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({ corp_id: "p1", event_code: "ev" }),
    });

    const res = await handleAuthLogin(req);

    expect(res.status).toBe(200);
    expect(fetchMock).toHaveBeenCalledTimes(1);
    const [calledUrl] = fetchMock.mock.calls[0] as unknown as [string | URL, RequestInit?];
    expect(String(calledUrl)).toBe("http://localhost:8000/auth/login");

    const json = await res.json();
    expect(json).toEqual({ ok: true });

    const setCookie = res.headers.get("set-cookie");
    expect(setCookie).toContain("token=jwt.payload.here");
    expect(setCookie?.toLowerCase()).toContain("httponly");
    expect(setCookie).toContain("Path=/");
    expect(setCookie?.toLowerCase()).toContain("samesite=strict");
  });

  it("passes FastAPI failure status and JSON body without token cookie", async () => {
    const fetchMock = vi.fn(async () => {
      return new Response(JSON.stringify({ success: false, message: "Invalid event code" }), {
        status: 401,
        headers: { "content-type": "application/json" },
      });
    });
    globalThis.fetch = fetchMock as unknown as typeof fetch;

    const req = new NextRequest("http://localhost:3000/api/auth/login", {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({ corp_id: "x", event_code: "wrong" }),
    });

    const res = await handleAuthLogin(req);
    expect(res.status).toBe(401);

    expect(res.headers.get("set-cookie")).toBeNull();
    const body = await res.json();
    expect(body).toEqual(expect.objectContaining({ message: expect.any(String) as string }));
  });
});
