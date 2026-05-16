"use client";

import { useLeaderboard } from "@/services/leaderboard/hooks";

export default function LeaderboardClient() {
  const { data } = useLeaderboard();
  const entries = data?.entries ?? [];

  return (
    <div className="mx-auto max-w-4xl px-4 py-8">
      <h1 className="mb-2 text-2xl font-semibold tracking-tight">Leaderboard</h1>
      <p className="text-muted-foreground mb-6 text-sm">Live standings — updates every few seconds.</p>
      <div className="overflow-hidden rounded-xl border shadow-sm">
        <table className="w-full text-sm">
          <thead className="bg-muted/60 border-b text-left text-xs font-medium uppercase tracking-wide">
            <tr>
              <th className="px-4 py-3">Rank</th>
              <th className="px-4 py-3">Name</th>
              <th className="px-4 py-3 text-right">Score</th>
              <th className="px-4 py-3 text-right">Games done</th>
            </tr>
          </thead>
          <tbody>
            {entries.map((row) => (
              <tr key={row.corp_id} className="odd:bg-muted/25 border-b last:border-b-0">
                <td className="text-muted-foreground px-4 py-3 tabular-nums">{row.rank}</td>
                <td className="px-4 py-3 font-medium">{row.display_name}</td>
                <td className="px-4 py-3 text-right tabular-nums">{row.total_score}</td>
                <td className="px-4 py-3 text-right tabular-nums">{row.games_completed}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
