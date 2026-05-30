/** Recoverable error surface for Rapid Fire. */

import { ArrowLeft } from "lucide-react";

import { Button } from "@/components/ui/button";

export function RapidFireErrorState(props: { message?: string; onBackToLobby: () => void }) {
  return (
    <div className="rounded-[var(--radius)] border-2 border-line bg-panel p-6 shadow-[var(--shadow-cabinet)]">
      <p className="font-pixel text-[9px] uppercase tracking-[2px] text-cross">▸ Game over</p>
      <h1 className="mt-3 font-pixel text-[13px] leading-[1.5] text-ink">RAPID FIRE</h1>
      <p className="mt-3 text-[15px] text-ink-dim">{props.message ?? "Something went wrong."}</p>
      <Button type="button" variant="outline" className="mt-5" onClick={props.onBackToLobby}>
        <ArrowLeft aria-hidden className="size-4" />
        Back to Lobby
      </Button>
    </div>
  );
}
