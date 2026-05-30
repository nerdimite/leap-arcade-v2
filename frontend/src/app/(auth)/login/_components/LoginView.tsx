/**
 * Login — the "insert coin" attract screen. The one cabinet lit in the dark
 * room before the lobby: corp ID + shared event code, then START.
 * Dumb view; all wiring lives in LoginClient.
 */

import { ChevronRight, Loader2, TriangleAlert } from "lucide-react"
import type { FormEvent } from "react"

import { Wordmark } from "@/components/chrome/Wordmark"

export type LoginViewProps = {
  corpId: string
  eventCode: string
  isPending: boolean
  showInvalidCreds: boolean
  onCorpIdChange: (value: string) => void
  onEventCodeChange: (value: string) => void
  onSubmit: (e: FormEvent) => void
}

const FIELD_CLASS =
  "h-11 w-full rounded-[var(--radius)] border-2 border-line bg-bg-2 px-3.5 text-[15px] text-ink " +
  "placeholder:text-ink-faint outline-none transition-[border-color,box-shadow] duration-150 " +
  "focus-visible:border-wiki focus-visible:shadow-[0_0_0_3px_oklch(0.78_0.16_220_/_0.25)] " +
  "motion-reduce:transition-none"

export function LoginView({
  corpId,
  eventCode,
  isPending,
  showInvalidCreds,
  onCorpIdChange,
  onEventCodeChange,
  onSubmit,
}: LoginViewProps) {
  const errorId = "login-error"

  return (
    <main className="flex min-h-dvh flex-col items-center justify-center gap-7 px-5 py-10">
      <Wordmark />

      {/* The lit cabinet: a single framed panel, the right place for a card. */}
      <section className="w-full max-w-[420px] rounded-[var(--radius)] border-2 border-line bg-panel shadow-[var(--shadow-cabinet)]">
        {/* Lit marquee strip — the one sanctioned glow. */}
        <div
          className="h-2 rounded-t-[2px] bg-wiki"
          style={{ boxShadow: "0 0 18px var(--wiki)" }}
        />

        <div className="p-7">
          <h1 className="mt-4 font-pixel text-[13px] leading-[1.5] text-ink">
            PLAYER LOGIN
          </h1>
          <p className="mt-3 max-w-[44ch] text-[15px] leading-relaxed text-ink-dim">
            Enter your corp ID and the event code from your facilitator to take
            the floor.
          </p>

          <form
            onSubmit={onSubmit}
            className="mt-6 flex flex-col gap-5"
            noValidate
          >
            <div className="flex flex-col gap-2">
              <label
                htmlFor="corp_id"
                className="text-[10px] font-bold tracking-[1px] text-ink-faint uppercase"
              >
                Corp ID
              </label>
              <input
                id="corp_id"
                name="corp_id"
                autoComplete="username"
                autoCapitalize="none"
                spellCheck={false}
                placeholder="e.g. ap10000"
                value={corpId}
                onChange={(e) => onCorpIdChange(e.target.value)}
                aria-invalid={showInvalidCreds}
                aria-describedby={showInvalidCreds ? errorId : undefined}
                className={FIELD_CLASS}
              />
            </div>

            <div className="flex flex-col gap-2">
              <label
                htmlFor="event_code"
                className="text-[10px] font-bold tracking-[1px] text-ink-faint uppercase"
              >
                Event code
              </label>
              <input
                id="event_code"
                name="event_code"
                autoComplete="off"
                autoCapitalize="characters"
                spellCheck={false}
                placeholder="Called out by your facilitator"
                value={eventCode}
                onChange={(e) => onEventCodeChange(e.target.value)}
                aria-invalid={showInvalidCreds}
                aria-describedby={showInvalidCreds ? errorId : undefined}
                className={FIELD_CLASS}
              />
            </div>

            {showInvalidCreds ? (
              <p
                id={errorId}
                role="alert"
                className="flex animate-picture-input-shake items-center gap-2.5 rounded-[var(--radius)] border-2 border-cross bg-cross/12 px-3.5 py-3 text-[14px] font-medium text-ink motion-reduce:animate-none"
              >
                <TriangleAlert
                  aria-hidden
                  className="size-4 shrink-0 text-cross"
                />
                Invalid corp ID or event code
              </p>
            ) : null}

            <button
              type="submit"
              disabled={isPending}
              className={
                "group mt-1 inline-flex h-12 w-full items-center justify-center gap-2 " +
                "rounded-[var(--radius)] border-2 border-wiki bg-wiki text-[13px] font-extrabold " +
                "tracking-[1.5px] text-bg uppercase shadow-[var(--shadow-cabinet-sm)] " +
                "transition-[transform,box-shadow] duration-150 ease-[var(--ease-arcade)] " +
                "hover:-translate-x-0.5 hover:-translate-y-0.5 hover:shadow-[var(--shadow-cabinet)] " +
                "active:translate-x-[2px] active:translate-y-[2px] active:shadow-none " +
                "focus-visible:ring-2 focus-visible:ring-wiki focus-visible:outline-none " +
                "focus-visible:ring-offset-2 focus-visible:ring-offset-panel " +
                "disabled:pointer-events-none disabled:opacity-60 " +
                "motion-reduce:transition-none motion-reduce:hover:translate-x-0 motion-reduce:hover:translate-y-0"
              }
            >
              {isPending ? (
                <>
                  <Loader2
                    aria-hidden
                    className="size-4 animate-spin motion-reduce:animate-none"
                  />
                  Signing in…
                </>
              ) : (
                <>
                  <ChevronRight aria-hidden className="size-4" />
                  Sign in
                </>
              )}
            </button>
          </form>
        </div>
      </section>
    </main>
  )
}
