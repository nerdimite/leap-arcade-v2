"use client";

import { useLeaderboard } from "@/services/leaderboard/hooks";
import type { LeaderboardEntry } from "@/services/leaderboard/schema";

function normalizeCorp(s: string): string {
  return s.toLowerCase();
}

function MiniRow({
  row,
  highlight,
}: {
  row: LeaderboardEntry;
  highlight: boolean;
}) {
  return (
    <tr className={highlight ? "bg-primary/15 font-semibold" : "odd:bg-muted/30"}>
      <td className="text-muted-foreground w-10 px-2 py-1.5 tabular-nums">{row.rank}</td>
      <td className="max-w-[9rem] truncate px-2 py-1.5">{row.display_name}</td>
      <td className="w-14 px-2 py-1.5 text-right tabular-nums">{row.total_score}</td>
      <td className="text-muted-foreground w-10 px-2 py-1.5 text-right tabular-nums">
        {row.games_completed}
      </td>
    </tr>
  );
}

export default function LobbyLeaderboardSidebar({
  currentCorpId,
}: {
  currentCorpId: string | null;
}) {
  const { data } = useLeaderboard();
  const entries = data?.entries ?? [];
  const top10 = entries.slice(0, 10);

  const selfRow =
    currentCorpId != null
      ? entries.find((e) => normalizeCorp(e.corp_id) === normalizeCorp(currentCorpId))
      : undefined;
  const selfInTop10 =
    currentCorpId != null &&
    top10.some((e) => normalizeCorp(e.corp_id) === normalizeCorp(currentCorpId));
  const showPinned = Boolean(selfRow && currentCorpId && !selfInTop10);

  return (
    <section className="bg-card rounded-xl border p-4 shadow-sm" aria-labelledby="mini-lb-heading">
      <h2 id="mini-lb-heading" className="mb-3 text-lg font-semibold tracking-tight">
        Leaderboard
      </h2>
      <div className="overflow-hidden rounded-lg border">
        <table className="w-full text-xs">
          <thead className="bg-muted/50 border-b text-[10px] font-medium uppercase tracking-wide">
            <tr>
              <th className="px-2 py-1.5 text-left">#</th>
              <th className="px-2 py-1.5 text-left">Player</th>
              <th className="px-2 py-1.5 text-right">Pts</th>
              <th className="text-muted-foreground px-2 py-1.5 text-right">Done</th>
            </tr>
          </thead>
          <tbody>
            {top10.map((row) => (
              <MiniRow
                key={row.corp_id}
                row={row}
                highlight={
                  currentCorpId != null &&
                  normalizeCorp(row.corp_id) === normalizeCorp(currentCorpId)
                }
              />
            ))}
          </tbody>
        </table>
      </div>

      {showPinned && selfRow ? (
        <>
          <div className="text-muted-foreground my-3 flex items-center gap-2 text-[10px] font-medium uppercase tracking-wide">
            <span className="bg-border h-px flex-1" />
            Your rank
            <span className="bg-border h-px flex-1" />
          </div>
          <div className="overflow-hidden rounded-lg border">
            <table className="w-full text-xs">
              <tbody>
                <MiniRow row={selfRow} highlight />
              </tbody>
            </table>
          </div>
        </>
      ) : null}
    </section>
  );
}
