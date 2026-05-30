import {
  dehydrate,
  HydrationBoundary,
  QueryClient,
} from "@tanstack/react-query"
import { cookies, headers } from "next/headers"

import { postWikiPlay } from "@/lib/api/wiki"
import { wikiQueryKeys } from "@/services/wiki/keys"

import { WikiClient } from "./_components/WikiClient"

async function serverOrigin(): Promise<string> {
  const h = await headers()
  const host = h.get("x-forwarded-host") ?? h.get("host") ?? "localhost:3000"
  const proto = h.get("x-forwarded-proto") ?? "http"
  return `${proto}://${host}`
}

export default async function WikiSpeedRunPage() {
  const origin = await serverOrigin()
  const cookieStore = await cookies()
  const cookieHeader = cookieStore
    .getAll()
    .map((c) => `${c.name}=${c.value}`)
    .join("; ")

  const play = await postWikiPlay({ baseUrl: origin, cookieHeader })

  const queryClient = new QueryClient()
  queryClient.setQueryData(wikiQueryKeys.play(), play)

  return (
    <HydrationBoundary state={dehydrate(queryClient)}>
      <WikiClient initialPlay={play} />
    </HydrationBoundary>
  )
}
