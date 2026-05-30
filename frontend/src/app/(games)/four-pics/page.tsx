import {
  dehydrate,
  HydrationBoundary,
  QueryClient,
} from "@tanstack/react-query"
import { cookies, headers } from "next/headers"

import { FourPicsClient } from "@/app/(games)/four-pics/_components/FourPicsClient"
import { postPlay } from "@/lib/api/four-pics"
import { fourPicsQueryKeys } from "@/services/four_pics/keys"

async function serverOrigin(): Promise<string> {
  const h = await headers()
  const host = h.get("x-forwarded-host") ?? h.get("host") ?? "localhost:3000"
  const proto = h.get("x-forwarded-proto") ?? "http"
  return `${proto}://${host}`
}

export default async function FourPicsOneLiePage() {
  const origin = await serverOrigin()
  const cookieStore = await cookies()
  const cookieHeader = cookieStore
    .getAll()
    .map((c) => `${c.name}=${c.value}`)
    .join("; ")

  const play = await postPlay({ baseUrl: origin, cookieHeader })

  const queryClient = new QueryClient()
  queryClient.setQueryData(fourPicsQueryKeys.play(), play)

  return (
    <HydrationBoundary state={dehydrate(queryClient)}>
      <FourPicsClient initialPlay={play} />
    </HydrationBoundary>
  )
}
