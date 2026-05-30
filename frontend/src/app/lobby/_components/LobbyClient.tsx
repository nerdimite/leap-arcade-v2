"use client"

import { GAME_TILES } from "@/lib/game-tiles"
import { usePlayerSessions } from "@/services/players/hooks"
import type { PlayerSession } from "@/services/players/schema"
import type { GameTileProps } from "./GameTile"
import LobbyLeaderboardSidebar from "./LobbyLeaderboardSidebar"
import { LobbyView } from "./LobbyView"

function sessionsByGameId(
  rows: PlayerSession[] | undefined
): Map<string, PlayerSession> {
  const map = new Map<string, PlayerSession>()
  for (const row of rows ?? []) {
    map.set(row.game_id, row)
  }
  return map
}

function statusLabel(session: PlayerSession | undefined): string {
  if (!session) {
    return "Not started"
  }
  if (session.status === "active") {
    return "In progress"
  }
  if (session.status === "completed") {
    return "Completed"
  }
  return "Abandoned"
}

export default function LobbyClient({
  currentCorpId,
}: {
  currentCorpId: string | null
}) {
  const { data } = usePlayerSessions()
  const byGame = sessionsByGameId(data)

  const tiles: GameTileProps[] = GAME_TILES.map((game) => {
    const session = byGame.get(game.id)
    /** Once a game ends it stays ended — no re-entry or results re-view (may revisit later). */
    const locked =
      session?.status === "completed" || session?.status === "abandoned"
    const badge = statusLabel(session)

    return {
      gameId: game.id,
      name: game.name,
      description: game.description,
      maxPoints: game.maxPoints,
      badge,
      score: session?.score,
      href: game.href,
      locked,
    }
  })

  return (
    <LobbyView
      tiles={tiles}
      sidebar={<LobbyLeaderboardSidebar currentCorpId={currentCorpId} />}
    />
  )
}
