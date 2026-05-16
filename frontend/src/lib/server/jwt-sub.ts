/** Extract JWT `sub` from an HS256 token without verifying the signature.
 *
 * Used only on the server where the httpOnly session cookie is readable, so the
 * client can highlight the current player without exposing the JWT to browser JS.
 */
export function decodeJwtSub(token: string): string | null {
  try {
    const parts = token.split(".");
    if (parts.length !== 3) {
      return null;
    }
    const payloadSegment = parts[1];
    if (!payloadSegment) {
      return null;
    }
    const payloadJson = Buffer.from(payloadSegment, "base64url").toString("utf8");
    const payload = JSON.parse(payloadJson) as { sub?: unknown };
    return typeof payload.sub === "string" ? payload.sub : null;
  } catch {
    return null;
  }
}
