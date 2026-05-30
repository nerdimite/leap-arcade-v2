/**
 * Shared game marquee header: the cabinet plate (`▸ label` kicker + tagline
 * `<h1>` + optional progress line) on the left, derived from the per-game
 * registry so the copy lives once. Each game slots its own right-side cluster
 * (score readout, timer, action) as `children`. The accent colour is inherited
 * from the `--accent` channel the View sets on its root, so the header stays
 * game-agnostic.
 */

import type { ReactNode } from "react";

import type { LobbyGameId } from "@/lib/constants";
import { GAME_VISUALS } from "@/lib/game-tiles";
import { cn } from "@/lib/utils";

export type GameHeaderProps = {
  gameId: LobbyGameId;
  /** Sits under the tagline, e.g. "Question 3 of 10". */
  progress?: ReactNode;
  /** Denser plate for sticky/space-tight headers (Wikipedia Speed Run). */
  compact?: boolean;
  /** Right-side cluster: ScoreReadout, timers, submit, composed per game. */
  children?: ReactNode;
  className?: string;
};

export function GameHeader({ gameId, progress, compact, children, className }: GameHeaderProps) {
  const { label, tagline } = GAME_VISUALS[gameId];

  return (
    <header className={cn("flex flex-wrap items-end justify-between gap-4", className)}>
      <div>
        <p
          className={cn(
            "font-pixel uppercase tracking-[2px] text-[var(--accent)]",
            compact ? "text-[8px]" : "text-[9px]",
          )}
        >
          ▸ {label}
        </p>
        <h1
          className={cn(
            "font-pixel text-ink",
            compact ? "mt-1.5 text-[12px] leading-none" : "mt-2.5 text-[13px] leading-[1.5]",
          )}
        >
          {tagline}
        </h1>
        {progress ? (
          <p className="mt-2 text-[13px] text-ink-dim tabular-nums">{progress}</p>
        ) : null}
      </div>
      {children ? <div className="flex items-center gap-3">{children}</div> : null}
    </header>
  );
}
