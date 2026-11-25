// /llms.txt: a plain-text summary of this section for AI assistants (llmstxt.org). Lists every published answer.
import { api } from "@/lib/api";
import { SECTION_LEDE, SECTION_NAME, SITE_NAME, SITE_URL } from "@/lib/site";

export async function GET() {
  const pages = await api<{ slug: string; title: string; meta_description: string }[]>("/pages").catch(() => []);
  const text = [
    `# ${SITE_NAME}: ${SECTION_NAME}`,
    "",
    `> ${SECTION_LEDE} Each answer is drafted by AI from cited, dated sources and approved by a named expert. Owned by Vyohm AI Private Limited.`,
    "",
    "## Answers",
    ...(pages.length ? pages.map((p) => `- [${p.title}](${SITE_URL}/q/${p.slug}): ${p.meta_description}`) : ["- None published yet."]),
    "",
    "## About",
    `- [How this section works](${SITE_URL}/about): who builds it, who reviews it, how AI is used`,
    "",
  ].join("\n");
  return new Response(text, { headers: { "Content-Type": "text/plain; charset=utf-8" } });
}
