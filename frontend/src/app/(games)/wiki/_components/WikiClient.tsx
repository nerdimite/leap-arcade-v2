"use client";

import { Loader2 } from "lucide-react";
import { memo, useCallback, useEffect, useRef, useState } from "react";

import { Button } from "@/components/ui/button";
import { useNavigationGuard } from "@/hooks/use-navigation-guard";
import { postWikiAbandon, postWikiBack, postWikiNavigate, postWikiPlay, postWikiTimeout } from "@/lib/api/wiki";
import { cn } from "@/lib/utils";

import "./wiki-article.css";

import type { WikiPlayResponse, WikiPuzzleResult } from "@/services/wiki/schema";

import { useWikiReducer } from "../_hooks/useWikiReducer";

function formatMs(ms: number): string {
  const s = Math.max(0, Math.floor(ms / 1000));
  const m = Math.floor(s / 60);
  const r = s % 60;
  return `${m}:${r.toString().padStart(2, "0")}`;
}

function WikiProgressBar(props: {
  puzzleIndex: number;
  puzzleCount: number;
  completedCount: number;
}) {
  const { puzzleIndex, puzzleCount, completedCount } = props;
  return (
    <div
      className="flex gap-1"
      role="progressbar"
      aria-valuemin={0}
      aria-valuemax={puzzleCount}
      aria-valuenow={completedCount}
      aria-label={`${completedCount} of ${puzzleCount} puzzles completed`}
    >
      {Array.from({ length: puzzleCount }, (_, i) => {
        const idx = i + 1;
        const done = idx <= completedCount;
        const current = idx === puzzleIndex;
        return (
          <div
            key={idx}
            className={cn(
              "h-2 min-w-[1.5rem] flex-1 rounded-full transition-colors",
              done && "bg-primary",
              !done && current && "bg-primary/35 ring-2 ring-primary ring-offset-2 ring-offset-background",
              !done && !current && "bg-muted",
            )}
          />
        );
      })}
    </div>
  );
}

function WikiClickBreadcrumb(props: { pathRoot: string; clickPath: string[] }) {
  const { pathRoot, clickPath } = props;
  const chain = [pathRoot, ...clickPath];
  const crumbs = chain.filter((c, i) => i === 0 || c !== chain[i - 1]);
  if (crumbs.length === 0) {
    return null;
  }
  return (
    <div className="min-w-0 text-xs text-muted-foreground" data-testid="wiki-breadcrumb">
      <span className="font-medium text-foreground">Path</span>
      <span className="mx-1.5">·</span>
      <div className="max-w-full overflow-x-auto overscroll-x-contain [-ms-overflow-style:none] [scrollbar-width:thin] [&::-webkit-scrollbar]:h-1">
        <span className="inline-flex w-max min-w-0 flex-nowrap items-baseline gap-x-1 whitespace-nowrap">
          {crumbs.map((c, i) => (
            <span key={crumbs.slice(0, i + 1).join("\u2192")} className="inline-flex items-baseline gap-x-1">
              {i > 0 ? <span className="text-muted-foreground">→</span> : null}
              <span className="max-w-[14rem] truncate font-medium text-foreground sm:max-w-[18rem]" title={c}>
                {c}
              </span>
            </span>
          ))}
        </span>
      </div>
    </div>
  );
}

function WikiFinalResults(props: {
  totalScore: number;
  results: WikiPuzzleResult[];
  title?: string;
  subtitle?: string;
}) {
  const { totalScore, results, title, subtitle } = props;
  const ordered = [...results].sort((a, b) => a.puzzle_index - b.puzzle_index);
  return (
    <div className="mx-auto max-w-3xl space-y-6 p-6">
      <header className="space-y-1">
        <h1 className="text-xl font-semibold">{title ?? "Wikipedia Speed Run"}</h1>
        <p className="text-muted-foreground">{subtitle ?? "All puzzles complete."}</p>
        <p className="text-2xl font-bold tabular-nums">
          Total score <span className="text-primary">{totalScore}</span>
        </p>
      </header>
      <ul className="grid gap-3 sm:grid-cols-2">
        {ordered.map((r) => (
          <li
            key={r.round_id}
            className="rounded-lg border bg-card p-4 shadow-sm"
          >
            <p className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
              Puzzle {r.puzzle_index}
            </p>
            <p className="mt-1 font-medium leading-snug">{r.clue}</p>
            <p className="mt-2 text-sm text-muted-foreground">Target</p>
            <p className="text-lg font-semibold leading-snug">{r.target_title}</p>
            <dl className="mt-3 grid grid-cols-2 gap-2 text-sm">
              <dt className="text-muted-foreground">Score</dt>
              <dd className="font-mono tabular-nums text-right">{r.score}</dd>
              <dt className="text-muted-foreground">Clicks</dt>
              <dd className="font-mono tabular-nums text-right">{r.steps_taken}</dd>
              <dt className="text-muted-foreground">Time (ms)</dt>
              <dd className="font-mono tabular-nums text-right">{r.time_ms ?? "—"}</dd>
            </dl>
          </li>
        ))}
      </ul>
    </div>
  );
}

