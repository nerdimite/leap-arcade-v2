"use client";

import { useLeaderboard } from "@/services/leaderboard/hooks";

import { LeaderboardTable } from "./LeaderboardTable";

export default function LeaderboardClient() {
  const { data } = useLeaderboard();
  const entries = data?.entries ?? [];

  return (
    <div className="mx-auto max-w-4xl px-4 py-8">
      <h1 className="mb-2 text-2xl font-semibold tracking-tight">Leaderboard</h1>
      <p className="text-muted-foreground mb-6 text-sm">Live standings — updates every few seconds.</p>
      <LeaderboardTable entries={entries} />
    </div>
  );
}
