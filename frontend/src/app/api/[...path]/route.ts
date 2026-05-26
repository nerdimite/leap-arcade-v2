import type { NextRequest } from "next/server";

import { handleAuthLogin, isAuthLoginPath } from "@/lib/server/auth-login-handler";
import { forwardApiToBackend } from "@/lib/server/api-catch-all-proxy";

type RouteParams = Promise<{ path: string[] }>;

async function handle(request: NextRequest, params: RouteParams) {
  const { path: segments } = await params;

  if (request.method === "POST" && isAuthLoginPath(segments)) {
    return handleAuthLogin(request);
  }

  return forwardApiToBackend(request, segments);
}

export async function GET(request: NextRequest, context: { params: RouteParams }) {
  return handle(request, context.params);
}

export async function POST(request: NextRequest, context: { params: RouteParams }) {
  return handle(request, context.params);
}

export async function PUT(request: NextRequest, context: { params: RouteParams }) {
  return handle(request, context.params);
}

export async function PATCH(request: NextRequest, context: { params: RouteParams }) {
  return handle(request, context.params);
}

export async function DELETE(request: NextRequest, context: { params: RouteParams }) {
  return handle(request, context.params);
}
