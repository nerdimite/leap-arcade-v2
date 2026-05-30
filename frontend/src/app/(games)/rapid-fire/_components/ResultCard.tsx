/** End-of-run score summary for Rapid Fire. */

import { ArrowLeft } from "lucide-react";

import { Button } from "@/components/ui/button";
import type { Result } from "@/services/rapid_fire/schema";

export function ResultCard(props: {
  score: Result["score"];
  correctCount: Result["correct_count"];
  wrongCount: Result["wrong_count"];
  skippedCount: Result["skipped_count"];
  timeTakenSeconds: Result["time_taken_seconds"];
  onBackToLobby: () => void;
}) {
  const stats = [
    { label: "Correct", value: props.correctCount, tone: "text-four" },
    { label: "Wrong", value: props.wrongCount, tone: "text-cross" },
    { label: "Skipped", value: props.skippedCount, tone: "text-ink" },
    { label: "Time", value: `${props.timeTakenSeconds.toFixed(1)}s`, tone: "text-ink" },
  ];

  return (
    <div className="overflow-hidden rounded-[var(--radius)] border-2 border-line bg-panel shadow-[var(--shadow-cabinet)]">
      <div className="h-2 bg-[var(--accent)]" style={{ boxShadow: "0 0 18px var(--accent)" }} />
      <div className="p-6">
        <p className="font-pixel text-[9px] uppercase tracking-[2px] text-[var(--accent)]">
          ▸ Run complete
        </p>
        <p className="mt-4 font-pixel text-[26px] leading-none text-four tabular-nums">
          {props.score}
        </p>
        <p className="mt-2 text-[11px] font-bold uppercase tracking-[1px] text-ink-faint">Points</p>

        <dl className="mt-6 grid grid-cols-2 gap-3">
          {stats.map((s) => (
            <div
              key={s.label}
              className="rounded-[var(--radius)] border-2 border-line bg-bg-2 px-4 py-3"
            >
              <dd className={`font-pixel text-[14px] tabular-nums ${s.tone}`}>{s.value}</dd>
              <dt className="mt-1.5 text-[10px] font-bold uppercase tracking-[1px] text-ink-faint">
                {s.label}
              </dt>
            </div>
          ))}
        </dl>

        <Button type="button" className="mt-6 w-full" onClick={props.onBackToLobby}>
          <ArrowLeft aria-hidden className="size-4" />
          Back to Lobby
        </Button>
      </div>
    </div>
  );
}
