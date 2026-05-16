import {
  dehydrate,
  HydrationBoundary,
  QueryClient,
} from "@tanstack/react-query";
import { cookies, headers } from "next/headers";
import { redirect } from "next/navigation";
import { getPlayerSessions, PLAYER_SESSIONS_QUERY_KEY } from "@/lib/api/players";
import { PLAYER_SESSIONS_STALE_TIME_MS } from "@/lib/constants";
import { decodeJwtSub } from "@/lib/server/jwt-sub";
import { getLeaderboardQueryOptions } from "@/services/leaderboard/query-options";
import LobbyClient from "./_components/LobbyClient";

export default async function LobbyPage() {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
    },
  });

  const cookie = (await headers()).get("cookie") ?? "";

  try {
    await Promise.all([
      queryClient.prefetchQuery({
        queryKey: PLAYER_SESSIONS_QUERY_KEY,
        queryFn: () => getPlayerSessions({ headers: { cookie } }),
        staleTime: PLAYER_SESSIONS_STALE_TIME_MS,
      }),
      queryClient.prefetchQuery(getLeaderboardQueryOptions({ headers: { cookie } })),
    ]);
  } catch {
    redirect("/login");
  }

  const token = (await cookies()).get("token")?.value ?? "";
  const currentCorpId = token ? decodeJwtSub(token) : null;

  return (
    <HydrationBoundary state={dehydrate(queryClient)}>
      <LobbyClient currentCorpId={currentCorpId} />
    </HydrationBoundary>
  );
}
