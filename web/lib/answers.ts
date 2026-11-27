// What the home page's answer list shows and searches. Plain functions, so they can be tested without a browser
// (run from web/:  node --test lib/answers.test.mjs).

/** One answer on the home page. `trust` is empty if the answer's details couldn't be loaded. */
export type AnswerCard = { slug: string; title: string; preview: string; trust: string; providers: string[] };

/** The first ordinary paragraph of an answer: no headings, lists, tables, [n] fact markers or ** bold marks. */
export function previewOf(body: string): string {
  const paragraph = body
    .replace(/\r/g, "")
    .split(/\n\s*\n/)
    .map((block) => block.trim())
    .find((block) => block && !/^(#|\||[-*]\s)/.test(block));
  return (paragraph ?? "")
    .replace(/\s*\[\d+\]/g, "")
    .replace(/\*\*/g, "")
    .replace(/\s+/g, " ");
}

/** True when every typed word appears somewhere in the question, the preview or a provider's name. */
export function matches(card: AnswerCard, query: string): boolean {
  const text = [card.title, card.preview, ...card.providers].join(" ").toLowerCase();
  return query.toLowerCase().split(/\s+/).every((word) => text.includes(word));
}
