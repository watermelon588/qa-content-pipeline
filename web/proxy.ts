import { NextResponse, type NextFetchEvent, type NextRequest } from "next/server";
import { classify } from "@/lib/aiTraffic";
import { api } from "@/lib/api";

// Two jobs, before any page renders:
// 1. Public pages: count visits from AI crawlers and from AI assistants (Level 6), then let the page load as normal.
// 2. Password for everything under /admin, using the browser's own login box (HTTP Basic Auth).
// Runs before the page renders, so it also guards the admin buttons (server actions POST to the same URL).
// Docs: node_modules/next/dist/docs/01-app/03-api-reference/03-file-conventions/proxy.md
// ponytail: one shared password, no logout button. Close the browser to log out. Fine for one owner.

export function proxy(request: NextRequest, event: NextFetchEvent) {
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
  const expected = `${process.env.ADMIN_USER || "admin"}:${password}`;
  const [scheme, encoded] = (request.headers.get("authorization") || "").split(" ");
  if (scheme === "Basic" && encoded && sameText(decode(encoded), expected)) {
    return NextResponse.next();
  }
  return new NextResponse("Login required", {
    status: 401,
    headers: { "WWW-Authenticate": 'Basic realm="AI Atlas admin", charset="UTF-8"' },
  });
}

function decode(base64: string) {
  try {
    return new TextDecoder().decode(Uint8Array.from(atob(base64), (c) => c.charCodeAt(0)));
  } catch {
    return ""; // not valid base64: treat as a wrong password
  }
}

// Compares every character even after a mismatch, so the time taken doesn't hint at how much was right.
function sameText(a: string, b: string) {
  let diff = a.length ^ b.length;
  for (let i = 0; i < Math.max(a.length, b.length); i++) diff |= (a.charCodeAt(i) || 0) ^ (b.charCodeAt(i) || 0);
  return diff === 0;
}

// Every request except Next's own files and the two images (they'd only add noise to the counts).
export const config = { matcher: ["/((?!_next/|favicon.svg|plate-gpu.webp).*)"] };
