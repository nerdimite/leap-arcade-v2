"use client"

import { useLeaderboard } from "@/services/leaderboard/hooks"

import { MiniLeaderboard } from "./MiniLeaderboard"

function normalizeCorp(s: string): string {
  return s.toLowerCase()
}

export default function LobbyLeaderboardSidebar({
  currentCorpId,
}: {
  currentCorpId: string | null
}) {
  const { data } = useLeaderboard()
  const entries = data?.entries ?? []
  const top10 = entries.slice(0, 10)

  const selfRow =
    currentCorpId != null
      ? entries.find(
          (e) => normalizeCorp(e.corp_id) === normalizeCorp(currentCorpId)
        )
      : undefined
  const selfInTop10 =
    currentCorpId != null &&
    top10.some((e) => normalizeCorp(e.corp_id) === normalizeCorp(currentCorpId))
  const showPinned = Boolean(selfRow && currentCorpId && !selfInTop10)

  return (
    <MiniLeaderboard
      entries={top10}
      currentCorpId={currentCorpId}
      pinnedEntry={showPinned ? selfRow : undefined}
      fullBoardHref="/leaderboard"
    />
  )
}
