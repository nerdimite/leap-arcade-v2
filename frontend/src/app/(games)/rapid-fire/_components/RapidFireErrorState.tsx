/** Recoverable error surface for Rapid Fire. */

import { Button } from "@/components/ui/button";

export function RapidFireErrorState(props: { message?: string; onBackToLobby: () => void }) {
  return (
    <>
      <h1 className="mb-2 font-semibold text-lg">Rapid Fire</h1>
      <p className="mb-4 text-muted-foreground">{props.message ?? "Something went wrong."}</p>
      <Button type="button" variant="outline" onClick={props.onBackToLobby}>
        Back to Lobby
      </Button>
    </>
  );
}
