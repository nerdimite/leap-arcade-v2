import { type NextRequest, NextResponse } from "next/server";

export const config = {
  // Exclude public game assets under /games/* (e.g. picture puzzle images in public/games/picture/).
  matcher: ["/((?!api|_next/static|_next/image|favicon\\.ico|games).*)"],
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
