import { type NextRequest, NextResponse } from "next/server";

export const config = {
  // Exclude public game assets so next/image can fetch sources without auth cookies
  // (e.g. /games/picture/*, /images/four-pics/*).
  matcher: ["/((?!api|_next/static|_next/image|favicon\\.ico|games|images).*)"],
};

export function proxy(request: NextRequest) {
  const pathname = request.nextUrl.pathname;
  const token = request.cookies.get("token")?.value;

  if (pathname === "/login") {
    if (token) {
      return NextResponse.redirect(new URL("/lobby", request.url));
    }
    return NextResponse.next();
  }

  if (!token) {
    return NextResponse.redirect(new URL("/login", request.url));
  }
  return NextResponse.next();
}
