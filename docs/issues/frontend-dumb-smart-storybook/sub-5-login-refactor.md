# Sub-5: Login refactor

**Status:** done  
**Blocked by:** Sub-4 (mirror Rapid Fire + Wiki conventions)  
**Blocks:** None

## Parent

`docs/issues/frontend-dumb-smart-storybook/parent.md`

## ⚠️ Mirror Sub-3 and Sub-4 conventions

Before writing code, read the files produced by Sub-3 (`app/(games)/rapid-fire/_components/`) and Sub-4 (`app/(games)/wiki/_components/`). Mirror file naming, story file shape, callback prop naming, and the `*Client` / `*View` split. Login is simpler than those slices (no discriminated-union `viewState` is needed — see below) but the surface-level conventions must match.

## What to build

The current `login/page.tsx` is itself a `"use client"` component. Promote it to a server component that renders a new `<LoginClient />`. Extract a dumb `LoginView` that receives all state and callbacks as plain props.

### Server page (`app/(auth)/login/page.tsx`)

Becomes a server component. Renders `<LoginClient />`. No data fetching, no auth logic in the page itself — it is just a shell.

### Smart layer (`_components/LoginClient.tsx`)

Owns:
- `useLoginMutation` from `services/auth/hooks`
- `useRouter` from `next/navigation`
- Local form state: `corpId`, `eventCode`
- Submit handler that calls `login.mutate(...)` and on success `router.replace('/lobby')`
- Derives `showInvalidCreds` from `login.isError` + `LoginApiError` status (verbatim from existing code)
- Renders `<LoginView ... />`

### Dumb view (`_components/LoginView.tsx`)

Props:
```ts
{
  corpId: string
  eventCode: string
  isPending: boolean
  showInvalidCreds: boolean
  onCorpIdChange: (value: string) => void
  onEventCodeChange: (value: string) => void
  onSubmit: (e: React.FormEvent) => void
}
```

Pure render — zero hooks. Owns the page layout wrapper, the heading/subheading, the form, the two labelled inputs, the error message, and the submit button. All Tailwind class strings move verbatim.

### No `viewState` discriminated union here

Login has no meaningful state-machine; the three visual variants (`Idle`, `Pending`, `InvalidCredentials`) are expressible directly via the `isPending` and `showInvalidCreds` boolean props. Do not introduce a `viewState` union just for symmetry — keep it simple. (This is the one place where Login intentionally deviates from the discriminated-union pattern Sub-3 establishes; the simpler shape is justified by the lack of internal states.)

### Stories

`LoginView.stories.tsx` with three stories:
- `Idle` — empty fields, `isPending=false`, `showInvalidCreds=false`
- `Pending` — fields filled, `isPending=true`
- `InvalidCredentials` — fields filled, `showInvalidCreds=true`

Use `fn()` for all callbacks. Each story should be interactable via Storybook controls so the values can be tweaked live.

### What does not change

- `services/auth/*` and `lib/api/auth.ts` — zero edits.
- `app/api/auth/login/route.ts` and its tests — zero edits.
- All Tailwind class strings — move verbatim.

### Existing test handling

`__tests__/login-page.test.tsx` exercises the current `"use client"` login page. It must continue passing. The test imports the page module and renders it; after the refactor it should either:
- Continue importing `app/(auth)/login/page.tsx` (now a server component) — likely won't work directly, so:
- Switch its import to `app/(auth)/login/_components/LoginClient.tsx` and assert the same behaviours through the client component. Update only imports and rendering setup; do not change behavioural assertions (form submit, success redirect, error message presence).

## Acceptance criteria

- [x] `app/(auth)/login/page.tsx` is a server component with no `"use client"` directive, no hooks, and no JSX beyond `<LoginClient />`
- [x] `LoginClient.tsx` owns `useLoginMutation`, `useRouter`, form state, and submit handler
- [x] `LoginView.tsx` is a pure render with the props shape above and zero hooks
- [x] `LoginView.stories.tsx` ships three stories: `Idle`, `Pending`, `InvalidCredentials`
- [x] `__tests__/login-page.test.tsx` passes with import/setup-only edits — behavioural assertions unchanged
- [ ] Manual smoke test (`bun dev`): login with valid credentials redirects to `/lobby`; invalid credentials shows the error message; pending state disables the submit button and shows "Signing in…"
- [x] `bun run lint`, `bun run typecheck`, `bun run test` all pass
