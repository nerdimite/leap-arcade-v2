import {
  dehydrate,
  HydrationBoundary,
  QueryClient,
} from "@tanstack/react-query";
import { cookies, headers } from "next/headers";
import { redirect } from "next/navigation";
import { decodeJwtSub } from "@/lib/server/jwt-sub";
import { getLeaderboardQueryOptions } from "@/services/leaderboard/query-options";
import LeaderboardClient from "./_components/LeaderboardClient";

export default async function LeaderboardPage() {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
    },
  });

  const cookie = (await headers()).get("cookie") ?? "";

  try {
    await queryClient.prefetchQuery(getLeaderboardQueryOptions({ headers: { cookie } }));
  } catch {
    redirect("/login");
  }

  const token = (await cookies()).get("token")?.value ?? "";
  const currentCorpId = token ? decodeJwtSub(token) : null;

  return (
    <HydrationBoundary state={dehydrate(queryClient)}>
      <LeaderboardClient currentCorpId={currentCorpId} />
    </HydrationBoundary>
  );
}
