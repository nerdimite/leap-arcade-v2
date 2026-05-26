/** End-of-run summary — per-question rows by number only (no images). */

import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import type { Result, ResultQuestion } from "@/services/four_pics/schema";

export type ResultViewProps = {
  result: Result;
  onBackToLobby: () => void;
};

function statusBadge(status: ResultQuestion["status"]): { label: string; className: string } {
  switch (status) {
    case "correct":
      return {
        label: "Correct",
        className: "border-emerald-600/25 bg-emerald-600/10 text-emerald-900 dark:text-emerald-100",
      };
    case "wrong":
      return {
        label: "Wrong",
        className: "border-destructive/30 bg-destructive/10 text-destructive",
      };
    case "not_reached":
      return {
        label: "Not reached",
        className: "border-muted-foreground/25 bg-muted text-muted-foreground",
      };
  }
}

export function ResultView({ result, onBackToLobby }: ResultViewProps) {
  const rows = [...result.questions].map((q, index) => ({ ...q, questionNumber: index + 1 }));

  return (
    <div className="mx-auto flex max-w-lg flex-col gap-6 p-6 pb-10">
      <header className="space-y-1">
        <h1 className="font-semibold text-xl tracking-tight">Four Pics, One Lie</h1>
        <p className="text-muted-foreground text-sm">Session complete.</p>
      </header>

      <section className="rounded-2xl border bg-card p-6 shadow-sm">
        <p className="text-muted-foreground text-xs font-medium uppercase tracking-wide">Total score</p>
        <p className="mt-1 font-bold text-5xl tabular-nums tracking-tight text-primary">{result.score}</p>
        <ul className="mt-4 flex flex-wrap gap-3 text-sm text-muted-foreground">
          <li>
            <span className="font-medium text-foreground tabular-nums">{result.questions_correct}</span>{" "}
            correct
          </li>
          <li>
            <span className="font-medium text-foreground tabular-nums">{result.questions_wrong}</span> wrong
          </li>
          <li>
            <span className="font-medium text-foreground tabular-nums">
              {result.questions_not_reached}
            </span>{" "}
            not reached
          </li>
        </ul>
      </section>

      <section className="space-y-3">
        <h2 className="text-sm font-semibold tracking-tight">Per question</h2>
        <div className="overflow-hidden rounded-xl border">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b bg-muted/50 text-left text-muted-foreground text-xs">
                <th className="px-3 py-2 font-medium">#</th>
                <th className="px-3 py-2 font-medium">Status</th>
                <th className="px-3 py-2 text-right font-medium">Score</th>
                <th className="px-3 py-2 text-right font-medium">Bonus</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((row) => {
                const badge = statusBadge(row.status);
                return (
                  <tr key={row.question_id} className="border-b last:border-b-0">
                    <td className="px-3 py-2.5 font-mono tabular-nums">{row.questionNumber}</td>
                    <td className="px-3 py-2.5">
                      <span
                        className={cn(
                          "inline-flex rounded-full border px-2 py-0.5 text-xs font-medium",
                          badge.className,
                        )}
                      >
                        {badge.label}
                      </span>
                    </td>
                    <td className="px-3 py-2.5 text-right font-mono tabular-nums">{row.score}</td>
                    <td className="px-3 py-2.5 text-right font-mono tabular-nums">{row.time_bonus}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </section>

      <Button type="button" size="lg" className="w-full" onClick={onBackToLobby}>
        Back to Lobby
      </Button>
    </div>
  );
}
