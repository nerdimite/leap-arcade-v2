import { type NextRequest, NextResponse } from "next/server";
import { z } from "zod";

import { LoginRequestSchema } from "@/services/auth/schema";

const UpstreamLoginSuccessSchema = z.object({
  access_token: z.string(),
});

function defaultBackendOrigin(): string {
  return process.env.BACKEND_INTERNAL_ORIGIN ?? "http://fastapi:8000";
}

export async function POST(request: NextRequest) {
  let jsonUnknown: unknown;
  try {
    jsonUnknown = await request.json();
  } catch {
    return NextResponse.json({ error: "Invalid JSON body" }, { status: 400 });
  }

  const bodyParse = LoginRequestSchema.safeParse(jsonUnknown);
  if (!bodyParse.success) {
    return NextResponse.json({ error: "Invalid login payload" }, { status: 400 });
  }

  const upstreamUrl = new URL("/auth/login", defaultBackendOrigin().replace(/\/?$/, "/"));
  const upstream = await fetch(upstreamUrl, {
    method: "POST",
    headers: {
      "content-type": "application/json",
      accept: "application/json",
    },
    body: JSON.stringify(bodyParse.data),
  });

  const responseText = await upstream.text();

  if (!upstream.ok) {
    return new NextResponse(responseText, {
      status: upstream.status,
      statusText: upstream.statusText,
      headers: {
        "content-type": upstream.headers.get("content-type") ?? "application/json",
      },
    });
  }

  let upstreamJson: unknown;
  try {
    upstreamJson = JSON.parse(responseText) as unknown;
  } catch {
    return NextResponse.json({ error: "Upstream login response was not JSON" }, { status: 502 });
  }

  const tokenParse = UpstreamLoginSuccessSchema.safeParse(upstreamJson);
  if (!tokenParse.success) {
    return NextResponse.json({ error: "Upstream login missing access_token" }, { status: 502 });
  }

  const ok = NextResponse.json({ ok: true as const });
  ok.cookies.set({
    name: "token",
    value: tokenParse.data.access_token,
    httpOnly: true,
    sameSite: "strict",
    path: "/",
  });
  return ok;
}
