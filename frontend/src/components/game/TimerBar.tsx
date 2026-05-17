export function TimerBar(props: { percentage: number }) {
  const pct = Math.min(100, Math.max(0, props.percentage));

  return (
    <div
      className="h-2 overflow-hidden rounded-full bg-muted"
      role="progressbar"
      aria-valuemin={0}
      aria-valuemax={100}
      aria-valuenow={Math.round(pct)}
      aria-label="Time remaining"
    >
      <div
        className="h-full rounded-full bg-primary transition-[width] duration-75 ease-linear"
        style={{ width: `${pct}%` }}
      />
    </div>
  );
}
