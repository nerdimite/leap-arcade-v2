/** Active wiki puzzle layout: sticky HUD shell + riddle ribbon + browser window. */

import type { CSSProperties } from "react"

import { GAME_VISUALS } from "@/lib/game-tiles"
import { cn, formatMs } from "@/lib/utils"
import type { WikiActivePuzzle } from "@/services/wiki/schema"

import { WikiArticlePane } from "./WikiArticlePane"
import { WikiClickBreadcrumb } from "./WikiClickBreadcrumb"
import { WikiProgressBar } from "./WikiProgressBar"

/** Wikipedia Speed Run runs on the default cyan marquee accent. */
const WIKI_ACCENT = { "--accent": "var(--wiki)" } as CSSProperties

/** Timer turns coral + blinks under this remaining threshold. */
const LOW_TIME_MS = 30_000

type HudTone = "ink" | "time" | "score"

/** One framed cabinet stat block in the HUD cluster. */
function HudStat({
  label,
  value,
  tone = "ink",
  low = false,
}: {
  label: string
  value: string
  tone?: HudTone
  low?: boolean
}) {
  return (
    <div
      className={cn(
        "flex min-w-[5.25rem] flex-col items-center justify-center rounded-[var(--radius)] border-2 border-line bg-panel px-4 py-1.5 shadow-[var(--shadow-cabinet-sm)]",
        tone === "time" && low && "border-cross"
      )}
    >
      <span className="text-[9px] tracking-[1px] text-ink-faint uppercase">
        {label}
      </span>
      <span
        className={cn(
          "mt-2 font-pixel text-[14px] leading-none tabular-nums",
          tone === "ink" && "text-ink",
          tone === "time" && (low ? "text-cross" : "text-rapid"),
          tone === "score" && "text-four",
          tone === "time" && low && "motion-safe:animate-arcade-blink"
        )}
      >
        {value}
      </span>
    </div>
  )
}

export type WikiActiveViewProps = {
  current: WikiActivePuzzle
  pathRoot: string
  timerRemainingMs: number
  completedCount: number
  totalScore: number
  navPending: boolean
  onNavigate: (title: string) => Promise<void>
  /** Caller wraps async work with `void` at the boundary. */
  onBack: () => void
}

export function WikiActiveView(props: WikiActiveViewProps) {
  const {
    current,
    pathRoot,
    timerRemainingMs,
    completedCount,
    totalScore,
    navPending,
    onNavigate,
    onBack,
  } = props
  const displayMs = timerRemainingMs
  const lowTime = displayMs <= LOW_TIME_MS

  return (
    <div
      className="mx-auto flex min-h-svh w-full max-w-[min(100%,1680px)] flex-col px-3 pb-10 sm:px-5 lg:px-7"
      style={WIKI_ACCENT}
    >
      {/* header + puzzle progress travel together as one sticky shell */}
      <div className="sticky top-0 z-30 -mx-3 backdrop-blur supports-[backdrop-filter]:bg-bg/85 sm:-mx-5 lg:-mx-7">
        <header className="flex flex-wrap items-center justify-between gap-x-6 gap-y-3 border-b-2 border-line bg-bg/95 px-3 py-3.5 sm:px-5 lg:px-7">
          <div className="flex items-center gap-3">
            <div
              aria-hidden
              className="grid h-10 w-10 place-items-center rounded-[var(--radius)] border-2 border-[var(--accent)] bg-bg text-[21px] shadow-[inset_0_0_12px_oklch(0_0_0/0.6)]"
            >
              {GAME_VISUALS.wiki.sprite}
            </div>
            <div>
              <p className="font-pixel text-[8px] tracking-[2px] text-[var(--accent)] uppercase">
                ▸ {GAME_VISUALS.wiki.label}
              </p>
              <h1 className="mt-1.5 font-pixel text-[12px] leading-none text-ink">
                {GAME_VISUALS.wiki.tagline}
              </h1>
            </div>
          </div>
          <div className="flex flex-wrap items-stretch gap-2.5">
            <HudStat label="Clicks" value={String(current.steps_taken)} />
            <HudStat
              label="Rounds"
              value={`${completedCount}/${current.puzzle_count}`}
            />
            <HudStat
              label="Time left"
              value={formatMs(displayMs)}
              tone="time"
              low={lowTime}
            />
            <HudStat label="Score" value={String(totalScore)} tone="score" />
          </div>
        </header>
        <div className="flex items-center gap-4 border-b-2 border-line bg-bg/85 px-3 py-3 sm:px-5 lg:px-7">
          <div className="flex-1">
            <WikiProgressBar
              puzzleCount={current.puzzle_count}
              puzzleIndex={current.puzzle_index}
              completedCount={completedCount}
            />
          </div>
          <span className="font-pixel text-[11px] whitespace-nowrap text-ink-dim tabular-nums">
            PUZZLE{" "}
            <span className="text-[var(--accent)]">
              {String(current.puzzle_index).padStart(2, "0")}
            </span>{" "}
            / {String(current.puzzle_count).padStart(2, "0")}
          </span>
        </div>
      </div>

      {/* riddle ribbon: the clue, promoted to its own band */}
      <div className="mt-6 flex items-start gap-5 rounded-[var(--radius)] border-2 border-line bg-panel px-5 py-4 shadow-[var(--shadow-cabinet-sm)]">
        <span className="shrink-0 rounded-[var(--radius)] bg-[var(--accent)] px-2.5 py-2 font-pixel text-[9px] tracking-[1px] text-bg">
          RIDDLE
        </span>
        <p className="max-w-[64ch] text-[16px] leading-snug font-medium text-ink italic">
          {current.clue}
        </p>
      </div>

      {/* path the player has taken so far this puzzle */}
      <div className="mt-4">
        <WikiClickBreadcrumb
          pathRoot={pathRoot}
          clickPath={current.click_path}
        />
      </div>

      <div className="mt-4 min-h-0 flex-1">
        <WikiArticlePane
          currentTitle={current.current_title}
          articleHtml={current.article_html}
          navPending={navPending}
          backEnabled={current.back_enabled}
          onBack={onBack}
          onNavigate={onNavigate}
        />
      </div>
    </div>
  )
}
