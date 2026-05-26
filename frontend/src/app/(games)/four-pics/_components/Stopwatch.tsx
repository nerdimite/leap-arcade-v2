"use client";

import { useEffect, useState } from "react";

import {
  elapsedMsFromStartedAt,
  formatMmSsFromElapsedMs,
  stopwatchToneClass,
} from "@/app/(games)/four-pics/_lib/stopwatch";
import { FOUR_PICS_TIME_DECAY_MS } from "@/lib/constants";
import { cn } from "@/lib/utils";

export type StopwatchProps = {
  startedAt: string;
};

export function Stopwatch({ startedAt }: StopwatchProps) {
  const [elapsedMs, setElapsedMs] = useState(() => elapsedMsFromStartedAt(startedAt));

  useEffect(() => {
    const tick = () => setElapsedMs(elapsedMsFromStartedAt(startedAt));
    tick();
    const id = window.setInterval(tick, 100);
    return () => window.clearInterval(id);
  }, [startedAt]);

  const pastDecay = elapsedMs >= FOUR_PICS_TIME_DECAY_MS;

  return (
    <div className="flex flex-col items-end gap-0.5">
      <span
        className={cn("font-mono text-lg tabular-nums tracking-tight", stopwatchToneClass(elapsedMs))}
        aria-live="polite"
        aria-label={`Elapsed time ${formatMmSsFromElapsedMs(elapsedMs)}`}
      >
        {formatMmSsFromElapsedMs(elapsedMs)}
      </span>
      {pastDecay ? (
        <span className="text-muted-foreground text-xs">No time bonus</span>
      ) : null}
    </div>
  );
}
