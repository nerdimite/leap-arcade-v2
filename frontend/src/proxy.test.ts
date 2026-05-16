import { NextRequest } from "next/server";
import { describe, expect, it } from "vitest";

import { config, proxy } from "./proxy";

describe("proxy", () => {
  it("redirects unauthenticated /lobby to /login", () => {
    const req = new NextRequest("http://localhost:3000/lobby");
    const res = proxy(req);
    expect(res.status).toBeGreaterThanOrEqual(300);
    expect(res.status).toBeLessThan(400);
    expect(res.headers.get("location")).toBe("http://localhost:3000/login");
  });

  it("allows authenticated requests through", () => {
    const req = new NextRequest("http://localhost:3000/lobby", {
      headers: { cookie: "token=valid.jwt" },
    });
    const res = proxy(req);
    expect(res.status).toBe(200);
  });

  it("allows unauthenticated /login without redirect loop", () => {
    const req = new NextRequest("http://localhost:3000/login");
    const res = proxy(req);
    expect(res.status).toBe(200);
  });

  it("redirects authenticated users from /login to /lobby", () => {
    const req = new NextRequest("http://localhost:3000/login", {
      headers: { cookie: "token=already.jwt" },
    });
    const res = proxy(req);
    expect(res.headers.get("location")).toBe("http://localhost:3000/lobby");
  });

  it("documents static asset paths in matcher so proxy is not applied to them", () => {
    const m = config.matcher[0] as string;
    expect(m).toContain("_next/static");
    expect(m).toContain("_next/image");
    expect(m).not.toContain("login");
  });
});
