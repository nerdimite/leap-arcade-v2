/** Inline feedback banner shown over the question card during the feedback phase. */

export function FeedbackOverlay(props: { lastCorrect: boolean | null; currentScore: number }) {
  return (
    <div
      className="pointer-events-none absolute inset-0 z-10 flex items-end justify-center rounded-xl bg-background/40 pb-6"
      aria-live="polite"
    >
      <div className="rounded-md border border-border bg-card px-3 py-2 text-center font-medium text-sm shadow-sm">
        <p>{props.lastCorrect ? "Correct!" : "Wrong"}</p>
        <p className="mt-1 text-muted-foreground text-xs tabular-nums">Score: {props.currentScore}</p>
      </div>
    </div>
  );
}
