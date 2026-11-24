// The admin login cookie. Its value is "<expiry in ms>.<signature>". The signature is an HMAC (a keyed fingerprint:
// only someone who knows the key can produce a matching one) of the expiry, so nobody can forge a cookie or
// stretch its expiry. The key is the admin user and password, so changing the password logs everyone out.
// Runs in proxy.ts and in Server Actions, so it uses only Web Crypto and no Node-only imports.
// ponytail: one shared admin, no per-session list on the server, so "sign out" removes this browser's cookie only.

export const COOKIE = "atlas_admin";
export const MAX_AGE = 7 * 24 * 60 * 60; // seconds: stay signed in for a week

export const sessionKey = () => `${process.env.ADMIN_USER || "admin"}:${process.env.ADMIN_PASSWORD}`;

async function sign(text: string, key: string) {
  const enc = new TextEncoder();
  const k = await crypto.subtle.importKey("raw", enc.encode(key), { name: "HMAC", hash: "SHA-256" }, false, ["sign"]);
  const sig = new Uint8Array(await crypto.subtle.sign("HMAC", k, enc.encode(text)));
  return Array.from(sig, (b) => b.toString(16).padStart(2, "0")).join("");
}

/** Compares every character even after a mismatch, so the time taken doesn't hint at how much was right. */
export function sameText(a: string, b: string) {
  let diff = a.length ^ b.length;
  for (let i = 0; i < Math.max(a.length, b.length); i++) diff |= (a.charCodeAt(i) || 0) ^ (b.charCodeAt(i) || 0);
  return diff === 0;
}

export async function makeToken(key: string, now = Date.now()) {
  const expires = String(now + MAX_AGE * 1000);
  return `${expires}.${await sign(expires, key)}`;
}

/** True only for a cookie we signed with this key that hasn't expired. */
export async function checkToken(token: string | undefined, key: string, now = Date.now()) {
  const [expires, signature = ""] = (token || "").split(".");
  if (!expires || !(Number(expires) > now)) return false; // empty, not a number, or past its expiry
  return sameText(signature, await sign(expires, key));
}
