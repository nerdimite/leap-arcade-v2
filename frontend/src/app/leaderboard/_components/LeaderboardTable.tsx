/** Full tournament standings — a framed arcade high-scores board. */

/** Row shape matches `LeaderboardEntry` from the API; kept local so this leaf has no `services/*` imports. */
export type LeaderboardTableRow = {
  rank: number
  corp_id: string
  display_name: string
  total_score: number
  games_completed: number
}

export type LeaderboardTableProps = {
  entries: LeaderboardTableRow[]
  currentCorpId?: string | null
}

function normalize(s: string): string {
  return s.toLowerCase()
}

export function LeaderboardTable({
  entries,
  currentCorpId,
}: LeaderboardTableProps) {
  const current = currentCorpId != null ? normalize(currentCorpId) : null

  return (
    <section className="overflow-hidden rounded-[var(--radius)] border-2 border-line bg-panel shadow-[var(--shadow-cabinet)]">
      <div className="flex items-center justify-between bg-pin px-5 py-3 text-bg">
        <h2 className="font-pixel text-[11px] leading-none">HIGH SCORES</h2>
        <span className="flex items-center gap-1.5 font-pixel text-[9px] leading-none">
          <span
            aria-hidden
            className="size-2 animate-arcade-blink rounded-full bg-bg motion-reduce:animate-none"
          />
          LIVE
        </span>
      </div>

      {entries.length === 0 ? (
        <p className="px-5 py-14 text-center text-[14px] text-ink-dim">
          No scores yet. Be the first on the board.
        </p>
      ) : (
        <table className="w-full border-collapse">
          <thead>
            <tr className="bg-bg-2 text-left text-[10px] font-bold tracking-[1px] text-ink-faint uppercase">
              <th className="w-16 px-5 py-2.5 font-bold">Rank</th>
              <th className="px-5 py-2.5 font-bold">Player</th>
              <th className="px-5 py-2.5 text-right font-bold">Score</th>
              <th className="w-20 px-5 py-2.5 text-right font-bold">Done</th>
            </tr>
          </thead>
          <tbody>
            {entries.map((row) => {
              const top1 = row.rank === 1
              const you = current != null && normalize(row.corp_id) === current
              return (
                <tr
                  key={row.corp_id}
                  className={`border-t-[1.5px] border-line ${you ? "bg-panel-2" : ""}`}
                >
                  <td
                    className={`px-5 py-3.5 font-pixel text-[12px] ${top1 ? "text-rapid" : "text-ink-faint"}`}
                  >
                    {row.rank}
                  </td>
                  <td className="px-5 py-3.5">
                    <span
                      className={`block text-[15px] font-semibold ${you ? "text-wiki" : "text-ink"}`}
                    >
                      {row.display_name}
                    </span>
                    <span className="block text-[12px] text-ink-faint">
                      {you ? "you" : row.corp_id}
                    </span>
                  </td>
                  <td
                    className={`px-5 py-3.5 text-right font-pixel text-[12px] tabular-nums ${top1 ? "text-rapid" : "text-four"}`}
                  >
                    {row.total_score.toLocaleString()}
                  </td>
                  <td className="px-5 py-3.5 text-right text-[14px] text-ink-dim tabular-nums">
                    {row.games_completed}
                  </td>
                </tr>
              )
            })}
          </tbody>
        </table>
      )}
    </section>
  )
}
