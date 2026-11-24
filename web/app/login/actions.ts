"use server";
// Sign in and sign out for the admin desk. A correct login sets a signed cookie (see lib/session.ts); proxy.ts
// then lets /admin through. Docs: node_modules/next/dist/docs/01-app/03-api-reference/04-functions/cookies.md

import { cookies } from "next/headers";
import { redirect } from "next/navigation";
import type { Result } from "@/lib/api";
import { COOKIE, makeToken, MAX_AGE, sameText, sessionKey } from "@/lib/session";

export async function login(_: Result, form: FormData): Promise<Result> {
  if (!process.env.ADMIN_PASSWORD) return { ok: false, message: "The admin is switched off: ADMIN_PASSWORD is not set." };
  const given = `${String(form.get("user") || "")}:${String(form.get("password") || "")}`;
  if (!sameText(given, sessionKey())) {
    // A one-second wait makes guessing passwords slow. ponytail: it is not a real rate limit (serverless has no
    // memory between requests); add Upstash if the site ever gets attacked.
    await new Promise((done) => setTimeout(done, 1000));
    return { ok: false, message: "Wrong username or password." };
  }
  (await cookies()).set(COOKIE, await makeToken(sessionKey()), {
    httpOnly: true, // JavaScript on the page can't read it
    secure: process.env.NODE_ENV === "production", // https only once deployed
    sameSite: "lax", // other sites can't make the browser send it with a form post
    maxAge: MAX_AGE,
    path: "/",
  });
  redirect("/admin"); // always the desk: never a page taken from the address, so no open redirect
}

export async function logout() {
  (await cookies()).delete(COOKIE);
  redirect("/login");
}
