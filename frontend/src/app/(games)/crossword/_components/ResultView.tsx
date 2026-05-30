import { Button } from "@/components/ui/button";
import { formatMs } from "@/lib/utils";
import type { Result } from "@/services/crossword/schema";

export type ResultViewProps = {
  result: Result;
  onBackToLobby: () => void;
};

function formatDirection(direction: string): string {
  return direction.charAt(0).toUpperCase() + direction.slice(1).toLowerCase();
}

function entryHeading(number: number, direction: string, answer: string): string {
  return `${number} ${formatDirection(direction)} — ${answer}`;
}

function scoreBreakdown(result: Result): string | null {
  if (result.base_score === undefined || result.time_bonus === undefined) {
    return null;
  }
  return `${result.base_score} (= ${result.solved_count} × 100) + ${result.time_bonus} = ${result.score}`;
}

export function ResultView({ result, onBackToLobby }: ResultViewProps) {
  const breakdown = scoreBreakdown(result);

  return (
    <div className="mx-auto flex max-w-lg flex-col gap-6 p-6 pb-10">
      <header className="space-y-1">
        <h1 className="text-xl font-semibold tracking-tight">Crossword</h1>
        <p className="text-sm text-muted-foreground">Session complete.</p>
      </header>

      <section className="rounded-2xl border bg-card p-6 shadow-sm">
        <p className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
          Total score
        </p>
        <p className="mt-1 text-5xl font-bold tabular-nums tracking-tight text-primary">
          {result.score}
        </p>
        {breakdown !== null ? (
          <p className="mt-2 text-sm text-muted-foreground tabular-nums">{breakdown}</p>
        ) : null}
        <ul className="mt-4 flex flex-wrap gap-3 text-sm text-muted-foreground">
          <li>
            <span className="font-medium tabular-nums text-foreground">
              {result.solved_count} / {result.total_entries}
            </span>{" "}
            entries solved
          </li>
          {result.time_elapsed_ms !== undefined ? (
            <li>
              Time{" "}
              <span className="font-medium tabular-nums text-foreground">
                {formatMs(result.time_elapsed_ms)}
              </span>
            </li>
          ) : null}
        </ul>
      </section>

      {result.solved_entries.length > 0 ? (
        <section className="space-y-3">
          <h2 className="text-sm font-semibold tracking-tight">Entries solved</h2>
          <ul className="overflow-hidden rounded-xl border">
            {result.solved_entries.map((entry) => (
              <li
                key={entry.entry_id}
                className="flex flex-col gap-0.5 border-b px-4 py-3 last:border-b-0"
              >
                <span className="font-medium">
                  {entryHeading(entry.number, entry.direction, entry.answer)}
                </span>
                <span className="text-sm text-muted-foreground">{entry.clue}</span>
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
