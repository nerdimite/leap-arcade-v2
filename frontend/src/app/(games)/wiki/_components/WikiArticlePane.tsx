/** Diegetic browser window: window chrome + address bar over the light article. */

import { ArrowLeft, Loader2, Lock } from "lucide-react";
import { memo, useEffect, useRef } from "react";

import { cn } from "@/lib/utils";

import "./wiki-article.css";

export type WikiArticlePaneProps = {
  currentTitle: string;
  articleHtml: string;
  navPending: boolean;
  backEnabled: boolean;
  onBack: () => void;
  onNavigate: (title: string) => Promise<void>;
};

/** Wikipedia article path as it would appear in the address bar. */
function toWikiUrl(title: string): string {
  return `en.wikipedia.org/wiki/${title.trim().replace(/\s+/g, "_")}`;
}

export const WikiArticlePane = memo(function WikiArticlePane(props: WikiArticlePaneProps) {
  const { currentTitle, articleHtml, navPending, backEnabled, onBack, onNavigate } = props;
  const articleRef = useRef<HTMLElement | null>(null);
  const viewportRef = useRef<HTMLDivElement | null>(null);

  // Each navigation lands at the top of the new article, like a real browser.
  useEffect(() => {
    viewportRef.current?.scrollTo({ top: 0, left: 0 });
  }, [currentTitle, articleHtml]);

  useEffect(() => {
    const root = articleRef.current;
    if (!root) {
      return undefined;
    }
    const onClick = (e: MouseEvent) => {
      const el = (e.target as HTMLElement | null)?.closest?.("a");
      if (!el || !(el instanceof HTMLAnchorElement)) {
        return;
      }
      const href = el.getAttribute("href")?.trim() ?? "";
      const title = el.getAttribute("data-wiki-title");
      const isSamePageHash = href.startsWith("#") && href.length > 1;
      if (!title) {
        if (!isSamePageHash) {
          e.preventDefault();
          e.stopPropagation();
        }
        return;
      }
      e.preventDefault();
      e.stopPropagation();
      if (navPending) {
        return;
      }
      void onNavigate(title);
    };
    root.addEventListener("click", onClick, true);
    return () => root.removeEventListener("click", onClick, true);
  }, [onNavigate, navPending]);

  const backDisabled = !backEnabled || navPending;

  return (
    <section className="overflow-hidden rounded-[var(--radius)] border-2 border-[var(--accent)] bg-white shadow-[0_0_0_1px_oklch(0_0_0/0.4),0_0_40px_oklch(0.78_0.16_220/0.26),var(--shadow-cabinet)]">
      {/* window title bar */}
      <div className="flex items-center gap-2.5 border-b border-[oklch(0.12_0.03_280)] bg-[linear-gradient(to_bottom,oklch(0.30_0.045_284),oklch(0.225_0.04_283))] px-3 py-2">
        <div className="flex min-w-0 flex-1 items-center gap-2 text-[12px] font-semibold text-ink-dim">
          <span aria-hidden className="text-[var(--accent)]">
            🌐
          </span>
          <span className="truncate">
            <span className="text-ink">{currentTitle}</span> — Wikipedia · LEAP Browser
          </span>
        </div>
        <div aria-hidden className="flex gap-1.5 text-[11px] text-ink-dim">
          <span className="grid h-[18px] w-[22px] place-items-center rounded-[2px] border border-line bg-[oklch(0.20_0.04_283)]">
            —
          </span>
          <span className="grid h-[18px] w-[22px] place-items-center rounded-[2px] border border-line bg-[oklch(0.20_0.04_283)]">
            ▢
          </span>
          <span className="grid h-[18px] w-[22px] place-items-center rounded-[2px] border border-line bg-[oklch(0.20_0.04_283)] text-cross">
            ✕
          </span>
        </div>
      </div>

      {/* browser chrome: back (the only control) + address bar */}
      <div className="flex items-center gap-2.5 border-b-2 border-[oklch(0.12_0.03_280)] bg-[linear-gradient(to_bottom,oklch(0.24_0.04_283),oklch(0.205_0.04_283))] px-3 py-2.5">
        <button
          type="button"
          onClick={onBack}
          disabled={backDisabled}
          title="Back (counts as a click)"
          aria-label="Back"
          className={cn(
            "grid h-[26px] w-7 place-items-center rounded-[3px] border border-line bg-[oklch(0.20_0.04_283)] text-ink-dim transition-colors",
            "hover:enabled:border-[var(--accent)] hover:enabled:text-[var(--accent)]",
            "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--accent)]",
            "disabled:cursor-default disabled:opacity-30",
          )}
        >
          <ArrowLeft className="h-[15px] w-[15px]" aria-hidden />
        </button>
        <div className="flex flex-1 items-center gap-2 rounded-[3px] border border-line bg-white px-2.5 py-1.5 text-[13px] text-[#333]">
          <Lock className="h-3 w-3 text-[#1a9d4b]" aria-hidden />
          <span className="truncate text-[#555]">
            {toWikiUrl(currentTitle).split("/wiki/")[0]}/wiki/
            <span className="text-[#111]">{toWikiUrl(currentTitle).split("/wiki/")[1]}</span>
          </span>
        </div>
      </div>

      {/* lit viewport: the article renders in light mode */}
      <div ref={viewportRef} className="relative max-h-[min(70svh,640px)] overflow-y-auto bg-white">
        {navPending ? (
          <div
            className="absolute inset-0 z-10 flex items-center justify-center bg-white/40 backdrop-blur-[1px]"
            role="status"
            aria-live="polite"
          >
            <span className="sr-only">Loading article</span>
            <Loader2 className="h-9 w-9 animate-spin text-[var(--wiki-link,#3366cc)]" aria-hidden />
          </div>
        ) : null}
        <article
          ref={articleRef}
          className={cn("leap-wiki-skin px-6 py-7 lg:px-11", navPending && "pointer-events-none")}
        >
          <header className="mb-5 border-b border-black/10 pb-3">
            <p className="m-0 text-[0.72rem] font-medium uppercase tracking-[0.18em] text-[color:var(--wiki-muted)]">
              From Wikipedia, the free encyclopedia
            </p>
            <h1 className="m-0 mt-1 text-3xl font-semibold leading-tight text-[color:var(--wiki-ink)]">
              {currentTitle}
            </h1>
          </header>
          <div
            // biome-ignore lint/security/noDangerouslySetInnerHtml: HTML is rewritten server-side for the wiki game
            dangerouslySetInnerHTML={{ __html: articleHtml }}
          />
        </article>
      </div>
    </section>
  );
});
