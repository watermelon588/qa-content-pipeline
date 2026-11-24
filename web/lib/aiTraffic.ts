// Level 6: is this request an AI crawler, or a person sent here by an AI assistant? proxy.ts asks on every page
// request and reports the matches to the API, which keeps only a count per page per day (no IP, no user agent).

// Crawlers name themselves in the User-Agent header. Sources: each company's crawler docs (OpenAI, Anthropic,
// Perplexity, ByteDance, Common Crawl, Meta, Amazon).
const CRAWLERS = [
  "GPTBot", "OAI-SearchBot", "ChatGPT-User", "ClaudeBot", "Claude-User", "Claude-SearchBot",
  "PerplexityBot", "Perplexity-User", "Bytespider", "CCBot", "Meta-ExternalAgent", "Amazonbot",
];

// A visitor's browser sends the page they came from (Referer). ChatGPT often hides it but adds ?utm_source=chatgpt.com.
const ASSISTANTS: [domain: string, name: string][] = [
  ["chatgpt.com", "ChatGPT"],
  ["chat.openai.com", "ChatGPT"],
  ["perplexity.ai", "Perplexity"],
  ["gemini.google.com", "Gemini"],
  ["copilot.microsoft.com", "Copilot"],
  ["claude.ai", "Claude"],
];

export type AiHit = { kind: "crawler" | "referral"; name: string };

export function classify(userAgent: string, referer: string, utmSource: string): AiHit | null {
  const ua = userAgent.toLowerCase();
  const crawler = CRAWLERS.find((c) => ua.includes(c.toLowerCase()));
  if (crawler) return { kind: "crawler", name: crawler };

  let host = "";
  try {
    host = new URL(referer).hostname;
  } catch {} // no referer, or not a URL
  const from = (d: string) => host === d || host.endsWith(`.${d}`) || utmSource.toLowerCase().includes(d);
  const assistant = ASSISTANTS.find(([d]) => from(d));
  return assistant ? { kind: "referral", name: assistant[1] } : null;
}
