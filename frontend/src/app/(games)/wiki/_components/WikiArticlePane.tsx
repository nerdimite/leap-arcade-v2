/** Wikipedia HTML pane with delegated in-article navigation clicks. */

import { Loader2 } from "lucide-react";
import { memo, useEffect, useRef } from "react";

import { cn } from "@/lib/utils";

import "./wiki-article.css";

export type WikiArticlePaneProps = {
  currentTitle: string;
  articleHtml: string;
  navPending: boolean;
  onNavigate: (title: string) => Promise<void>;
};

export const WikiArticlePane = memo(function WikiArticlePane(props: WikiArticlePaneProps) {
  const { currentTitle, articleHtml, navPending, onNavigate } = props;
  const articleRef = useRef<HTMLElement | null>(null);

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

  return (
    <div className="relative z-0 mt-4 min-h-0 flex-1">
      {navPending ? (
        <div
          className="absolute inset-0 z-10 flex items-center justify-center bg-background/30 backdrop-blur-[1px]"
          role="status"
          aria-live="polite"
        >
          <span className="sr-only">Loading article</span>
          <Loader2 className="h-9 w-9 animate-spin text-primary" aria-hidden />
        </div>
      ) : null}
      <article
        ref={articleRef}
        className={cn(
          "leap-wiki-skin overflow-x-auto border border-border/70 bg-card/80 px-4 py-5 shadow-sm sm:px-6 lg:px-8 lg:py-7",
          navPending && "pointer-events-none",
        )}
      >
        <header className="mb-5 border-b border-black/8 pb-3">
          <p className="m-0 text-[0.72rem] font-medium uppercase tracking-[0.18em] text-[color:var(--wiki-muted)]">
            Current article
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
  );
});
