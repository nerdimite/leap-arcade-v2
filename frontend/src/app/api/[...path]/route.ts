import type { NextRequest } from "next/server"
import { forwardApiToBackend } from "@/lib/server/api-catch-all-proxy"
import {
  handleAuthLogin,
  handleAuthLogout,
  isAuthLoginPath,
  isAuthLogoutPath,
} from "@/lib/server/auth-login-handler"

type RouteParams = Promise<{ path: string[] }>

async function handle(request: NextRequest, params: RouteParams) {
  const { path: segments } = await params

  if (request.method === "POST" && isAuthLoginPath(segments)) {
    return handleAuthLogin(request)
  }

  if (request.method === "POST" && isAuthLogoutPath(segments)) {
    return handleAuthLogout()
  }

  return forwardApiToBackend(request, segments)
}

export async function GET(
  request: NextRequest,
  context: { params: RouteParams }
) {
  return handle(request, context.params)
}

export async function POST(
  request: NextRequest,
  context: { params: RouteParams }
) {
  return handle(request, context.params)
}

export async function PUT(
  request: NextRequest,
  context: { params: RouteParams }
) {
  return handle(request, context.params)
}

export async function PATCH(
  request: NextRequest,
  context: { params: RouteParams }
) {
  return handle(request, context.params)
}

export async function DELETE(
  request: NextRequest,
  context: { params: RouteParams }
) {
  return handle(request, context.params)
}
