/**
 * Shared game shell: the cabinet frame every `<Game>View` renders into. It owns
 * the three things that were copy-pasted across all seven views:
 *   1. the local `--accent` channel (derived from `gameId` via `GAME_VISUALS`),
 *   2. the centred page container (`size` → max-width + padding), and
 *   3. the state switch — it renders `slots[state]` for the current view status.
 *
 * States that own their own layout (result screens, error panels) go in
 * `bleedStates`: the shell still sets the accent but skips the container so the
 * slot controls its own width. Grid games pass `className` (e.g. `lg:flex-row`).
 */

import type { CSSProperties, ReactNode } from "react";

import type { LobbyGameId } from "@/lib/constants";
import { GAME_VISUALS } from "@/lib/game-tiles";
import { cn } from "@/lib/utils";

export type GameShellSize = "sm" | "md" | "lg" | "xl" | "wide" | "ultrawide";

/** Container max-widths, named to the per-game sizes the views already used. */
const SIZE_MAX_WIDTH: Record<GameShellSize, string> = {
  sm: "max-w-md",
  md: "max-w-lg",
  lg: "max-w-xl",
  xl: "max-w-2xl",
  wide: "max-w-5xl",
  ultrawide: "max-w-6xl",
};

export type GameShellProps = {
  /** Drives the local `--accent` channel via `GAME_VISUALS`. */
  gameId: LobbyGameId;
  /** Current `viewState.status`; selects which slot renders. */
  state: string;
  /** View content keyed by status. A missing slot renders nothing. */
  slots: Partial<Record<string, ReactNode>>;
  /** Container width for the framed (non-bleed) states. Defaults to `md`. */
  size?: GameShellSize;
  /** Padding utility for the framed container. Defaults to `p-6`. */
  padding?: string;
  /** States that own their own width/padding; the shell sets accent only. */
  bleedStates?: readonly string[];
  /** Extra classes on the container (e.g. `lg:flex-row` for grid games). */
  className?: string;
};

export function GameShell({
  gameId,
  state,
  slots,
  size = "md",
  padding = "p-6",
  bleedStates,
  className,
}: GameShellProps) {
  const accentStyle = { "--accent": GAME_VISUALS[gameId].accent } as CSSProperties;
  const content = slots[state] ?? null;
  const bleed = bleedStates?.includes(state) ?? false;

  if (bleed) {
    return (
      <div style={accentStyle} className={className}>
        {content}
      </div>
    );
  }

  return (
    <div
      style={accentStyle}
      className={cn("mx-auto", SIZE_MAX_WIDTH[size], padding, className)}
    >
      {content}
    </div>
  );
}
