/** Compact leaderboard table + optional pinned row for current player. */

/** Structural match for API leaderboard rows; avoids importing service modules in the leaf. */
export type MiniLeaderboardRow = {
  corp_id: string;
  rank: number;
  display_name: string;
  total_score: number;
  games_completed: number;
};

export type MiniLeaderboardProps = {
  entries: MiniLeaderboardRow[];
  currentCorpId: string | null;
  pinnedEntry?: MiniLeaderboardRow;
};

function normalizeCorpId(s: string): string {
  return s.toLowerCase();
}

function MiniRow({
  row,
  highlight,
}: {
  row: MiniLeaderboardRow;
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

export function MiniLeaderboard({ entries, currentCorpId, pinnedEntry }: MiniLeaderboardProps) {
  const normalizedCurrent =
    currentCorpId != null ? normalizeCorpId(currentCorpId) : null;

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
            {entries.map((row) => (
              <MiniRow
                key={row.corp_id}
                row={row}
                highlight={
                  normalizedCurrent != null &&
                  normalizeCorpId(row.corp_id) === normalizedCurrent
                }
              />
            ))}
          </tbody>
        </table>
      </div>

      {pinnedEntry ? (
        <>
          <div className="text-muted-foreground my-3 flex items-center gap-2 text-[10px] font-medium uppercase tracking-wide">
            <span className="bg-border h-px flex-1" />
            Your rank
            <span className="bg-border h-px flex-1" />
          </div>
          <div className="overflow-hidden rounded-lg border">
            <table className="w-full text-xs">
              <tbody>
                <MiniRow row={pinnedEntry} highlight />
              </tbody>
            </table>
          </div>
        </>
      ) : null}
    </section>
  );
}
