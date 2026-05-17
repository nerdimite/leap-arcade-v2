/** Dumb login screen: corp ID + event code, invalid-credentials alert, submit. */

import type { FormEvent } from "react";

import { Button } from "@/components/ui/button";

export type LoginViewProps = {
  corpId: string;
  eventCode: string;
  isPending: boolean;
  showInvalidCreds: boolean;
  onCorpIdChange: (value: string) => void;
  onEventCodeChange: (value: string) => void;
  onSubmit: (e: FormEvent) => void;
};

export function LoginView({
  corpId,
  eventCode,
  isPending,
  showInvalidCreds,
  onCorpIdChange,
  onEventCodeChange,
  onSubmit,
}: LoginViewProps) {
  return (
    <div className="flex min-h-dvh flex-col items-center justify-center gap-6 p-6">
      <div className="w-full max-w-sm space-y-2 text-center">
        <h1 className="text-2xl font-semibold tracking-tight">Sign in to LEAP</h1>
        <p className="text-muted-foreground text-sm">Use your corp ID and the event code provided by your facilitator.</p>
      </div>
      <form onSubmit={onSubmit} className="flex w-full max-w-sm flex-col gap-4">
        <div className="space-y-2 text-left">
          <label className="text-sm font-medium" htmlFor="corp_id">
            Corp ID
          </label>
          <input
            id="corp_id"
            name="corp_id"
            autoComplete="username"
            value={corpId}
            onChange={(e) => onCorpIdChange(e.target.value)}
            className="border-input bg-background focus-visible:ring-ring h-9 w-full rounded-md border px-3 text-sm shadow-xs outline-none focus-visible:ring-2"
          />
        </div>
        <div className="space-y-2 text-left">
          <label className="text-sm font-medium" htmlFor="event_code">
            Event code
          </label>
          <input
            id="event_code"
            name="event_code"
            autoComplete="off"
            value={eventCode}
            onChange={(e) => onEventCodeChange(e.target.value)}
            className="border-input bg-background focus-visible:ring-ring h-9 w-full rounded-md border px-3 text-sm shadow-xs outline-none focus-visible:ring-2"
          />
        </div>
        {showInvalidCreds ? (
          <p className="text-destructive text-sm" role="alert">
            Invalid corp ID or event code
          </p>
        ) : null}
        <Button type="submit" disabled={isPending}>
          {isPending ? "Signing in…" : "Sign in"}
        </Button>
      </form>
    </div>
  );
}
