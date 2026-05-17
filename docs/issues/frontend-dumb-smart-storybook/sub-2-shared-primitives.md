# Sub-2: Shared primitives — `formatMs` + `TimerBar`

**Status:** done  
**Blocked by:** None — can start immediately  
**Blocks:** Sub-3 (Rapid Fire needs `TimerBar`), Sub-4 (Wiki needs `formatMs`)

## Parent

`docs/issues/frontend-dumb-smart-storybook/parent.md`

## What to build

Two small, well-tested primitives that subsequent slices will consume. Neither has runtime consumers yet at the time this slice ships (Rapid Fire and Wiki still inline their copies); the consumer migration happens in their respective refactor slices.

**1. Promote `formatMs(ms: number): string` to `src/lib/utils.ts`**

- The current inline definition lives in `WikiClient`. Move the function (verbatim semantics) into `src/lib/utils.ts` as a named export.
- Behaviour: clamps negative input to `0:00`; formats as `m:ss` with zero-padded seconds; non-integer milliseconds floor correctly via `Math.floor(ms / 1000)`.
- Do not remove the inline copy in `WikiClient` in this slice — Sub-4 (Wiki refactor) handles the migration.
- Add a Vitest unit test file covering: `0` → `0:00`, negative input → `0:00`, `1_000` → `0:01`, `59_999` → `0:59`, `60_000` → `1:00`, `61_500` → `1:01`, `3_599_000` → `59:59`.

**2. Create `TimerBar` in `src/components/game/TimerBar.tsx`**

- Props: `{ percentage: number }` — value from `0` to `100`, representing time remaining (full bar = 100%, empty = 0%). Clamp out-of-range values in the component.
- Render: matches the existing Rapid Fire timer treatment exactly — `h-2 overflow-hidden rounded-full bg-muted` container with an inner `h-full rounded-full bg-primary transition-[width] duration-75 ease-linear` bar whose `style={{ width: '<pct>%' }}`. ARIA: `role="progressbar"`, `aria-valuemin={0}`, `aria-valuemax={100}`, `aria-valuenow={Math.round(percentage)}`, `aria-label="Time remaining"`.
- No hooks, no internal state. Pure render.
- Add a `TimerBar.stories.tsx` co-located file with three stories: `Default` (60%), `Low` (15%), `Full` (100%). Meta omits `title` per convention.
- Do not wire `TimerBar` into `RapidFireClient` in this slice — Sub-3 handles the migration.

## Acceptance criteria

- [x] `formatMs` exported from `src/lib/utils.ts`
- [x] `src/lib/utils.test.ts` covers the seven cases listed above and passes
- [x] `TimerBar` exported from `src/components/game/TimerBar.tsx` with the props shape above
- [x] `TimerBar` clamps `percentage` to `[0, 100]` before rendering
- [x] `TimerBar.stories.tsx` renders three stories in Storybook (assuming Sub-1 has landed; if not, the stories are inert files that cause no harm)
- [x] No edits to `WikiClient` or `RapidFireClient` — consumer migration is deferred to Sub-3/Sub-4
- [x] `bun run lint`, `bun run typecheck`, `bun run test` all pass
