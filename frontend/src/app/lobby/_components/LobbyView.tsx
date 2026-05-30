/** Lobby layout shell — arcade head, tile grid, and sidebar slot. */

import type { ReactNode } from "react";

import { GameTile, type GameTileProps } from "./GameTile";

export type LobbyViewProps = {
  tiles: GameTileProps[];
  sidebar: ReactNode;
};

export function LobbyView({ tiles, sidebar }: LobbyViewProps) {
  return (
    <div className="mx-auto flex max-w-[1240px] flex-col gap-8 px-6 py-8 lg:flex-row lg:items-start">
      <div className="min-w-0 flex-1">
        <h1 className="font-pixel text-[15px] leading-[1.5] text-ink">PICK A GAME</h1>
        <p className="mt-3.5 max-w-[60ch] text-[15px] leading-relaxed text-ink-dim">
          Play all seven in any order. Finish each before you move on.
        </p>

        <div className="mt-6 grid gap-[22px] sm:grid-cols-2">
          {tiles.map((tile) => (
            <GameTile key={tile.gameId} {...tile} />
          ))}
        </div>
      </div>

      <aside className="lg:sticky lg:top-8 lg:w-[320px] lg:shrink-0">{sidebar}</aside>
    </div>
  );
}
