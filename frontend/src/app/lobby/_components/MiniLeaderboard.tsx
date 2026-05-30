/** Live high-scores board — framed cabinet panel with a magenta title bar. */

import { ArrowRight } from "lucide-react";
import Link from "next/link";

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
  /** When set, renders a footer link to the full standings page. */
  fullBoardHref?: string;
};

function normalizeCorpId(s: string): string {
  return s.toLowerCase();
}

function Row({
  row,
  highlight,
}: {
  row: MiniLeaderboardRow;
  highlight: boolean;
}) {
  const top1 = row.rank === 1;
  return (
    <div
      className={`grid grid-cols-[28px_1fr_auto] items-center gap-3 border-t-[1.5px] border-line px-4 py-3 ${
        highlight ? "bg-panel-2" : ""
      }`}
    >
      <span className={`font-pixel text-[11px] ${top1 ? "text-rapid" : "text-ink-faint"}`}>
        {row.rank}
      </span>
      <span className="min-w-0">
        <span
          className={`block truncate text-[14px] font-semibold ${highlight ? "text-wiki" : "text-ink"}`}
        >
          {row.display_name}
        </span>
        <span className="block truncate text-[11px] text-ink-faint">
          {highlight ? "you" : row.corp_id}
        </span>
      </span>
      <span className={`font-pixel text-[11px] ${top1 ? "text-rapid" : "text-four"}`}>
        {row.total_score.toLocaleString()}
      </span>
    </div>
  );
}

export function MiniLeaderboard({
  entries,
  currentCorpId,
  pinnedEntry,
  fullBoardHref,
}: MiniLeaderboardProps) {
  const normalizedCurrent = currentCorpId != null ? normalizeCorpId(currentCorpId) : null;
  const isCurrent = (corpId: string) =>
    normalizedCurrent != null && normalizeCorpId(corpId) === normalizedCurrent;

  return (
    <section
      className="overflow-hidden rounded-[var(--radius)] border-2 border-line bg-panel shadow-[var(--shadow-cabinet)]"
      aria-labelledby="mini-lb-heading"
    >
      <div className="flex items-center justify-between bg-pin px-4 py-3 text-bg">
        <h2 id="mini-lb-heading" className="font-pixel text-[10px] leading-none">
          HIGH SCORES
        </h2>
        <span className="flex items-center gap-1.5 font-pixel text-[9px] leading-none">
          <span
            aria-hidden
            className="size-2 rounded-full bg-bg animate-arcade-blink motion-reduce:animate-none"
          />
          LIVE
        </span>
      </div>

      {entries.length === 0 ? (
        <p className="px-4 py-6 text-center text-[13px] text-ink-dim">
          No scores yet. Be the first on the board.
        </p>
      ) : (
        entries.map((row) => (
          <Row key={row.corp_id} row={row} highlight={isCurrent(row.corp_id)} />
        ))
      )}

      {pinnedEntry ? (
        <>
          <div className="flex items-center gap-2 bg-bg-2 px-4 py-2 text-[10px] font-bold uppercase tracking-[1px] text-ink-faint">
            <span className="h-px flex-1 bg-line" />
            Your rank
            <span className="h-px flex-1 bg-line" />
          </div>
          <Row row={pinnedEntry} highlight />
        </>
      ) : null}

      {fullBoardHref ? (
        <Link
          href={fullBoardHref}
          className="group flex items-center justify-center gap-1.5 border-t-[1.5px] border-line px-4 py-3 text-[12px] font-bold uppercase tracking-[0.5px] text-ink-dim outline-none transition-colors duration-150 hover:text-wiki focus-visible:text-wiki"
        >
          View full board
          <ArrowRight
            aria-hidden
            className="size-3.5 transition-transform duration-150 ease-[var(--ease-arcade)] group-hover:translate-x-0.5 motion-reduce:transition-none motion-reduce:group-hover:translate-x-0"
          />
        </Link>
      ) : null}
    </section>
  );
}
