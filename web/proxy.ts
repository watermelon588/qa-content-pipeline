import { NextResponse, type NextFetchEvent, type NextRequest } from "next/server";
import { classify } from "@/lib/aiTraffic";
import { api } from "@/lib/api";
import { checkToken, COOKIE, sessionKey } from "@/lib/session";

// Two jobs, before any page renders:
// 1. Public pages: count visits from AI crawlers and from AI assistants (Level 6), then let the page load as normal.
// 2. Everything under /admin needs the signed login cookie from /login (lib/session.ts); without it you are sent to /login.
// Runs before the page renders, so it also guards the admin buttons (server actions POST to the same URL).
// Docs: node_modules/next/dist/docs/01-app/03-api-reference/03-file-conventions/proxy.md
// ponytail: one shared admin login. Fine for one owner.

export async function proxy(request: NextRequest, event: NextFetchEvent) {
  const { pathname, searchParams } = request.nextUrl;
  if (!pathname.startsWith("/admin")) {
    const hit = classify(request.headers.get("user-agent") || "", request.headers.get("referer") || "", searchParams.get("utm_source") || "");
    // waitUntil: the page is sent straight away; the report finishes in the background. A failed report is
    // dropped rather than slowing or breaking the page.
    if (hit) event.waitUntil(api("/hits", { method: "POST", body: { ...hit, path: pathname.slice(0, 200) } }).catch(() => {}));
    return NextResponse.next();
  }

  const password = process.env.ADMIN_PASSWORD;
  if (!password) {
    // Safe default: with no password set, the admin is closed rather than open to everyone.
    return new NextResponse("Admin is switched off. Set ADMIN_PASSWORD in web/.env.local.", { status: 503 });
  }
  if (await checkToken(request.cookies.get(COOKIE)?.value, sessionKey())) return NextResponse.next();
  return NextResponse.redirect(new URL("/login", request.url));
}

// Every request except Next's own files and the two images (they'd only add noise to the counts).
export const config = { matcher: ["/((?!_next/|favicon.svg|plate-gpu.webp).*)"] };
