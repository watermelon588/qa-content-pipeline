"use server";
// The expert's two buttons: "Open the answer" (their personal reviewer code, asked once) and "Send my decision".
// Anyone can call a Server Action, so neither decides anything here: both forward the link's code and the reviewer
// code to the API, which checks that the link is unused and that the code belongs to the expert it was sent to.

import { cookies } from "next/headers";
import { refresh } from "next/cache";
import { api, ApiError, type Result } from "@/lib/api";
import { cleanCode, EXPERT_COOKIE, isCode } from "./code";

const DAYS_30 = 60 * 60 * 24 * 30;

export async function enterCode(_: Result, form: FormData): Promise<Result> {
  const token = String(form.get("token") || "");
  const code = cleanCode(String(form.get("code") || ""));
  if (!isCode(token)) return { ok: false, message: "This review link is not valid." };
  if (!code) return { ok: false, message: "Type the reviewer code we sent you." };
  try {
    // Ask the API with this code. Only if it opens the answer do we remember it.
    await api(`/review/${token}`, { headers: { "X-Expert-Code": code } });
  } catch (e) {
    const wrong = e instanceof ApiError && e.status === 401;
    return { ok: false, message: wrong ? "That code is not right. Check it and try again." : e instanceof Error ? e.message : String(e) };
  }
  (await cookies()).set(EXPERT_COOKIE, code, {
    httpOnly: true, // JavaScript on the page can't read it
    secure: process.env.NODE_ENV === "production", // https only once deployed
    sameSite: "lax", // other sites can't make the browser send it with a form post
    maxAge: DAYS_30, // the next review link opens without asking again
    path: "/review", // sent only to review pages, nowhere else on the site
  });
  refresh(); // re-render the page, which now shows the answer
  return { ok: true, message: "Code accepted." };
}

export async function decideReview(_: Result, form: FormData): Promise<Result> {
  const token = String(form.get("token") || "");
  if (!isCode(token)) return { ok: false, message: "This review link is not valid." };
  const code = (await cookies()).get(EXPERT_COOKIE)?.value || "";
  const field = (k: string) => String(form.get(k) || "");
  try {
    await api(`/review/${token}`, {
      method: "POST",
      headers: { "X-Expert-Code": code },
      body: {
        decision: field("decision"), body: field("body"), title: field("title"), meta_description: field("meta_description"),
        alt_text: field("alt_text"), advice: field("advice"), note: field("note"),
      },
    });
  } catch (e) {
    return { ok: false, message: e instanceof Error ? e.message : String(e) };
  }
  refresh(); // re-render the page, which now shows the thank-you message
  return { ok: true, message: "Thank you. Your decision is saved." };
}

export async function forgetCode() {
  // "Not you?" on a shared computer: drop the saved code so the next person is asked for theirs.
  (await cookies()).delete({ name: EXPERT_COOKIE, path: "/review" });
  refresh();
}
