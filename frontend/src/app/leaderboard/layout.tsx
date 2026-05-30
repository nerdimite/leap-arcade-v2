import { cookies } from "next/headers";
import type { ReactNode } from "react";

import { AppBar } from "@/components/chrome/AppBar";
import { decodeJwtPlayer } from "@/lib/server/jwt-sub";

export default async function LeaderboardLayout({ children }: { children: ReactNode }) {
  const token = (await cookies()).get("token")?.value ?? "";
  const { corpId, displayName } = token
    ? decodeJwtPlayer(token)
    : { corpId: null, displayName: null };

  return (
    <>
      <AppBar corpId={corpId} displayName={displayName} />
      {children}
    </>
  );
}
