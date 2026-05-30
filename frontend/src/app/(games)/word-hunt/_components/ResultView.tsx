import { Button } from "@/components/ui/button";
import { formatMs } from "@/lib/utils";
import type { Result } from "@/services/word_hunt/schema";

export type ResultViewProps = {
  result: Result;
  onBackToLobby: () => void;
};

function scoreBreakdown(result: Result): string | null {
  if (result.base_score === undefined || result.time_bonus === undefined) {
    return null;
  }
  return `${result.base_score} (= ${result.found_count} × 100) + ${result.time_bonus} = ${result.score}`;
}

export function ResultView({ result, onBackToLobby }: ResultViewProps) {
  const breakdown = scoreBreakdown(result);

  return (
    <div className="mx-auto flex max-w-lg flex-col gap-6 p-6 pb-10">
      <div className="overflow-hidden rounded-[var(--radius)] border-2 border-line bg-panel shadow-[var(--shadow-cabinet)]">
        <div
          className="h-2 bg-[var(--accent,var(--word))]"
          style={{ boxShadow: "0 0 18px var(--accent, var(--word))" }}
        />
        <div className="p-6">
          <p className="font-pixel text-[9px] uppercase tracking-[2px] text-[var(--accent,var(--word))]">
            ▸ Session complete
          </p>
          <p className="mt-4 font-pixel text-[26px] leading-none tabular-nums text-four">
            {result.score}
          </p>
          <p className="mt-2 text-[11px] font-bold uppercase tracking-[1px] text-ink-faint">
            Total score
          </p>
          {breakdown !== null ? (
            <p className="mt-3 text-[13px] tabular-nums text-ink-dim">{breakdown}</p>
          ) : null}
          <ul className="mt-4 flex flex-wrap gap-3 text-[14px] text-ink-dim">
            <li>
              <span className="font-pixel text-[11px] tabular-nums text-ink">
                {result.found_count} / {result.total_words}
              </span>{" "}
              words found
            </li>
            {result.time_elapsed_ms !== undefined ? (
              <li>
                Time{" "}
                <span className="font-pixel text-[11px] tabular-nums text-ink">
                  {formatMs(result.time_elapsed_ms)}
                </span>
              </li>
            ) : null}
          </ul>
        </div>
      </div>

      {result.found_words.length > 0 ? (
        <section className="space-y-3">
          <h2 className="text-[10px] font-bold uppercase tracking-[1px] text-ink-faint">
            Words found
          </h2>
          <ul className="overflow-hidden rounded-[var(--radius)] border-2 border-line">
            {result.found_words.map((found) => (
              <li
                key={found.word_id}
                className="flex flex-col gap-0.5 border-t-[1.5px] border-line bg-bg-2 px-4 py-3 first:border-t-0"
              >
                <span className="font-semibold uppercase tracking-[0.5px] text-ink">
                  {found.word}
                </span>
                <span className="text-[13px] text-ink-dim">{found.clue}</span>
              </li>
            ))}
          </ul>
        </section>
      ) : null}

      <Button type="button" size="lg" className="w-full" onClick={onBackToLobby}>
        Back to Lobby
      </Button>
    </div>
  );
}
