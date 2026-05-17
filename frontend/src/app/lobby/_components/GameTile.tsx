/** Lobby game card — link when playable or disabled shell when locked. */

import { Lock } from "lucide-react";
import Link from "next/link";

export type GameTileProps = {
  name: string;
  description: string;
  maxPoints: number;
  badge: string;
  score?: number | null;
  href?: string;
  locked: boolean;
};

export function GameTile({
  name,
  description,
  maxPoints,
  badge,
  score,
  href,
  locked,
}: GameTileProps) {
  const body = (
    <>
      <div className="flex items-start justify-between gap-2">
        <h2 className="text-lg font-medium">{name}</h2>
        {locked ? <Lock className="size-4 shrink-0 opacity-70" aria-hidden /> : null}
      </div>
      <p className="text-muted-foreground mt-1 text-sm leading-relaxed">{description}</p>
      <div className="mt-4 flex flex-wrap items-center gap-2 text-sm">
        <span className="bg-secondary/50 rounded-full border px-2 py-0.5 text-xs font-medium">
          {badge}
        </span>
        <span className="text-muted-foreground">Up to {maxPoints} pts</span>
        {score != null ? <span className="font-medium">Score: {score}</span> : null}
      </div>
    </>
  );

  const cardBase =
    "rounded-xl border p-4 transition focus-visible:ring-2 focus-visible:ring-ring focus-visible:outline-none";

  if (locked) {
    return (
      <div
        className={`${cardBase} bg-muted/30 cursor-not-allowed opacity-75`}
        aria-disabled="true"
      >
        {body}
      </div>
    );
  }

  return (
    <Link
      href={href ?? "#"}
      className={`${cardBase} bg-card block cursor-pointer shadow-sm hover:border-primary/40 hover:shadow`}
    >
      {body}
    </Link>
  );
}
