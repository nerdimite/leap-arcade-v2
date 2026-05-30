"use client";

/**
 * Global chrome for the lobby and leaderboard (games stay full-focus with only
 * their own GameHeader). Left: the Glitch & Giggle wordmark, linking home.
 * Right: the one bright action (context-aware Leaderboard / Lobby CTA) and a
 * pixel player token that opens a menu with the player's name, corp ID, and
 * logout. Runs on the default Wiki-cyan accent since no game is in context.
 */

import { ArrowLeft, ArrowRight, ChevronDown, LogOut } from "lucide-react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import type { CSSProperties } from "react";

import { Wordmark } from "@/components/chrome/Wordmark";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { useLogoutMutation } from "@/services/auth/hooks";

// Primary action: the single lit CTA. Solid accent fill, dark ink, cabinet
// press. This is the one thing in the bar we want players reaching for.
const NAV_CTA =
  "inline-flex h-9 items-center gap-1.5 rounded-[var(--radius)] bg-[var(--accent)] " +
  "px-3.5 text-[12px] font-bold uppercase tracking-[0.5px] text-bg shadow-[var(--shadow-cabinet-sm)] " +
  "transition-[transform,box-shadow] duration-150 ease-[var(--ease-arcade)] " +
  "hover:-translate-x-px hover:-translate-y-px hover:shadow-[var(--shadow-cabinet)] " +
  "active:translate-x-[1px] active:translate-y-[1px] active:shadow-none " +
  "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--accent)] " +
  "focus-visible:ring-offset-2 focus-visible:ring-offset-bg " +
  "motion-reduce:transition-none motion-reduce:hover:translate-x-0 motion-reduce:hover:translate-y-0";

// Player token: a framed cabinet chip with a recessed "screen" of initials.
const PLAYER_TOKEN =
  "group inline-flex h-9 items-center gap-1.5 rounded-[var(--radius)] border-2 border-[var(--accent)] " +
  "bg-panel-2 py-0.5 pl-1 pr-2 text-ink shadow-[var(--shadow-cabinet-sm)] " +
  "transition-[transform,box-shadow] duration-150 ease-[var(--ease-arcade)] " +
  "hover:-translate-x-px hover:-translate-y-px hover:shadow-[var(--shadow-cabinet)] " +
  "active:translate-x-[1px] active:translate-y-[1px] active:shadow-none " +
  "aria-expanded:translate-x-[1px] aria-expanded:translate-y-[1px] aria-expanded:shadow-none " +
  "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--accent)] " +
  "focus-visible:ring-offset-2 focus-visible:ring-offset-bg " +
  "motion-reduce:transition-none motion-reduce:hover:translate-x-0 motion-reduce:hover:translate-y-0";

// Recessed "screen" holding the initials. A deep, near-black well plus a
// bright cyan glyph (raised lightness, same wiki hue) so the thin pixel
// strokes clear AA comfortably; the inset is soft so it frames, not crowds.
const TOKEN_SCREEN =
  "grid place-items-center rounded-[2px] bg-[oklch(0.13_0.03_280)] font-pixel leading-none " +
  "text-[oklch(0.9_0.14_220)] shadow-[inset_0_0_5px_oklch(0_0_0/0.45)]";

const BAR_ACCENT = { "--accent": "var(--wiki)" } as CSSProperties;

function initialsFrom(displayName: string | null, corpId: string | null): string {
  const source = displayName?.trim() || corpId?.trim() || "";
  if (!source) return "??";
  const words = source.split(/\s+/).filter(Boolean);
  if (words.length >= 2) {
    return (words[0][0] + words[1][0]).toUpperCase();
  }
  return source.slice(0, 2).toUpperCase();
}

export type AppBarProps = {
  corpId: string | null;
  displayName?: string | null;
};

export function AppBar({ corpId, displayName }: AppBarProps) {
  const router = useRouter();
  const pathname = usePathname();
  const logout = useLogoutMutation();

  const onLeaderboard = pathname?.startsWith("/leaderboard") ?? false;
  const dest = onLeaderboard
    ? { href: "/lobby", label: "Lobby", Icon: ArrowLeft, side: "before" as const }
    : { href: "/leaderboard", label: "Leaderboard", Icon: ArrowRight, side: "after" as const };

  const initials = initialsFrom(displayName ?? null, corpId);
  const primaryName = displayName?.trim() || corpId || "Player";
  const showCorpMeta = Boolean(displayName?.trim()) && Boolean(corpId);

  function handleLogout() {
    if (logout.isPending) return;
    logout.mutate(undefined, {
      onSettled: () => {
        router.replace("/login");
        router.refresh();
      },
    });
  }

  return (
    <header
      style={BAR_ACCENT}
      className="sticky top-0 z-40 border-b-2 border-line bg-panel"
    >
      <div className="mx-auto flex h-14 max-w-[1240px] items-center justify-between gap-4 px-6">
        <Link
          href="/lobby"
          aria-label="Glitch & Giggle — back to lobby"
          className="group rounded-[var(--radius)] outline-none focus-visible:ring-2 focus-visible:ring-[var(--accent)] focus-visible:ring-offset-2 focus-visible:ring-offset-bg"
        >
          <Wordmark size="compact" />
        </Link>

        <div className="flex items-center gap-2.5 sm:gap-3">
          <Link href={dest.href} className={NAV_CTA}>
            {dest.side === "before" ? <dest.Icon aria-hidden className="size-3.5" /> : null}
            {dest.label}
            {dest.side === "after" ? <dest.Icon aria-hidden className="size-3.5" /> : null}
          </Link>

          <DropdownMenu>
            <DropdownMenuTrigger
              aria-label={`${primaryName} — open player menu`}
              className={PLAYER_TOKEN}
            >
              <span className={`${TOKEN_SCREEN} size-7 text-[10px]`}>{initials}</span>
              <ChevronDown
                aria-hidden
                className="size-3.5 text-ink-faint transition-colors duration-150 ease-[var(--ease-arcade)] group-hover:text-ink group-aria-expanded:text-ink"
              />
            </DropdownMenuTrigger>

            <DropdownMenuContent
              align="end"
              sideOffset={8}
              className="min-w-52 rounded-[var(--radius)] border-2 border-line bg-panel p-1.5 shadow-[var(--shadow-cabinet)]"
            >
              <div className="flex items-center gap-2.5 px-2 pt-1 pb-2">
                <span className={`${TOKEN_SCREEN} size-8 text-[11px]`}>{initials}</span>
                <span className="flex min-w-0 flex-col">
                  <span className="truncate text-[13px] font-semibold text-ink">{primaryName}</span>
                  {showCorpMeta ? (
                    <span className="text-[10px] font-bold uppercase tracking-[1px] text-ink-faint">
                      {corpId}
                    </span>
                  ) : (
                    <span className="text-[10px] font-bold uppercase tracking-[1px] text-ink-faint">
                      Player
                    </span>
                  )}
                </span>
              </div>

              <DropdownMenuSeparator className="bg-line" />

              <DropdownMenuItem
                disabled={logout.isPending}
                onSelect={(event) => {
                  event.preventDefault();
                  handleLogout();
                }}
                className="gap-2 rounded-[2px] px-2 py-1.5 text-[12px] font-bold uppercase tracking-[0.5px] text-ink-dim focus:bg-panel-2 focus:text-cross"
              >
                <LogOut aria-hidden className="size-3.5" />
                {logout.isPending ? "Leaving…" : "Logout"}
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </div>
    </header>
  );
}
