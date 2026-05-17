/** Row shape matches `LeaderboardEntry` from the API; kept local so this leaf has no `services/*` imports. */
export type LeaderboardTableRow = {
  rank: number;
  corp_id: string;
  display_name: string;
  total_score: number;
  games_completed: number;
};

export function LeaderboardTable(props: { entries: LeaderboardTableRow[] }) {
  const { entries } = props;

  if (entries.length === 0) {
    return (
      <div className="overflow-hidden rounded-xl border shadow-sm">
        <p className="text-muted-foreground px-4 py-12 text-center text-sm">
          No scores yet — be the first.
        </p>
      </div>
    );
  }

  return (
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
  );
}
