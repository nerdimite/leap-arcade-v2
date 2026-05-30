import { type NextRequest, NextResponse } from "next/server"

const HOP_BY_HOP_REQUEST_HEADERS = new Set([
  "connection",
  "keep-alive",
  "proxy-authenticate",
  "proxy-authorization",
  "te",
  "trailers",
  "transfer-encoding",
  "upgrade",
  "host",
  "content-length",
  "cookie",
])

const HOP_BY_HOP_RESPONSE_HEADERS = new Set([
  "connection",
  "keep-alive",
  "transfer-encoding",
  "trailer",
])

export type ForwardApiOptions = {
  backendOrigin?: string
}

function defaultBackendOrigin(): string {
  return process.env.BACKEND_INTERNAL_ORIGIN ?? "http://localhost:8000"
}

function buildUpstreamUrl(backendOrigin: string, pathSegments: string[]): URL {
  const path = pathSegments.map(encodeURIComponent).join("/")
  return new URL(
    `/${path}`,
    backendOrigin.endsWith("/") ? backendOrigin : `${backendOrigin}/`
  )
}

function buildUpstreamHeaders(
  request: NextRequest,
  bearerToken: string | undefined
): Headers {
  const headers = new Headers()
  request.headers.forEach((value, key) => {
    const lower = key.toLowerCase()
    if (HOP_BY_HOP_REQUEST_HEADERS.has(lower)) {
      return
    }
    headers.append(key, value)
  })
  if (bearerToken) {
    headers.set("Authorization", `Bearer ${bearerToken}`)
  }
  return headers
}

function filterResponseHeaders(upstream: Headers): Headers {
  const out = new Headers()
  upstream.forEach((value, key) => {
    if (HOP_BY_HOP_RESPONSE_HEADERS.has(key.toLowerCase())) {
      return
    }
    out.append(key, value)
  })
  return out
}

export async function forwardApiToBackend(
  request: NextRequest,
  pathSegments: string[],
  options: ForwardApiOptions = {}
): Promise<Response> {
  const backendOrigin = options.backendOrigin ?? defaultBackendOrigin()
  const token = request.cookies.get("token")?.value

  if (!token) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 })
  }

  const upstreamUrl = buildUpstreamUrl(backendOrigin, pathSegments)
  const bearer = token
  const headers = buildUpstreamHeaders(request, bearer)

  const hasBody = !["GET", "HEAD"].includes(request.method)
  const body = hasBody ? await request.arrayBuffer() : undefined

  const upstreamResponse = await fetch(upstreamUrl, {
    method: request.method,
    headers,
    body: body && body.byteLength > 0 ? body : undefined,
  })

  return new NextResponse(upstreamResponse.body, {
    status: upstreamResponse.status,
    statusText: upstreamResponse.statusText,
    headers: filterResponseHeaders(upstreamResponse.headers),
  })
}
