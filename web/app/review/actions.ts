"use server";
// The expert's "send my decision" button. Anyone can call a Server Action, so the link's code is the only
// permission, exactly as when the API is called directly. The API checks it, and that it's unused and unexpired.

import { refresh } from "next/cache";
import { api, type Result } from "@/lib/api";
import { isCode } from "./code";

export async function decideReview(_: Result, form: FormData): Promise<Result> {
  const token = String(form.get("token") || "");
  if (!isCode(token)) return { ok: false, message: "This review link is not valid." };
  const field = (k: string) => String(form.get(k) || "");
  try {
    await api(`/review/${token}`, {
      method: "POST",
      body: { decision: field("decision"), body: field("body"), advice: field("advice"), note: field("note") },
    });
  } catch (e) {
    return { ok: false, message: e instanceof Error ? e.message : String(e) };
  }
  refresh(); // re-render the page, which now shows the thank-you message
  return { ok: true, message: "Thank you. Your decision is saved." };
}
