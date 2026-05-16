import {
  dehydrate,
  HydrationBoundary,
  QueryClient,
} from "@tanstack/react-query";
import { headers } from "next/headers";
import { redirect } from "next/navigation";
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

  return (
    <HydrationBoundary state={dehydrate(queryClient)}>
      <LeaderboardClient />
    </HydrationBoundary>
  );
}