const WikiArticlePane = memo(function WikiArticlePane(props: {
  currentTitle: string;
  articleHtml: string;
  navPending: boolean;
  onNavigate: (title: string) => Promise<void>;
}) {
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

export function WikiClient({ initialPlay }: { initialPlay: WikiPlayResponse }) {
  const [state, dispatch] = useWikiReducer(initialPlay);
  const { setIsDirty, registerBeforeNavigateConfirm } = useNavigationGuard();
  const tickRef = useRef<number | null>(null);
  const [navPending, setNavPending] = useState(false);
  const [continuePending, setContinuePending] = useState(false);
  const attemptIdRef = useRef<string | null>(null);
  const [pathRoot, setPathRoot] = useState("");
  const serverTimeoutSyncRef = useRef(false);

  useEffect(() => {
    if (state.phase !== "active" || state.timerRemainingMs == null) {
      serverTimeoutSyncRef.current = false;
      return;
    }
    if (state.timerRemainingMs > 0) {
      serverTimeoutSyncRef.current = false;
      return;
    }
    if (serverTimeoutSyncRef.current) {
      return;
    }
    serverTimeoutSyncRef.current = true;
    void postWikiTimeout()
      .then((res) => {
        dispatch({ type: "PLAY_OK", payload: res });
      })
      .catch(() => {
        dispatch({
          type: "PLAY_ERROR",
          payload: { message: "Could not sync timer — please try again." },
        });
      });
  }, [state.phase, state.timerRemainingMs, dispatch]);

  useEffect(() => {
    return registerBeforeNavigateConfirm(async () => {
      await postWikiAbandon();
    });
  }, [registerBeforeNavigateConfirm]);

  useEffect(() => {
    const dirty = state.phase === "active" || state.phase === "puzzleResult";
    setIsDirty(dirty);
  }, [state.phase, setIsDirty]);

  useEffect(() => {
    if (state.phase !== "active") {
      if (tickRef.current != null) {
        window.clearInterval(tickRef.current);
        tickRef.current = null;
      }
      return undefined;
    }
    tickRef.current = window.setInterval(() => {
      dispatch({ type: "TICK", payload: { nowMs: Date.now() } });
    }, 250);
    return () => {
      if (tickRef.current != null) {
        window.clearInterval(tickRef.current);
        tickRef.current = null;
      }
    };
  }, [state.phase, dispatch]);

  useEffect(() => {
    if (state.play?.state !== "active") {
      return;
    }
    const aid = state.play.current.attempt_id;
    if (attemptIdRef.current !== aid) {
      attemptIdRef.current = aid;
      setPathRoot(state.play.current.current_title);
    }
  }, [state.play]);

  const navigateToTitle = useCallback(async (title: string) => {
    setNavPending(true);
    try {
      const res = await postWikiNavigate(title);
      dispatch({ type: "NAVIGATE_OK", payload: res });
    } catch {
      dispatch({
        type: "NAVIGATE_ERROR",
        payload: { message: "Navigation failed — please try again." },
      });
    } finally {
      setNavPending(false);
    }
  }, [dispatch]);

  const continueViaPlay = useCallback(async () => {
    setContinuePending(true);
    try {
      const res = await postWikiPlay();
      dispatch({ type: "PLAY_OK", payload: res });
    } catch {
      dispatch({
        type: "PLAY_ERROR",
        payload: { message: "Could not continue — please try again." },
      });
    } finally {
      setContinuePending(false);
    }
  }, [dispatch]);

  const wikiBack = useCallback(async () => {
    setNavPending(true);
    try {
      const res = await postWikiBack();
      dispatch({ type: "NAVIGATE_OK", payload: res });
    } catch {
      dispatch({
        type: "NAVIGATE_ERROR",
        payload: { message: "Back navigation failed — please try again." },
      });
    } finally {
      setNavPending(false);
    }
  }, [dispatch]);

  if (state.phase === "terminal" && state.play) {
    const p = state.play;
    if (p.state === "completed") {
      return <WikiFinalResults totalScore={p.total_score} results={p.results} />;
    }
    if (p.state === "abandoned") {
      return (
        <WikiFinalResults
          totalScore={p.total_score}
          results={p.results}
          title="Wikipedia Speed Run"
          subtitle="Session ended. Completed puzzles keep their scores; others count as zero."
        />
      );
    }
  }

  if (state.phase === "error") {
    return (
      <div className="mx-auto max-w-2xl p-6">
        <p className="text-destructive">{state.errorMessage ?? "Something went wrong"}</p>
      </div>
    );
  }

  if (state.phase === "puzzleResult" && state.puzzleResult != null) {
    const r = state.puzzleResult;
    const total = state.totalScoreAfterPuzzle ?? r.score;
    const hasNext = state.nextPuzzleAvailable === true;
    return (
      <div className="mx-auto flex max-w-lg flex-col gap-4 p-6">
        <h1 className="text-lg font-semibold">Puzzle complete</h1>
        <div className="rounded-lg border bg-card p-4 shadow-sm">
          <p className="text-sm text-muted-foreground">Target revealed</p>
          <p className="text-lg font-medium">{r.target_title}</p>
          <dl className="mt-3 grid grid-cols-2 gap-2 text-sm">
            <dt className="text-muted-foreground">Clicks</dt>
            <dd className="font-mono tabular-nums">{r.steps_taken}</dd>
            <dt className="text-muted-foreground">Score</dt>
            <dd className="font-mono tabular-nums">{r.score}</dd>
            <dt className="text-muted-foreground">Time (ms)</dt>
            <dd className="font-mono tabular-nums">{r.time_ms ?? "—"}</dd>
            <dt className="text-muted-foreground">Total so far</dt>
            <dd className="font-mono tabular-nums">{total}</dd>
          </dl>
        </div>
        <Button
          type="button"
          className="w-full sm:w-auto"
          disabled={continuePending}
          onClick={() => void continueViaPlay()}
        >
          {continuePending ? "Loading…" : hasNext ? "Continue to next puzzle" : "View final results"}
        </Button>
      </div>
    );
  }

  if (state.play?.state !== "active") {
    return null;
  }

  const { current, completed_count, total_score } = state.play;
  const displayMs = state.timerRemainingMs ?? current.time_remaining_ms;

  return (
    <div className="mx-auto flex min-h-svh w-full max-w-[min(100%,1680px)] flex-col gap-0 px-3 pb-8 pt-4 sm:px-5 lg:px-7">
      <header className="sticky top-0 z-30 space-y-2 border-b border-border/80 bg-background/95 pb-3 backdrop-blur supports-[backdrop-filter]:bg-background/88">
        <div className="flex flex-wrap items-center justify-between gap-2">
          <div className="flex min-w-0 flex-wrap items-center gap-2">
            {current.back_enabled ? (
              <Button
                type="button"
                variant="outline"
                size="sm"
                disabled={navPending}
                onClick={() => void wikiBack()}
              >
                Back
              </Button>
            ) : null}
            <h1 className="text-lg font-semibold">Wikipedia Speed Run</h1>
          </div>
          <span className="text-sm font-medium text-muted-foreground">
            Puzzle {current.puzzle_index} of {current.puzzle_count}
          </span>
        </div>
        <WikiProgressBar
          puzzleCount={current.puzzle_count}
          puzzleIndex={current.puzzle_index}
          completedCount={completed_count}
        />
        <p className="text-sm font-medium leading-snug">{current.clue}</p>
        <WikiClickBreadcrumb pathRoot={pathRoot} clickPath={current.click_path} />
        <div className="flex flex-wrap gap-4 text-sm">
          <span className="rounded-md border px-2 py-1 font-mono tabular-nums">
            ⏱ {formatMs(displayMs)}
          </span>
          <span className="text-muted-foreground">
            Clicks: {current.steps_taken} · Completed rounds: {completed_count} · Score:{" "}
            {total_score}
          </span>
        </div>
      </header>
      <WikiArticlePane
        currentTitle={current.current_title}
        articleHtml={current.article_html}
        navPending={navPending}
        onNavigate={navigateToTitle}
      />
    </div>
  );
}
