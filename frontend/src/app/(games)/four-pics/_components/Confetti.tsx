/** Win-only confetti burst, lime-led for Four Pics. Hidden under reduced motion. */

import { cn } from "@/lib/utils";

/** Deterministic trajectories — stable across renders so React keys stay honest. */
const PIECES = [
  { dx: "-62px", dy: "-36px", rot: "-160deg", color: "var(--four)", delay: "0ms" },
  { dx: "-34px", dy: "-54px", rot: "120deg", color: "var(--word)", delay: "20ms" },
  { dx: "-10px", dy: "-62px", rot: "-90deg", color: "var(--four)", delay: "0ms" },
  { dx: "14px", dy: "-60px", rot: "200deg", color: "var(--rapid)", delay: "40ms" },
  { dx: "38px", dy: "-52px", rot: "-140deg", color: "var(--four)", delay: "10ms" },
  { dx: "62px", dy: "-32px", rot: "90deg", color: "var(--wiki)", delay: "30ms" },
  { dx: "-48px", dy: "-14px", rot: "160deg", color: "var(--four)", delay: "50ms" },
  { dx: "50px", dy: "-12px", rot: "-110deg", color: "var(--rapid)", delay: "60ms" },
];

export function Confetti({ className }: { className?: string }) {
  return (
    <span className={cn("pointer-events-none absolute motion-reduce:hidden", className)} aria-hidden>
      {PIECES.map((p) => (
        <span
          key={`${p.dx}-${p.dy}-${p.rot}`}
          className="absolute block h-1.5 w-1.5 rounded-[1px] motion-safe:animate-rf-confetti"
          style={{
            backgroundColor: p.color,
            animationDelay: p.delay,
            ["--dx" as string]: p.dx,
            ["--dy" as string]: p.dy,
            ["--rot" as string]: p.rot,
          }}
        />
      ))}
    </span>
  );
}
