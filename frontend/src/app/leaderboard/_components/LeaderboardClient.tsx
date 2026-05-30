"use client"

import { useLeaderboard } from "@/services/leaderboard/hooks"

import { LeaderboardTable } from "./LeaderboardTable"

export default function LeaderboardClient({
  currentCorpId,
}: {
  currentCorpId?: string | null
}) {
  const { data } = useLeaderboard()
  const entries = data?.entries ?? []

  return (
    <div className="mx-auto max-w-3xl px-6 py-10">
      <p className="font-pixel text-[9px] tracking-[2px] text-rapid uppercase">
        ▸ Final standings
      </p>
      <h1 className="mt-3.5 font-pixel text-[15px] leading-[1.5] text-ink">
        HIGH SCORES
      </h1>
      <p className="mt-3.5 flex items-center gap-2 text-[14px] text-ink-dim">
        <span
          aria-hidden
          className="size-2 animate-arcade-blink rounded-full bg-four motion-reduce:animate-none"
        />
        Live standings, refreshed every few seconds.
      </p>

      <div className="mt-6">
        <LeaderboardTable entries={entries} currentCorpId={currentCorpId} />
      </div>
    </div>
  )
}
