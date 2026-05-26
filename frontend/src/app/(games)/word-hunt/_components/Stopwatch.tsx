"use client";

import { useEffect, useState } from "react";

import {
  elapsedMsFromStartedAt,
  formatMmSsFromElapsedMs,
} from "@/app/(games)/word-hunt/_lib/stopwatch";

export type StopwatchProps = {
  startedAt: string;
};

export function Stopwatch({ startedAt }: StopwatchProps) {
  const [elapsedMs, setElapsedMs] = useState(() => elapsedMsFromStartedAt(startedAt));

  useEffect(() => {
    const tick = () => setElapsedMs(elapsedMsFromStartedAt(startedAt));
    tick();
    const id = window.setInterval(tick, 1000);
    return () => window.clearInterval(id);
  }, [startedAt]);

  return (
    <span
      className="font-mono text-lg tabular-nums tracking-tight text-muted-foreground"
      aria-live="polite"
      aria-label={`Elapsed time ${formatMmSsFromElapsedMs(elapsedMs)}`}
    >
      {formatMmSsFromElapsedMs(elapsedMs)}
    </span>
  );
}
