import { dehydrate, HydrationBoundary, QueryClient } from "@tanstack/react-query";
import { cookies, headers } from "next/headers";

import { PinpointClient } from "@/app/(games)/pinpoint/_components/PinpointClient";
import { postPinpointPlay } from "@/lib/api/pinpoint";
import { pinpointQueryKeys } from "@/services/pinpoint/keys";

async function serverOrigin(): Promise<string> {
  const h = await headers();
  const host = h.get("x-forwarded-host") ?? h.get("host") ?? "localhost:3000";
  const proto = h.get("x-forwarded-proto") ?? "http";
  return `${proto}://${host}`;
}

export default async function PinpointPage() {
  const origin = await serverOrigin();
  const cookieStore = await cookies();
  const cookieHeader = cookieStore
    .getAll()
    .map((c) => `${c.name}=${c.value}`)
    .join("; ");

  const play = await postPinpointPlay({ baseUrl: origin, cookieHeader });

  const queryClient = new QueryClient();
  queryClient.setQueryData(pinpointQueryKeys.play(), play);

  return (
    <HydrationBoundary state={dehydrate(queryClient)}>
      <PinpointClient initialPlay={play} />
    </HydrationBoundary>
  );
}
