"use client";

import { Lock } from "lucide-react";
import Link from "next/link";
import { GAME_TILES } from "@/lib/game-tiles";
import { usePlayerSessions } from "@/services/players/hooks";
import type { PlayerSession } from "@/services/players/schema";
import LobbyLeaderboardSidebar from "./LobbyLeaderboardSidebar";

function sessionsByGameId(rows: PlayerSession[] | undefined): Map<string, PlayerSession> {
  const map = new Map<string, PlayerSession>();
  for (const row of rows ?? []) {
    map.set(row.game_id, row);
  }
  return map;
}

function statusLabel(session: PlayerSession | undefined): string {
  if (!session) {
    return "Not started";
  }
  if (session.status === "active") {
    return "In progress";
  }
  if (session.status === "completed") {
    return "Completed";
  }
  return "Abandoned";
}

export default function LobbyClient({ currentCorpId }: { currentCorpId: string | null }) {
  const { data } = usePlayerSessions();
  const byGame = sessionsByGameId(data);

  return (
    <div className="mx-auto flex max-w-6xl flex-col gap-8 px-4 py-8 lg:flex-row lg:items-start">
      <div className="min-w-0 flex-1">
        <h1 className="mb-2 text-2xl font-semibold tracking-tight">Lobby</h1>
        <p className="text-muted-foreground mb-8 text-sm">Choose a game to play.</p>
        <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
          {GAME_TILES.map((game) => {
            const session = byGame.get(game.id);
            const locked =
              session?.status === "completed" || session?.status === "abandoned";
            const badge = statusLabel(session);

            const body = (
              <>
                <div className="flex items-start justify-between gap-2">
                  <h2 className="text-lg font-medium">{game.name}</h2>
                  {locked ? <Lock className="size-4 shrink-0 opacity-70" aria-hidden /> : null}
                </div>
                <p className="text-muted-foreground mt-1 text-sm leading-relaxed">{game.description}</p>
                <div className="mt-4 flex flex-wrap items-center gap-2 text-sm">
                  <span className="bg-secondary/50 rounded-full border px-2 py-0.5 text-xs font-medium">
                    {badge}
                  </span>
                  <span className="text-muted-foreground">Up to {game.maxPoints} pts</span>
                  {session?.score != null ? (
                    <span className="font-medium">Score: {session.score}</span>
                  ) : null}
                </div>
              </>
            );

            const cardBase =
              "rounded-xl border p-4 transition focus-visible:ring-2 focus-visible:ring-ring focus-visible:outline-none";

            if (locked) {
              return (
                <div
                  key={game.id}
                  className={`${cardBase} bg-muted/30 cursor-not-allowed opacity-75`}
                  aria-disabled="true"
                >
                  {body}
                </div>
              );
            }

            return (
              <Link
                key={game.id}
                href={game.href}
                className={`${cardBase} bg-card block cursor-pointer shadow-sm hover:border-primary/40 hover:shadow`}
              >
                {body}
              </Link>
            );
          })}
        </div>
      </div>
      <aside className="lg:w-80 lg:shrink-0">
        <LobbyLeaderboardSidebar currentCorpId={currentCorpId} />
      </aside>
    </div>
  );
}
