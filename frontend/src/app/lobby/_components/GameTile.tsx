/** Lobby game tile — a lit arcade cabinet. Link when playable, locked shell when done. */

import { Check, Lock, X } from "lucide-react"
import Link from "next/link"
import type { CSSProperties } from "react"

import type { LobbyGameId } from "@/lib/constants"
import { GAME_VISUALS } from "@/lib/game-tiles"

export type GameTileProps = {
  gameId: LobbyGameId
  name: string
  description: string
  maxPoints: number
  badge: string
  score?: number | null
  href?: string
  locked: boolean
}

/** Status pill content + style, derived from the lifecycle the lobby already computes. */
function pill(badge: string, locked: boolean, score?: number | null) {
  if (locked) {
    const ended = badge === "Abandoned"
    return {
      kind: "done" as const,
      ended,
      score: score ?? 0,
    }
  }
  if (badge === "In progress") return { kind: "play" as const, label: "Resume" }
  return { kind: "play" as const, label: "Play" }
}

export function GameTile({
  gameId,
  name,
  description,
  badge,
  score,
  href,
  locked,
}: GameTileProps) {
  const { accent, sprite } = GAME_VISUALS[gameId]
  const status = pill(badge, locked, score)

  const body = (
    <>
      {/* Lit marquee strip — the one sanctioned glow; desaturated when locked. */}
      <div
        className="h-2 bg-[var(--accent)]"
        style={
          locked
            ? { filter: "saturate(0.45)" }
            : { boxShadow: "0 0 18px var(--accent)" }
        }
      />

      <div className="flex gap-4 p-[18px]">
        <div
          className="grid size-[58px] flex-none place-items-center rounded-[var(--radius)] border-2 border-[var(--accent)] bg-bg text-[30px] [image-rendering:pixelated]"
          style={{ boxShadow: "inset 0 0 12px oklch(0 0 0 / 0.6)" }}
          aria-hidden
        >
          {sprite}
        </div>
        <div className="min-w-0">
          <h3 className="font-pixel text-[11px] leading-[1.5] text-ink">
            {name}
          </h3>
          <p className="mt-2.5 text-[13px] leading-[1.55] text-ink-dim">
            {description}
          </p>
        </div>
      </div>

      <div className="mt-0.5 flex items-center justify-end px-[18px] pb-[18px]">
        {status.kind === "play" ? (
          <span className="rounded-full bg-[var(--accent)] px-3 py-1.5 text-[11px] font-bold tracking-[0.5px] text-bg uppercase shadow-[var(--shadow-cabinet-sm)]">
            {status.label}
          </span>
        ) : (
          <span className="inline-flex items-center gap-1 rounded-full border-[1.5px] border-line px-3 py-1.5 text-[11px] font-bold tracking-[0.5px] text-ink-faint uppercase">
            {status.ended ? (
              <>
                <X aria-hidden className="size-3" />
                Ended
              </>
            ) : (
              <>
                <Check aria-hidden className="size-3" />
                {status.score}
              </>
            )}
          </span>
        )}
      </div>

      {locked ? (
        <Lock
          className="absolute top-3.5 right-3.5 size-3.5 text-ink-faint"
          aria-hidden
        />
      ) : null}
    </>
  )

  const base =
    "group relative block overflow-hidden rounded-[var(--radius)] border-2 border-line bg-panel " +
    "shadow-[var(--shadow-cabinet)] outline-none focus-visible:ring-2 focus-visible:ring-[var(--accent)] " +
    "focus-visible:ring-offset-2 focus-visible:ring-offset-bg"
  const style = { "--accent": accent } as CSSProperties

  if (locked) {
    return (
      <div
        className={`${base} cursor-not-allowed opacity-[0.72]`}
        style={style}
        role="img"
        aria-label={`${name}, ${badge}${score != null ? `, score ${score}` : ""}. Locked.`}
      >
        {body}
      </div>
    )
  }

  return (
    <Link
      href={href ?? "#"}
      style={style}
      aria-label={`${name} — ${status.label}`}
      className={
        `${base} transition-[transform,box-shadow] duration-150 ease-[var(--ease-arcade)] ` +
        "hover:-translate-x-[3px] hover:-translate-y-[3px] hover:shadow-[var(--shadow-cabinet-lift)] " +
        "active:translate-x-[2px] active:translate-y-[2px] active:shadow-[var(--shadow-cabinet-sm)] " +
        "motion-reduce:transition-none motion-reduce:hover:translate-x-0 motion-reduce:hover:translate-y-0"
      }
    >
      {body}
    </Link>
  )
}
