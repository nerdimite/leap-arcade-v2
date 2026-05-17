/** Lobby layout shell — tile grid and sidebar slot. */

import type { ReactNode } from "react";

import { GameTile, type GameTileProps } from "./GameTile";

export type LobbyViewProps = {
  tiles: GameTileProps[];
  sidebar: ReactNode;
};

export function LobbyView({ tiles, sidebar }: LobbyViewProps) {
  return (
    <div className="mx-auto flex max-w-6xl flex-col gap-8 px-4 py-8 lg:flex-row lg:items-start">
      <div className="min-w-0 flex-1">
        <h1 className="mb-2 text-2xl font-semibold tracking-tight">Lobby</h1>
        <p className="text-muted-foreground mb-8 text-sm">Choose a game to play.</p>
        <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
          {tiles.map((tile) => (
            <GameTile key={tile.name} {...tile} />
          ))}
        </div>
      </div>
      <aside className="lg:w-80 lg:shrink-0">{sidebar}</aside>
    </div>
  );
}
