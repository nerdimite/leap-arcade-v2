import { describe, expect, it } from "vitest";

import { LoginRequestSchema } from "./schema";

describe("LoginRequestSchema", () => {
  it("rejects payloads missing corp_id", () => {
    const parsed = LoginRequestSchema.safeParse({ event_code: "ev" });
    expect(parsed.success).toBe(false);
  });

  it("rejects payloads missing event_code", () => {
    const parsed = LoginRequestSchema.safeParse({ corp_id: "corp" });
    expect(parsed.success).toBe(false);
  });

  it("parses valid login payloads", () => {
    const parsed = LoginRequestSchema.safeParse({ corp_id: "a", event_code: "b" });
    expect(parsed.success).toBe(true);
    if (parsed.success) {
      expect(parsed.data).toEqual({ corp_id: "a", event_code: "b" });
    }
  });
});
