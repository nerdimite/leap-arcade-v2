# Sub-1: Storybook setup + AGENTS.md update + prettier fix

**Status:** done  
**Blocked by:** None — can start immediately  
**Blocks:** Sub-3, Sub-4, Sub-5, Sub-6, Sub-7

## Parent

`docs/issues/frontend-dumb-smart-storybook/parent.md`

## What to build

Three configuration deliverables in one slice. None of them touches production components — they prepare the ground for every subsequent refactor.

**1. Storybook installation and configuration**

- Install `@storybook/nextjs-vite` plus addons: `@storybook/addon-a11y`, `@storybook/addon-docs`, `@chromatic-com/storybook`, `@storybook/addon-vitest`. Use `bunx storybook@latest init --type nextjs` as the starting point if it cleanly produces a Vite-based config; otherwise install manually and configure.
- Add `.storybook/main.ts` with: `framework: '@storybook/nextjs-vite'`, `stories: ['../src/**/*.stories.@(ts|tsx)']`, `staticDirs: ['../public']`, the four addons above.
- Add `.storybook/preview.tsx` with two decorators wrapping every story:
  - `ThemeProvider` (from `src/components/theme-provider.tsx`)
  - A fresh `QueryClientProvider` with a per-story `QueryClient` instance (defensive — dumb views don't call hooks but a composed story might)
- Import `src/app/globals.css` in `preview.tsx` so Tailwind classes resolve.
- Add `bun run storybook` and `bun run build-storybook` scripts to `package.json`.
- Add one smoke-test story (anywhere, e.g. `src/components/ui/button.stories.tsx`) to confirm Storybook boots and renders.
- Do not configure Chromatic baselines or CI integration — out of scope.

**2. `frontend/AGENTS.md` update**

Append to the existing AGENTS.md two new rules in the "Dos and Don'ts" section:

- Every route with non-trivial UI splits into `*Client.tsx` (smart: hooks, mutations, effects, navigation guard, reducer) and `*View.tsx` (dumb: receives `viewState` + callback props, switches on `viewState.status`, renders leaf components). Leaf components have no hooks; the only sanctioned exception is `WikiArticlePane`'s DOM click delegation `useEffect` (see ADR-0005).
- Stories live co-located as `*.stories.tsx`; meta omits `title` (path-derived sidebar); one `Default` story per leaf unless variants warrant more; one story per status for every `*View`.

Also add a "Reference Docs" entry pointing at `docs/adr/0005-frontend-dumb-smart-split-and-storybook.md`.

**3. `.prettierrc` `tailwindStylesheet` fix**

The current `tailwindStylesheet` value is `app/globals.css`. The file actually lives at `src/app/globals.css`. Update the path so Tailwind class sorting continues to work for the many files touched by subsequent slices.

## Acceptance criteria

- [x] `bun run storybook` boots a dev server with no errors
- [x] `bun run build-storybook` produces a static build with no errors
- [x] The smoke-test story renders in the Storybook UI with the path-derived sidebar entry
- [x] `preview.tsx` wraps every story in `ThemeProvider` and `QueryClientProvider`
- [x] `src/app/globals.css` is imported in `preview.tsx`; Tailwind classes resolve in stories
- [x] `frontend/AGENTS.md` contains the two new Dos and Don'ts entries and the new Reference Docs row
- [x] `.prettierrc` `tailwindStylesheet` points at `src/app/globals.css`
- [x] `bun run lint`, `bun run typecheck`, and `bun run test` all pass
- [x] No production component files (anything under `src/app/`, `src/components/`, `src/services/`, `src/lib/`) are edited beyond the `theme-provider.tsx` import surfaced by Storybook
