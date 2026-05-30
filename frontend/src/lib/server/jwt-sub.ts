/** Extract JWT `sub` from an HS256 token without verifying the signature.
 *
 * Used only on the server where the httpOnly session cookie is readable, so the
 * client can highlight the current player without exposing the JWT to browser JS.
 */
export function decodeJwtSub(token: string): string | null {
  try {
    const parts = token.split(".")
    if (parts.length !== 3) {
      return null
    }
    const payloadSegment = parts[1]
    if (!payloadSegment) {
      return null
    }
    const payloadJson = Buffer.from(payloadSegment, "base64url").toString(
      "utf8"
    )
    const payload = JSON.parse(payloadJson) as { sub?: unknown }
    return typeof payload.sub === "string" ? payload.sub : null
  } catch {
    return null
  }
}

export type JwtPlayer = {
  corpId: string | null
  displayName: string | null
}

/** Extract the player identity (`sub` + `display_name`) from an HS256 token.
 *
 * Same server-only, no-verify contract as {@link decodeJwtSub}: used where the
 * httpOnly cookie is readable so the AppBar can show who is playing without
 * leaking the JWT to browser JS.
 */
export function decodeJwtPlayer(token: string): JwtPlayer {
  try {
    const payloadSegment = token.split(".")[1]
    if (!payloadSegment) {
      return { corpId: null, displayName: null }
    }
    const payloadJson = Buffer.from(payloadSegment, "base64url").toString(
      "utf8"
    )
    const payload = JSON.parse(payloadJson) as {
      sub?: unknown
      display_name?: unknown
    }
    return {
      corpId: typeof payload.sub === "string" ? payload.sub : null,
      displayName:
        typeof payload.display_name === "string" ? payload.display_name : null,
    }
  } catch {
    return { corpId: null, displayName: null }
  }
}
